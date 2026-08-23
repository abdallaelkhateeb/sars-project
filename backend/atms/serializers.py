# backend/atms/serializers.py
from rest_framework import serializers
from django.utils import timezone

from .models import ATM, Service, ATMService, HeartbeatLog


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class ServiceSerializer(serializers.ModelSerializer):
    """
    Backs GET /services.
    Contract fields: serviceId, name
    """
    serviceId = serializers.CharField(source="service_id")

    class Meta:
        model = Service
        fields = ["serviceId", "name"]


# ---------------------------------------------------------------------------
# HeartbeatLog (nested, read-only — used inside ATMDetailSerializer)
# ---------------------------------------------------------------------------

class HeartbeatLogSerializer(serializers.ModelSerializer):
    """
    Backs recentHeartbeats[] on GET /atms/{atmId}.
    Contract fields: status, cashStatus, receivedAt
    """
    cashStatus = serializers.CharField(source="cash_status")
    receivedAt = serializers.DateTimeField(source="received_at")

    class Meta:
        model = HeartbeatLog
        fields = ["status", "cashStatus", "receivedAt"]


# ---------------------------------------------------------------------------
# ATM — list / detail (read)
# ---------------------------------------------------------------------------
#
# NOTE: current_cash_balance is intentionally NOT exposed here.
# The API contract never returns the exact balance on GET /atms or
# GET /atms/{atmId} — only /routing/alternatives echoes it back as
# availableCashBalance, and only when requestedAmount was sent. Don't
# add current_cash_balance to these serializers without checking with
# سارة / the contract first — it's a deliberate omission, not a gap.

class ATMListSerializer(serializers.ModelSerializer):
    """
    Backs the data[] array of GET /atms.
    Contract fields: atmId, branchName, status, cashStatus, services,
                      latitude, longitude, lastHeartbeatAt
    """
    atmId = serializers.CharField(source="atm_id")
    branchName = serializers.CharField(source="branch_name")
    cashStatus = serializers.CharField(source="cash_status")
    lastHeartbeatAt = serializers.DateTimeField(source="last_heartbeat_at")
    services = serializers.SerializerMethodField()

    class Meta:
        model = ATM
        fields = [
            "atmId",
            "branchName",
            "status",
            "cashStatus",
            "services",
            "latitude",
            "longitude",
            "lastHeartbeatAt",
        ]

    def get_services(self, obj):
        # obj.get_supported_services() lives on the model (models.py, Task 1)
        return obj.get_supported_services()


class ATMDetailSerializer(ATMListSerializer):
    """
    Backs GET /atms/{atmId}.
    Adds recentHeartbeats[] on top of everything ATMListSerializer exposes.
    """
    recentHeartbeats = serializers.SerializerMethodField()

    class Meta(ATMListSerializer.Meta):
        fields = ATMListSerializer.Meta.fields + ["recentHeartbeats"]

    def get_recentHeartbeats(self, obj):
        # Most recent first (HeartbeatLog.Meta.ordering = ["-received_at"]).
        # Capped at 20 so one ATM's history can't blow up the response —
        # revisit this number with محمد/سارة if the dashboard needs more.
        qs = obj.heartbeats.all()[:20]
        return HeartbeatLogSerializer(qs, many=True).data


# ---------------------------------------------------------------------------
# ATM — create (POST /atms, SUPER_ADMIN only)
# ---------------------------------------------------------------------------

class ATMCreateSerializer(serializers.ModelSerializer):
    """
    Backs POST /atms.
    Contract request fields: atmId, branchName, latitude, longitude, services
    Contract response: created ATM object, same shape as GET /atms/{atmId}
                        -> the view re-serializes with ATMDetailSerializer,
                        this serializer only handles validation + create.
    """
    atmId = serializers.CharField(source="atm_id", max_length=50)
    branchName = serializers.CharField(source="branch_name", max_length=255)
    services = serializers.ListField(
        child=serializers.ChoiceField(choices=Service.SERVICE_CHOICES),
        allow_empty=False,
        write_only=True,
    )

    class Meta:
        model = ATM
        fields = ["atmId", "branchName", "latitude", "longitude", "services"]

    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("longitude must be between -180 and 180.")
        return value

    def validate_atmId(self, value):
        # Explicit check so the view can map this to a clean 409, matching
        # the contract's documented "atmId already exists" error.
        if ATM.objects.filter(atm_id=value).exists():
            raise serializers.ValidationError("atmId already exists.")
        return value

    def create(self, validated_data):
        service_names = validated_data.pop("services")
        atm = ATM.objects.create(**validated_data)
        self._sync_services(atm, service_names)
        return atm

    @staticmethod
    def _sync_services(atm, service_names):
        services = Service.objects.filter(name__in=service_names)
        atm.services.set(services)


# ---------------------------------------------------------------------------
# ATM — update (PATCH /atms/{atmId}, SUPER_ADMIN only)
# ---------------------------------------------------------------------------

class ATMUpdateSerializer(serializers.ModelSerializer):
    """
    Backs PATCH /atms/{atmId}.
    Contract request fields (all optional, partial update): branchName, services
    """
    branchName = serializers.CharField(
        source="branch_name", max_length=255, required=False
    )
    services = serializers.ListField(
        child=serializers.ChoiceField(choices=Service.SERVICE_CHOICES),
        allow_empty=False,
        required=False,
        write_only=True,
    )

    class Meta:
        model = ATM
        fields = ["branchName", "services"]

    def update(self, instance, validated_data):
        service_names = validated_data.pop("services", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if service_names is not None:
            ATMCreateSerializer._sync_services(instance, service_names)
        return instance


# ---------------------------------------------------------------------------
# Heartbeat (POST /atms/{atmId}/heartbeat)
# ---------------------------------------------------------------------------

class HeartbeatSerializer(serializers.Serializer):
    """
    Backs POST /atms/{atmId}/heartbeat.
    Contract request fields: status, cashStatus, cashBalance, services,
                              latitude, longitude, timestamp
    Contract response fields: atmId, received, processedAt

    This is a plain Serializer (not ModelSerializer) because the payload
    shape doesn't map 1:1 onto the ATM model — cashBalance -> current_cash_
    balance, timestamp is client-reported and not persisted as-is (we use
    server time for last_heartbeat_at / HeartbeatLog.received_at so heartbeat
    ordering can't be spoofed by clock drift on the ATM device).
    """
    status = serializers.ChoiceField(choices=ATM.STATUS_CHOICES)
    cashStatus = serializers.ChoiceField(choices=ATM.CASH_STATUS_CHOICES)
    cashBalance = serializers.FloatField(min_value=0)
    services = serializers.ListField(
        child=serializers.ChoiceField(choices=Service.SERVICE_CHOICES),
        allow_empty=True,
    )
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    timestamp = serializers.DateTimeField()

    def save(self, atm):
        """
        Applies the validated heartbeat to `atm`, appends a HeartbeatLog row,
        and returns the log entry. The view (Task 3) is expected to call:

            serializer.is_valid(raise_exception=True)
            log = serializer.save(atm=atm)

        Kept as an explicit `atm` kwarg rather than baked into the serializer
        context, since the view already resolves + 404s on atm_id before
        this runs.
        """
        data = self.validated_data
        now = timezone.now()

        atm.status = data["status"]
        atm.cash_status = data["cashStatus"]
        atm.current_cash_balance = data["cashBalance"]
        atm.latitude = data["latitude"]
        atm.longitude = data["longitude"]
        atm.last_heartbeat_at = now
        atm.save()

        ATMCreateSerializer._sync_services(atm, data["services"])

        return HeartbeatLog.objects.create(
            atm=atm,
            status=data["status"],
            cash_status=data["cashStatus"],
        )
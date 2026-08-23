# backend/atms/views.py
from datetime import timedelta

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.permissions import IsAdmin, IsSuperAdmin
from common.api_key_auth import ApiKeyAuthentication
from common.geo import haversine_km
from common.pagination import StandardResultsSetPagination

from .models import ATM, Service, HeartbeatLog
from .serializers import (
    ATMCreateSerializer,
    ATMDetailSerializer,
    ATMListSerializer,
    ATMUpdateSerializer,
    HeartbeatSerializer,
    ServiceSerializer,
)

# Cash-sufficiency safety margin (docs/api-contract.md §7). Kept server-side,
# never exposed to the client. Move to settings/prod.py with a real value
# before launch — 50.0 is a placeholder so the check has *something* to run
# against; سارة, align this with whatever RoutingEngine.findAlternatives()
# uses so the transaction-attempt pre-filter and the routing endpoint agree.
CASH_BUFFER_AMOUNT = getattr(settings, "ATM_CASH_BUFFER_AMOUNT", 50.0)

# How far back HeartbeatLog rows count toward the network-stats uptime %.
# Not specified in docs/api-contract.md (the endpoint was added post-review,
# see SARS-Final-Folder-Structure.md) — 30 days is my assumption. Flag this
# in a team standup if the dashboard needs a different window.
UPTIME_WINDOW_DAYS = 30


# ---------------------------------------------------------------------------
# 1. POST /atms/{atmId}/transactions/attempt
# ---------------------------------------------------------------------------

class TransactionAttemptView(APIView):
    """
    Contract §5. Kiosk calls this when a customer starts a transaction.
    NFR: must resolve in under 3s (same budget as /routing/alternatives,
    which this may call internally).
    """
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]

    VALID_SERVICES = {c[0] for c in Service.SERVICE_CHOICES}

    def post(self, request, atm_id):
        atm = get_object_or_404(ATM, atm_id=atm_id)

        requested_service = request.data.get("requestedService")
        if requested_service not in self.VALID_SERVICES:
            raise ValidationError(
                {"requestedService": "Must be one of: " + ", ".join(sorted(self.VALID_SERVICES))}
            )

        requested_amount = request.data.get("requestedAmount")
        if requested_service == Service.WITHDRAWAL and requested_amount is None:
            raise ValidationError(
                {"requestedAmount": "Required when requestedService is WITHDRAWAL."}
            )
        if requested_amount is not None:
            try:
                requested_amount = float(requested_amount)
            except (TypeError, ValueError):
                raise ValidationError({"requestedAmount": "Must be a number."})

        reason = self._resolve_reason(atm, requested_service, requested_amount)

        if reason is None:
            return Response({"outcome": "PROCEED", "atmId": atm.atm_id})

        alternatives = self._get_alternatives(atm, requested_service, requested_amount)
        return Response(
            {
                "outcome": "REDIRECT",
                "reason": reason,
                "requestedAmount": requested_amount,
                "alternatives": alternatives,
            }
        )

    @staticmethod
    def _resolve_reason(atm, requested_service, requested_amount):
        """Returns None if the transaction can proceed at this ATM, else
        one of OFFLINE / MAINTENANCE / NO_CASH / INSUFFICIENT_CASH."""
        if atm.status == ATM.OFFLINE:
            return "OFFLINE"
        if atm.status == ATM.MAINTENANCE:
            return "MAINTENANCE"

        # status == ONLINE from here on
        if requested_service == Service.WITHDRAWAL:
            if atm.cash_status == ATM.EMPTY or atm.current_cash_balance <= 0:
                return "NO_CASH"
            if not atm.has_sufficient_cash(requested_amount, CASH_BUFFER_AMOUNT):
                return "INSUFFICIENT_CASH"

        return None

    @staticmethod
    def _get_alternatives(atm, requested_service, requested_amount):
        """
        Delegates to سارة's RoutingEngine (backend/routing/services.py).
        Not implemented yet as of this commit, so this fails closed with
        the contract's documented 503 rather than crashing or silently
        returning an empty list.

        Expected interface (سارة, please confirm/adjust):
            RoutingEngine().find_alternatives(
                origin_atm=atm,
                requested_service=requested_service,
                requested_amount=requested_amount,   # None for non-withdrawal
                buffer_amount=CASH_BUFFER_AMOUNT,
                radius_km=<config default, contract says 5>,
            ) -> list[dict] shaped like /routing/alternatives's alternatives[]
        """
        try:
            from routing.services import RoutingEngine
        except ImportError:
            raise _service_unavailable("Routing engine unavailable.")

        engine = RoutingEngine()
        try:
            return engine.find_alternatives(
                origin_atm=atm,
                requested_service=requested_service,
                requested_amount=requested_amount,
                buffer_amount=CASH_BUFFER_AMOUNT,
            )
        except NotImplementedError:
            raise _service_unavailable("Routing engine unavailable.")


def _service_unavailable(message):
    from rest_framework.exceptions import APIException

    class ServiceUnavailable(APIException):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        default_detail = message

    return ServiceUnavailable(message)


# ---------------------------------------------------------------------------
# 2. POST /atms/{atmId}/heartbeat
# ---------------------------------------------------------------------------

class HeartbeatView(APIView):
    """Contract §6. NFR: must be reflected on the dashboard within 2s."""
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, atm_id):
        atm = get_object_or_404(ATM, atm_id=atm_id)

        serializer = HeartbeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(atm=atm)

        # Task 4 (consumers.py) will push this over WebSocket to
        # DashboardConsumer here — group_send to "dashboard" group.
        # Left as a TODO rather than a silent no-op so it's easy to grep for.
        # TODO(محمد, Task 4): broadcast atm.status.updated / atm.alert here.

        return Response(
            {
                "atmId": atm.atm_id,
                "received": True,
                "processedAt": timezone.now(),
            }
        )


# ---------------------------------------------------------------------------
# 3. GET /atms, POST /atms
# ---------------------------------------------------------------------------

class ATMListCreateView(generics.GenericAPIView):
    """Contract §13 (GET) and §15 (POST)."""
    authentication_classes = [JWTAuthentication]
    pagination_class = StandardResultsSetPagination
    queryset = ATM.objects.all().order_by("atm_id")

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsSuperAdmin()]
        return [IsAdmin()]

    def get_serializer_class(self):
        return ATMCreateSerializer if self.request.method == "POST" else ATMListSerializer

    def get(self, request):
        qs = self.queryset

        status_param = request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        cash_status_param = request.query_params.get("cashStatus")
        if cash_status_param:
            qs = qs.filter(cash_status=cash_status_param)

        service_param = request.query_params.get("service")
        if service_param:
            qs = qs.filter(services__name=service_param)

        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius_km = request.query_params.get("radiusKm")
        if lat and lng:
            lat, lng = float(lat), float(lng)
            radius_km = float(radius_km) if radius_km else 5.0
            # No PostGIS field on ATM (lat/lng are plain floats), so this is
            # a Python-side filter rather than a DB query. Fine at current
            # scale; revisit if the ATM table gets large enough that this
            # becomes a bottleneck (loads all rows first, then filters).
            matching_ids = [
                a.atm_id
                for a in qs
                if haversine_km(lat, lng, a.latitude, a.longitude) <= radius_km
            ]
            qs = qs.filter(atm_id__in=matching_ids)

        qs = qs.distinct()

        page = self.paginate_queryset(qs)
        serializer = ATMListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ATMCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        atm = serializer.save()
        return Response(ATMDetailSerializer(atm).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# 4. GET /atms/{atmId}, PATCH /atms/{atmId}
# ---------------------------------------------------------------------------

class ATMDetailView(APIView):
    """Contract §14 (GET) and §16 (PATCH)."""
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [IsSuperAdmin()]
        return [IsAdmin()]

    def get(self, request, atm_id):
        atm = get_object_or_404(ATM, atm_id=atm_id)
        return Response(ATMDetailSerializer(atm).data)

    def patch(self, request, atm_id):
        atm = get_object_or_404(ATM, atm_id=atm_id)
        serializer = ATMUpdateSerializer(atm, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        atm = serializer.save()
        return Response(ATMDetailSerializer(atm).data)


# ---------------------------------------------------------------------------
# 5. GET /services
# ---------------------------------------------------------------------------

class ServiceListView(APIView):
    """
    Contract §17. Auth: "Bearer or X-API-Key" — both admins and the kiosk
    hit this, so both authentication classes are registered and either one
    passing is enough (ApiKeyAuthentication returns a stand-in user that
    satisfies IsAuthenticated; see common/api_key_auth.py).
    """
    authentication_classes = [JWTAuthentication, ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        services = Service.objects.all().order_by("name")
        return Response(ServiceSerializer(services, many=True).data)


# ---------------------------------------------------------------------------
# 6. GET /atms/network-stats
# ---------------------------------------------------------------------------

class NetworkStatsView(APIView):
    """
    Backs the admin dashboard KPI row (online/low-cash/offline counts +
    uptime %). Added post-review per SARS-Final-Folder-Structure.md —
    NOT in docs/api-contract.md's endpoint list yet. Response shape below
    is my best read of "backs the admin KPI row"; صفية, flag me if the
    dashboard needs different/additional fields and I'll adjust, and
    someone should add this endpoint to docs/api-contract.md once the
    shape is confirmed.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        total = ATM.objects.count()
        online = ATM.objects.filter(status=ATM.ONLINE).count()
        offline = ATM.objects.filter(status=ATM.OFFLINE).count()
        maintenance = ATM.objects.filter(status=ATM.MAINTENANCE).count()
        low_cash = ATM.objects.filter(cash_status=ATM.LOW).count()
        empty_cash = ATM.objects.filter(cash_status=ATM.EMPTY).count()

        window_start = timezone.now() - timedelta(days=UPTIME_WINDOW_DAYS)
        recent_logs = HeartbeatLog.objects.filter(received_at__gte=window_start)
        recent_total = recent_logs.count()
        recent_online = recent_logs.filter(status=ATM.ONLINE).count()
        uptime_percentage = (
            round((recent_online / recent_total) * 100, 2) if recent_total else None
        )

        return Response(
            {
                "totalAtms": total,
                "online": online,
                "offline": offline,
                "maintenance": maintenance,
                "lowCash": low_cash,
                "emptyCash": empty_cash,
                "uptimePercentage": uptime_percentage,
                "uptimeWindowDays": UPTIME_WINDOW_DAYS,
                "calculatedAt": timezone.now(),
            }
        )
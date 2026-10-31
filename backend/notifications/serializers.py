# backend/notifications/serializers.py
import re

from rest_framework import serializers

from atms.models import Service

from .models import Notification

PHONE_RE = re.compile(r"^\+?[0-9]{8,15}$")


class SmsRequestSerializer(serializers.Serializer):
    """
    POST /notifications/sms. Plain Serializer on purpose: nothing here is
    ever saved as-is, so phoneNumber can't leak into the DB.
    """
    atmId = serializers.CharField(max_length=50)
    phoneNumber = serializers.CharField(write_only=True)
    requestedService = serializers.ChoiceField(choices=Service.SERVICE_CHOICES)
    requestedAmount = serializers.FloatField(required=False, allow_null=True, min_value=0)

    def validate_phoneNumber(self, value):
        cleaned = re.sub(r"[\s\-()]", "", value)
        if not PHONE_RE.match(cleaned):
            raise serializers.ValidationError("Invalid phone number.")
        return cleaned


class NotificationListSerializer(serializers.ModelSerializer):
    """Backs data[] of GET /notifications (admin log). No phone field exists."""
    notificationId = serializers.UUIDField(source="notification_id")
    atmId = serializers.CharField(source="atm_id")
    branchName = serializers.CharField(source="atm.branch_name")
    requestedService = serializers.CharField(source="requested_service")
    requestedAmount = serializers.FloatField(source="requested_amount", allow_null=True)
    failureReason = serializers.CharField(source="failure_reason")
    sentAt = serializers.DateTimeField(source="sent_at")
    createdAt = serializers.DateTimeField(source="created_at")

    class Meta:
        model = Notification
        fields = [
            "notificationId",
            "atmId",
            "branchName",
            "requestedService",
            "requestedAmount",
            "status",
            "failureReason",
            "sentAt",
            "createdAt",
        ]
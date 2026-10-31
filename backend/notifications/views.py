# backend/notifications/views.py
import uuid

from django.shortcuts import get_object_or_404
from kombu.exceptions import OperationalError
from rest_framework import generics, status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.permissions import IsAdmin
from atms.models import ATM
from common.api_key_auth import ApiKeyAuthentication
from common.pagination import StandardResultsSetPagination

from .models import Notification
from .serializers import NotificationListSerializer, SmsRequestSerializer
from .tasks import send_sms_task


class QueueUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "SMS queue unavailable."
    default_code = "queue_unavailable"


class SendSmsView(APIView):
    """POST /notifications/sms (Kiosk, API key). Returns 202 + taskId."""
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SmsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        atm = get_object_or_404(ATM, atm_id=data["atmId"])
        phone_number = data["phoneNumber"]  # goes to the task only, never the DB

        notification_id = uuid.uuid4()
        task_id = str(notification_id)
        notification = Notification.objects.create(
            notification_id=notification_id,
            atm=atm,
            requested_service=data["requestedService"],
            requested_amount=data.get("requestedAmount"),
            celery_task_id=task_id,
        )

        try:
            send_sms_task.apply_async(args=[task_id, phone_number], task_id=task_id)
        except OperationalError:
            notification.status = Notification.FAILED
            notification.failure_reason = "QUEUE_UNAVAILABLE"
            notification.save(update_fields=["status", "failure_reason", "updated_at"])
            raise QueueUnavailable()

        return Response(
            {"taskId": task_id, "status": notification.status},
            status=status.HTTP_202_ACCEPTED,
        )


class SmsStatusView(APIView):
    """GET /notifications/sms/{taskId}/status (Kiosk, API key)."""
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        notification = get_object_or_404(Notification, celery_task_id=task_id)
        return Response(
            {
                "taskId": notification.celery_task_id,
                "status": notification.status,
                "updatedAt": notification.updated_at,
            }
        )


class NotificationListView(generics.GenericAPIView):
    """GET /notifications (Admin, JWT). Filters: status, atmId, service."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    pagination_class = StandardResultsSetPagination
    serializer_class = NotificationListSerializer

    def get(self, request):
        qs = Notification.objects.select_related("atm").order_by("-created_at")

        status_param = request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        atm_param = request.query_params.get("atmId")
        if atm_param:
            qs = qs.filter(atm_id=atm_param)

        service_param = request.query_params.get("service")
        if service_param:
            qs = qs.filter(requested_service=service_param)

        page = self.paginate_queryset(qs)
        serializer = NotificationListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
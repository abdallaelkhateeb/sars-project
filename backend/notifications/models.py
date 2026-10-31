# backend/notifications/models.py
import uuid

from django.db import models

from atms.models import ATM, Service


class Notification(models.Model):
    """
    SMS audit log. NFR 4 (Data Minimization): the customer's phone number
    is NEVER stored here, in any form. It only travels request -> Celery
    task argument -> SMS provider.
    """
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (SENT, "Sent"),
        (FAILED, "Failed"),
    ]

    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The alternative ATM the customer is being told about.
    atm = models.ForeignKey(ATM, on_delete=models.CASCADE, related_name="notifications")

    requested_service = models.CharField(max_length=50, choices=Service.SERVICE_CHOICES)
    requested_amount = models.FloatField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    celery_task_id = models.CharField(max_length=255, null=True, blank=True, unique=True)

    # Short fixed code only (e.g. GATEWAY_UNREACHABLE). Never free text from
    # the gateway, because it could echo the phone number back.
    failure_reason = models.CharField(max_length=50, blank=True, default="")
    sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Notification({self.notification_id}) — {self.status}"
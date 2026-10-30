# backend/notifications/models.py
import uuid
from django.db import models

from atms.models import ATM, Service


class Notification(models.Model):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (SENT, "Sent"),
        (FAILED, "Failed"),
    ]

    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # الماكينة البديلة اللي بنبلّغ العميل عنها
    atm = models.ForeignKey(ATM, on_delete=models.CASCADE, related_name="notifications")

    requested_service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, related_name="notifications"
    )
    requested_amount = models.FloatField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    celery_task_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Notification({self.notification_id}) — {self.status}"
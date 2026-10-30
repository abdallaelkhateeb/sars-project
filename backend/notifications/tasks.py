# backend/notifications/tasks.py
import logging

from celery import shared_task
from django.utils import timezone

from .models import Notification
from .sms import SmsDeliveryError, build_message, get_provider

logger = logging.getLogger(__name__)


def _mark_failed(notification, code):
    notification.status = Notification.FAILED
    notification.failure_reason = code
    notification.save(update_fields=["status", "failure_reason", "updated_at"])


@shared_task(bind=True, max_retries=3)
def send_sms_task(self, notification_id, phone_number):
    """
    The phone number exists only as this task's argument. It is never saved
    to the DB, never returned (the result is just the notification id), and
    never logged. Exception messages are not stored either.
    """
    try:
        notification = Notification.objects.select_related("atm").get(pk=notification_id)
    except Notification.DoesNotExist:
        logger.error("send_sms_task: notification %s not found", notification_id)
        return None

    if notification.status == Notification.SENT:  # idempotent on redelivery
        return str(notification_id)

    message = build_message(notification)

    try:
        get_provider().send(phone_number, message)
    except SmsDeliveryError as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=5 * 2 ** self.request.retries)
        logger.warning("SMS %s failed: %s", notification_id, exc.code)
        _mark_failed(notification, exc.code)
        return str(notification_id)
    except Exception as exc:  # provider bug: don't retry, don't store its message
        logger.error("SMS %s failed: %s", notification_id, type(exc).__name__)
        _mark_failed(notification, "UNEXPECTED")
        return str(notification_id)

    notification.status = Notification.SENT
    notification.sent_at = timezone.now()
    notification.failure_reason = ""
    notification.save(update_fields=["status", "sent_at", "failure_reason", "updated_at"])
    return str(notification_id)
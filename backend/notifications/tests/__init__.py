# backend/notifications/tests/test_sms_dispatch.py
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.urls import reverse
from kombu.exceptions import OperationalError
from rest_framework.test import APIClient

from atms.models import ATM
from notifications.models import Notification
from notifications.sms import SmsDeliveryError
from notifications.tasks import send_sms_task

PHONE = "+201012345678"


class AdminStub:
    is_authenticated = True
    role = "ADMIN"


@override_settings(ATM_API_KEY="test-key")
class SmsDispatchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.atm = ATM.objects.create(
            atm_id="ATM-002", branch_name="Maadi Branch", latitude=29.96, longitude=31.25
        )
        self.url = reverse("notifications-sms-create")
        self.payload = {
            "atmId": "ATM-002",
            "phoneNumber": PHONE,
            "requestedService": "WITHDRAWAL",
            "requestedAmount": 1500,
        }

    def _post(self, payload=None, key="test-key"):
        headers = {"HTTP_X_API_KEY": key} if key else {}
        return self.client.post(self.url, payload or self.payload, format="json", **headers)

    @patch("notifications.views.send_sms_task.apply_async")
    def test_creates_pending_notification_and_enqueues(self, mock_apply):
        response = self._post()
        self.assertEqual(response.status_code, 202)
        notification = Notification.objects.get()
        self.assertEqual(notification.status, Notification.PENDING)
        self.assertEqual(response.json()["taskId"], notification.celery_task_id)
        mock_apply.assert_called_once()

    def test_requires_api_key(self):
        self.assertEqual(self._post(key=None).status_code, 401)

    @patch("notifications.views.send_sms_task.apply_async")
    def test_invalid_phone_rejected(self, _):
        payload = {**self.payload, "phoneNumber": "abc"}
        self.assertEqual(self._post(payload).status_code, 400)
        self.assertEqual(Notification.objects.count(), 0)

    @patch("notifications.views.send_sms_task.apply_async")
    def test_unknown_atm_404(self, _):
        payload = {**self.payload, "atmId": "NOPE"}
        self.assertEqual(self._post(payload).status_code, 404)

    @patch("notifications.views.send_sms_task.apply_async", side_effect=OperationalError("down"))
    def test_queue_down_returns_503_and_marks_failed(self, _):
        # assertLogs captures Django's 5xx error log, so the debug-report
        # handler (which breaks on Python 3.14 + Django 5.0.6) never runs.
        with self.assertLogs("django.request", level="ERROR"):
            response = self._post()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(Notification.objects.get().failure_reason, "QUEUE_UNAVAILABLE")

    def _make_notification(self):
        return Notification.objects.create(
            atm=self.atm, requested_service="WITHDRAWAL", requested_amount=1500
        )

    def test_task_marks_sent(self):
        n = self._make_notification()
        send_sms_task.apply(args=[str(n.pk), PHONE])
        n.refresh_from_db()
        self.assertEqual(n.status, Notification.SENT)
        self.assertIsNotNone(n.sent_at)

    @patch("notifications.tasks.get_provider")
    def test_task_marks_failed_when_retries_exhausted(self, mock_get_provider):
        mock_get_provider.return_value = Mock(
            send=Mock(side_effect=SmsDeliveryError("GATEWAY_UNREACHABLE"))
        )
        n = self._make_notification()
        send_sms_task.apply(args=[str(n.pk), PHONE], retries=3)
        n.refresh_from_db()
        self.assertEqual(n.status, Notification.FAILED)
        self.assertEqual(n.failure_reason, "GATEWAY_UNREACHABLE")

    def test_status_endpoint(self):
        n = self._make_notification()
        n.celery_task_id = str(n.pk)
        n.save()
        response = self.client.get(
            reverse("notifications-sms-status", args=[n.celery_task_id]),
            HTTP_X_API_KEY="test-key",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "PENDING")

    def test_admin_list_requires_auth(self):
        self.assertEqual(self.client.get(reverse("notifications-list")).status_code, 401)

    def test_admin_list_paginated(self):
        self._make_notification()
        self.client.force_authenticate(user=AdminStub())
        response = self.client.get(reverse("notifications-list"))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["meta"]["total"], 1)
        self.assertEqual(body["data"][0]["branchName"], "Maadi Branch")
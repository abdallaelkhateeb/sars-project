# backend/notifications/tests/test_no_phone_persistence.py
"""NFR 4 regression: the phone number must never reach the database."""
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from atms.models import ATM
from notifications.models import Notification
from notifications.tasks import send_sms_task

PHONE_DIGITS = "201012345678"


class AdminStub:
    is_authenticated = True
    role = "ADMIN"


def _all_rows_as_text():
    return " ".join(str(row) for row in Notification.objects.values())


@override_settings(ATM_API_KEY="test-key")
class NoPhonePersistenceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        ATM.objects.create(
            atm_id="ATM-002", branch_name="Maadi Branch", latitude=29.96, longitude=31.25
        )

    def test_model_has_no_phone_like_field(self):
        names = [f.name.lower() for f in Notification._meta.get_fields()]
        self.assertFalse([n for n in names if "phone" in n or "mobile" in n or "msisdn" in n])

    @patch("notifications.views.send_sms_task.apply_async")
    def test_phone_absent_from_db_responses_after_request_and_task(self, _):
        response = self.client.post(
            reverse("notifications-sms-create"),
            {
                "atmId": "ATM-002",
                "phoneNumber": f"+{PHONE_DIGITS}",
                "requestedService": "WITHDRAWAL",
            },
            format="json",
            HTTP_X_API_KEY="test-key",
        )
        self.assertEqual(response.status_code, 202)
        self.assertNotIn(PHONE_DIGITS, response.content.decode())

        task_id = response.json()["taskId"]
        send_sms_task.apply(args=[task_id, f"+{PHONE_DIGITS}"])

        self.assertNotIn("1012345678", _all_rows_as_text())

        self.client.force_authenticate(user=AdminStub())
        listing = self.client.get(reverse("notifications-list"))
        self.assertNotIn("1012345678", listing.content.decode())

    @patch("notifications.tasks.get_provider")
    def test_failure_reason_never_contains_provider_error_text(self, mock_get_provider):
        mock_get_provider.return_value = Mock(
            send=Mock(side_effect=RuntimeError(f"gateway rejected +{PHONE_DIGITS}"))
        )
        n = Notification.objects.create(
            atm=ATM.objects.get(), requested_service="WITHDRAWAL"
        )
        send_sms_task.apply(args=[str(n.pk), f"+{PHONE_DIGITS}"])
        n.refresh_from_db()
        self.assertEqual(n.failure_reason, "UNEXPECTED")
        self.assertNotIn("1012345678", _all_rows_as_text())
# backend/notifications/sms.py
"""
SMS providers. Pick one with settings.SMS_PROVIDER:
  "console"   -> dev/tests: logs a masked number + message, sends nothing
  "bank_http" -> the bank's HTTP gateway (payload below is a PLACEHOLDER,
                 adjust once the bank shares its API spec)

Rule: nothing in this file may log or raise anything containing the full
phone number.
"""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class SmsDeliveryError(Exception):
    """`code` is a short fixed string that is safe to store in the DB."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


def mask_phone(phone):
    if len(phone) <= 5:
        return "*" * len(phone)
    return phone[:3] + "*" * (len(phone) - 5) + phone[-2:]


def build_message(notification):
    atm = notification.atm
    service = notification.get_requested_service_display()
    maps_link = f"https://www.google.com/maps?q={atm.latitude},{atm.longitude}"
    return (
        f"SARS: nearest available ATM for {service}: "
        f"{atm.branch_name} (ID {atm.atm_id}). Directions: {maps_link}"
    )


class ConsoleSmsProvider:
    def send(self, phone_number, message):
        logger.info("[SMS:console] to=%s message=%s", mask_phone(phone_number), message)
        logger.warning("[SMS:console] to=%s message=%s", mask_phone(phone_number), message)


class BankHttpSmsProvider:
    def send(self, phone_number, message):
        url = getattr(settings, "SMS_GATEWAY_URL", "")
        if not url:
            raise SmsDeliveryError("NOT_CONFIGURED")

        payload = json.dumps({"to": phone_number, "message": message}).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {getattr(settings, 'SMS_GATEWAY_API_KEY', '')}",
            },
        )
        timeout = getattr(settings, "SMS_GATEWAY_TIMEOUT", 10)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if not 200 <= response.status < 300:
                    raise SmsDeliveryError("GATEWAY_REJECTED")
        except urllib.error.HTTPError:
            raise SmsDeliveryError("GATEWAY_REJECTED") from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise SmsDeliveryError("GATEWAY_UNREACHABLE") from None


def get_provider():
    name = getattr(settings, "SMS_PROVIDER", "console")
    if name == "console":
        return ConsoleSmsProvider()
    if name == "bank_http":
        return BankHttpSmsProvider()
    raise ImproperlyConfigured(f"Unknown SMS_PROVIDER: {name!r}")
# backend/common/api_key_auth.py
"""
Authenticates ATM device / kiosk requests via the `X-API-Key` header,
per NFR 4 ("All endpoints communicating with the ATMs must use API keys").

TEMPORARY / MINIMAL implementation: checks the header against a single
shared key (settings.ATM_API_KEY). The planned design (per
SARS-Final-Folder-Structure.md) is per-device keys salted with
ATM_API_KEY_SALT — this file is unowned in the team table, so I (محمد)
wrote just enough to unblock atms/views.py. Whoever picks up API-key
hardening: swap authenticate() below for a real per-ATM lookup, this
class's interface (returns (user, None) or raises AuthenticationFailed)
doesn't need to change.
"""
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ApiKeyUser:
    """
    Lightweight stand-in for `request.user` on API-Key-authenticated
    requests. Not a real Django user — just enough to satisfy
    IsAuthenticated and to identify the caller as a device in logs.
    """
    is_authenticated = True
    is_device = True

    def __str__(self):
        return "atm-device"


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            # No credentials supplied on this scheme -> let DRF fall through
            # to permission_classes, which will 401 via NotAuthenticated.
            return None

        expected = getattr(settings, "ATM_API_KEY", None)
        if not expected or api_key != expected:
            raise AuthenticationFailed("Invalid or missing API key.")

        return (ApiKeyUser(), None)

    def authenticate_header(self, request):
        return "X-API-Key"
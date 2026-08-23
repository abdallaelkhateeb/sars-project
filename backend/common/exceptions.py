# backend/common/exceptions.py
"""
Wraps DRF's default exception handling into the contract's standard error
object shape (docs/api-contract.md, section 4):

    {
      "error": {
        "code": "...",
        "message": "...",
        "details": { ... } | null
      }
    }

Already wired in settings/base.py via REST_FRAMEWORK["EXCEPTION_HANDLER"] —
this file just had to actually exist.
"""
from rest_framework.views import exception_handler as drf_exception_handler

_STATUS_CODE_MAP = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "UNPROCESSABLE_ENTITY",
    429: "RATE_LIMITED",
    500: "INTERNAL_SERVER_ERROR",
    503: "SERVICE_UNAVAILABLE",
}


def _flatten_message(detail):
    """DRF error `detail` can be a string, list, or nested dict of field
    errors. Reduce it to one human-readable message for error.message,
    keeping the original structure in error.details for debugging."""
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail:
        return str(detail[0])
    if isinstance(detail, dict) and detail:
        first_key = next(iter(detail))
        first_val = detail[first_key]
        if isinstance(first_val, list) and first_val:
            return f"{first_key}: {first_val[0]}"
        return f"{first_key}: {first_val}"
    return "An error occurred."


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data

    # Don't double-wrap if a view already returned the standard shape itself.
    if isinstance(detail, dict) and set(detail.keys()) == {"error"}:
        return response

    response.data = {
        "error": {
            "code": _STATUS_CODE_MAP.get(response.status_code, "ERROR"),
            "message": _flatten_message(detail),
            "details": detail if isinstance(detail, (dict, list)) else None,
        }
    }
    return response
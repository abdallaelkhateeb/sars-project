# backend/accounts/permissions.py
"""
TEMPORARY / MINIMAL — عبدالله owns backend/accounts/ (Task: Admin auth &
RBAC). I (محمد) added just this file so atms/views.py can enforce the
RBAC matrix (docs/api-contract.md §19) today instead of waiting.

Assumes request.user has a `.role` attribute set to "ADMIN" or
"SUPER_ADMIN", matching the ERD's Admin.role field and populated by
whatever JWT authentication backend accounts/ ends up using
(djangorestframework-simplejwt is already in requirements.txt).

عبدالله — please review/replace with your real implementation once the
Admin model + login/refresh views land; the class names and
has_permission() contract below are what atms/views.py imports against,
so keep those the same if you swap the internals.
"""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Any authenticated bank staff account (ADMIN or SUPER_ADMIN)."""

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        role = getattr(user, "role", None)
        return bool(
            user and user.is_authenticated and role in ("ADMIN", "SUPER_ADMIN")
        )


class IsSuperAdmin(BasePermission):
    """SUPER_ADMIN only — gates POST /atms and PATCH /atms/{atmId}."""

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        role = getattr(user, "role", None)
        return bool(user and user.is_authenticated and role == "SUPER_ADMIN")
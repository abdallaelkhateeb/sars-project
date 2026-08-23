from django.contrib.auth.models import AbstractUser
from django.db import models


class Admin(AbstractUser):
    """
    PLACEHOLDER - minimal implementation so AUTH_USER_MODEL = 'accounts.Admin'
    doesn't crash the app on boot.

    Whoever owns backend/accounts/ should replace this with the real version:
    role field (ADMIN / SUPER_ADMIN per ERD), used by accounts/permissions.py
    for RBAC (IsAdmin, IsSuperAdmin) as described in the folder structure doc.
    """

    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (SUPER_ADMIN, "Super Admin"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ADMIN)

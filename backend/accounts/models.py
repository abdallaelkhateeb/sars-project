import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class Admin(AbstractUser):
    """
    Custom user model for SARS Admins.
    Extends Django's AbstractUser to utilize built-in password hashing and auth features.
    """
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('SUPER_ADMIN', 'Super Admin'),
    )
    
    # Use UUID as primary key to match the API contract
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # RBAC role field
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ADMIN')
    
    # Note: AbstractUser already provides 'username', 'password', and 'date_joined' (used as created_at)

    def __str__(self):
        return f"{self.username} ({self.role})"
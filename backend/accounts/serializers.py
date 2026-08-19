from rest_framework import serializers
from .models import Admin

class AdminSerializer(serializers.ModelSerializer):
    """
    Serializer for returning Admin details without sensitive data.
    """
    admin_id = serializers.UUIDField(source='id', read_only=True)
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = Admin
        fields = ['admin_id', 'username', 'role', 'created_at']


class LoginSerializer(serializers.Serializer):
    """
    Serializer for handling login payloads.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class RefreshSerializer(serializers.Serializer):
    """
    Serializer for handling token refresh payloads.
    """
    refreshToken = serializers.CharField(required=True)
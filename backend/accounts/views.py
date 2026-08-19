from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, RefreshSerializer

class LoginView(APIView):
    # Allow unauthenticated users to hit this endpoint
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            # Authenticate against the Admin model
            user = authenticate(username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    "accessToken": str(refresh.access_token),
                    "refreshToken": str(refresh),
                    "expiresIn": 3600,  # Assuming 1-hour expiration
                    "role": user.role
                }, status=status.HTTP_200_OK)
            
            return Response(
                {"detail": "Invalid credentials"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data['refreshToken']
            try:
                token = RefreshToken(refresh_token)
                return Response({
                    "accessToken": str(token.access_token),
                    "expiresIn": 3600
                }, status=status.HTTP_200_OK)
            except Exception:
                return Response(
                    {"detail": "Invalid or expired refresh token"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
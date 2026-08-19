import os
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            return None 
            
        expected_salt = os.environ.get('ATM_API_KEY_SALT')
        
        if api_key != expected_salt:
            raise AuthenticationFailed('Invalid API Key')
            
        return (None, api_key)
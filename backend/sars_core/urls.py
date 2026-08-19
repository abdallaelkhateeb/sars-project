from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Map auth endpoints to /api/v1/auth/
    path('api/v1/auth/', include('accounts.urls')),
]
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth endpoints -> /api/v1/auth/login, /api/v1/auth/refresh
    path('api/v1/auth/', include('accounts.urls')),
    # ATM endpoints -> /api/v1/atms, /api/v1/atms/{id}/heartbeat,
    #   /api/v1/atms/network-stats, /api/v1/services, etc.
    #   (this was missing before - added so Task 3's views.py has somewhere to attach)
    path('api/v1/', include('atms.urls')),
    # Add these as سارة / صفية push their apps:
    # path('api/v1/', include('routing.urls')),
    # path('api/v1/', include('notifications.urls')),
]

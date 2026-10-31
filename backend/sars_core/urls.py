from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path('admin/', admin.site.urls),

    # Auth endpoints -> /api/v1/auth/login, /api/v1/auth/refresh
    path('api/v1/auth/', include('accounts.urls')),

    # ATM endpoints
    path('api/v1/', include('atms.urls')),

    # Routing endpoints -> /api/v1/routing/alternatives
    path('api/v1/routing/', include('routing.urls')),

    # Notifications endpoints
    path('api/v1/', include('notifications.urls')),
]

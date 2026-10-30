# backend/notifications/urls.py
from django.urls import path

from .views import NotificationListView, SendSmsView, SmsStatusView

urlpatterns = [
    path("notifications/sms", SendSmsView.as_view(), name="notifications-sms-create"),
    path(
        "notifications/sms/<str:task_id>/status",
        SmsStatusView.as_view(),
        name="notifications-sms-status",
    ),
    path("notifications", NotificationListView.as_view(), name="notifications-list"),
]
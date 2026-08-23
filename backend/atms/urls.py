# backend/atms/urls.py
from django.urls import path

from . import views

app_name = "atms"

# --- REST endpoints (Task 3 — done) ---
urlpatterns = [
    path(
        "atms/<str:atm_id>/transactions/attempt",
        views.TransactionAttemptView.as_view(),
        name="transaction-attempt",
    ),
    path(
        "atms/<str:atm_id>/heartbeat",
        views.HeartbeatView.as_view(),
        name="heartbeat",
    ),
    path(
        "atms/network-stats",
        views.NetworkStatsView.as_view(),
        name="network-stats",
    ),
    # NOTE: network-stats is registered BEFORE atms/<str:atm_id> below,
    # otherwise Django would match "network-stats" as an atm_id and this
    # endpoint would 404 against ATMDetailView instead.
    path(
        "atms",
        views.ATMListCreateView.as_view(),
        name="atm-list-create",
    ),
    path(
        "atms/<str:atm_id>",
        views.ATMDetailView.as_view(),
        name="atm-detail",
    ),
    path(
        "services",
        views.ServiceListView.as_view(),
        name="service-list",
    ),
]

# --- WebSocket routes (Task 4: consumers.py — still pending) ---
# asgi.py imports this list directly - keep it in this file, not a separate routing.py
websocket_urlpatterns = [
    # re_path(r"ws/dashboard$", consumers.DashboardConsumer.as_asgi()),
]
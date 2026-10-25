from django.urls import path

from .views import RoutingAlternativesView


urlpatterns = [
    path(
        "alternatives",
        RoutingAlternativesView.as_view(),
        name="routing-alternatives",
    ),
]
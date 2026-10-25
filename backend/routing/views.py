from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.api_key_auth import ApiKeyAuthentication

from .services import RoutingEngine


class RoutingAlternativesView(APIView):
    """
    POST /api/v1/routing/alternatives

    Returns the nearest suitable ATM alternatives.
    """

    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]

    """
    POST /api/v1/routing/alternatives

    Returns the nearest suitable ATM alternatives.
    """

    authentication_classes = [ApiKeyAuthentication]

    def post(self, request):
        data = request.data

        latitude = data.get("latitude")
        longitude = data.get("longitude")
        requested_service = data.get("requestedService")
        requested_amount = data.get("requestedAmount")
        exclude_atm_id = data.get("atmId")

        if latitude is None or longitude is None:
            return Response(
                {
                    "error": "latitude and longitude are required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not requested_service:
            return Response(
                {
                    "error": "requestedService is required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            latitude = float(latitude)
            longitude = float(longitude)

            if requested_amount is not None:
                requested_amount = float(requested_amount)

        except (TypeError, ValueError):
            return Response(
                {
                    "error": "Invalid numeric value"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        engine = RoutingEngine()

        alternatives = engine.find_alternatives(
            latitude=latitude,
            longitude=longitude,
            requested_service=requested_service,
            requested_amount=requested_amount,
            exclude_atm_id=exclude_atm_id,
        )

        return Response(
            {
                "alternatives": alternatives
            },
            status=status.HTTP_200_OK,
        )

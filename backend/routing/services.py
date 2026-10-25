from typing import Optional

from django.conf import settings
from django.db.models import QuerySet

from atms.models import ATM, Service
from common.geo import haversine_km

from .gateways import MappingGateway


class RoutingEngine:
    """
    Finds the best alternative ATMs for a customer.

    Routing rules:
    1. ATM must be ONLINE.
    2. ATM must support the requested service.
    3. ATM must be within the configured radius.
    4. Withdrawal requires sufficient cash:
       current_cash_balance >= requested_amount + buffer_amount.
    5. Google Maps is used for distance and ETA when available.
    6. Haversine is used automatically when Google Maps fails.
    7. Results are sorted by distance and limited to the top 3.
    """

    DEFAULT_RADIUS_KM = 5.0
    DEFAULT_LIMIT = 3

    DEFAULT_CASH_BUFFER = getattr(
        settings,
        "ATM_CASH_BUFFER_AMOUNT",
        50.0,
    )

    def __init__(
        self,
        radius_km: float = DEFAULT_RADIUS_KM,
        limit: int = DEFAULT_LIMIT,
        cash_buffer: float = DEFAULT_CASH_BUFFER,
        mapping_gateway: Optional[MappingGateway] = None,
    ):
        self.radius_km = radius_km
        self.limit = limit
        self.cash_buffer = cash_buffer
        self.mapping_gateway = (
            mapping_gateway
            or MappingGateway()
        )

    def find_alternatives(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        requested_service: Optional[str] = None,
        requested_amount: Optional[float] = None,
        exclude_atm_id: Optional[str] = None,
        origin_atm: Optional[ATM] = None,
        origin_atm_id: Optional[str] = None,
        buffer_amount: Optional[float] = None,
        radius_km: Optional[float] = None,
    ):
        """
        Find suitable alternative ATMs.

        Supports:
        - latitude / longitude requests
        - origin_atm object from TransactionAttemptView
        - origin_atm_id for compatibility with the task specification
        """

        # ---------------------------------------------------------
        # 1. Resolve origin ATM
        # ---------------------------------------------------------

        if origin_atm is not None:
            latitude = origin_atm.latitude
            longitude = origin_atm.longitude
            exclude_atm_id = origin_atm.atm_id

        elif origin_atm_id:
            try:
                origin_atm = ATM.objects.get(
                    atm_id=origin_atm_id
                )
            except ATM.DoesNotExist:
                raise ValueError(
                    "Origin ATM not found."
                )

            latitude = origin_atm.latitude
            longitude = origin_atm.longitude
            exclude_atm_id = origin_atm.atm_id

        if latitude is None or longitude is None:
            raise ValueError(
                "latitude and longitude or an origin ATM "
                "are required."
            )

        if requested_service is None:
            raise ValueError(
                "requested_service is required."
            )

        # ---------------------------------------------------------
        # 2. Configuration
        # ---------------------------------------------------------

        effective_cash_buffer = (
            self.cash_buffer
            if buffer_amount is None
            else buffer_amount
        )

        effective_radius = (
            self.radius_km
            if radius_km is None
            else radius_km
        )

        # ---------------------------------------------------------
        # 3. Only ONLINE ATMs
        # ---------------------------------------------------------

        candidates = (
            ATM.objects
            .filter(status=ATM.ONLINE)
            .prefetch_related("services")
        )

        # Do not recommend the ATM where the customer currently is.
        if exclude_atm_id:
            candidates = candidates.exclude(
                atm_id=exclude_atm_id
            )

        # ---------------------------------------------------------
        # 4. Requested service filter
        # ---------------------------------------------------------

        candidates = self.filter_by_service(
            candidates,
            requested_service,
        )

        # ---------------------------------------------------------
        # 5. Cash sufficiency filter
        # ---------------------------------------------------------

        candidates = self.filter_by_cash(
            candidates,
            requested_service,
            requested_amount,
            cash_buffer=effective_cash_buffer,
        )

        # ---------------------------------------------------------
        # 6. Radius filter
        # ---------------------------------------------------------

        candidates = self.filter_by_radius(
            candidates,
            latitude,
            longitude,
            radius_km=effective_radius,
        )

        # ---------------------------------------------------------
        # 7. Calculate distance / ETA
        # ---------------------------------------------------------

        results = []

        if not candidates:
            return results

        # Convert candidates into a list so that the order remains
        # exactly the same as the Google Maps destinations order.
        candidates = list(candidates)

        destinations = [
            (
                atm.latitude,
                atm.longitude,
            )
            for atm, _ in candidates
        ]

        # ---------------------------------------------------------
        # 8. Try Google Maps Distance Matrix
        # ---------------------------------------------------------

        try:
            mapping_results = (
                self.mapping_gateway.get_distance_matrix(
                    (latitude, longitude),
                    destinations,
                )
            )
        except Exception:
            # Any mapping API failure should trigger fallback.
            mapping_results = None

        # ---------------------------------------------------------
        # 9. Haversine fallback
        # ---------------------------------------------------------

        if mapping_results is None:
            for atm, haversine_distance in candidates:

                mapping_result = self.fallback_haversine(
                    latitude,
                    longitude,
                    atm,
                )

                results.append(
                    self.serialize_candidate(
                        atm=atm,
                        mapping_result=mapping_result,
                        haversine_distance=haversine_distance,
                        requested_amount=requested_amount,
                    )
                )

        # ---------------------------------------------------------
        # 10. Google Maps results
        # ---------------------------------------------------------

        else:
            for index, (
                atm,
                haversine_distance,
            ) in enumerate(candidates):

                mapping_result = mapping_results[index]

                results.append(
                    self.serialize_candidate(
                        atm=atm,
                        mapping_result=mapping_result,
                        haversine_distance=haversine_distance,
                        requested_amount=requested_amount,
                    )
                )

        # ---------------------------------------------------------
        # 11. Sort by distance
        # ---------------------------------------------------------

        results.sort(
            key=lambda item: item["distanceKm"]
        )

        # ---------------------------------------------------------
        # 12. Return top 3
        # ---------------------------------------------------------

        return results[: self.limit]

    def filter_by_service(
        self,
        candidates: QuerySet,
        requested_service: str,
    ) -> QuerySet:
        """
        Keep only ATMs that support the requested service.
        """

        return (
            candidates
            .filter(
                services__name=requested_service
            )
            .distinct()
        )

    def filter_by_cash(
        self,
        candidates: QuerySet,
        requested_service: str,
        requested_amount: Optional[float],
        cash_buffer: Optional[float] = None,
    ) -> QuerySet:
        """
        Apply cash sufficiency rule for withdrawals.

        Required cash:

            requested_amount + buffer_amount
        """

        # No cash filtering for non-withdrawal services.
        if requested_service != Service.WITHDRAWAL:
            return candidates

        # No amount means there is nothing to validate.
        if requested_amount is None:
            return candidates

        effective_cash_buffer = (
            self.cash_buffer
            if cash_buffer is None
            else cash_buffer
        )

        required_cash = (
            requested_amount
            + effective_cash_buffer
        )

        return candidates.filter(
            current_cash_balance__gte=required_cash
        )

    def filter_by_radius(
        self,
        candidates: QuerySet,
        latitude: float,
        longitude: float,
        radius_km: Optional[float] = None,
    ):
        """
        Keep ATMs within the configured radius using Haversine
        distance.
        """

        effective_radius = (
            self.radius_km
            if radius_km is None
            else radius_km
        )

        results = []

        for atm in candidates:

            distance_km = haversine_km(
                latitude,
                longitude,
                atm.latitude,
                atm.longitude,
            )

            if distance_km <= effective_radius:
                results.append(
                    (
                        atm,
                        distance_km,
                    )
                )

        return results

    def fallback_haversine(
        self,
        origin_latitude: float,
        origin_longitude: float,
        atm: ATM,
    ) -> dict:
        """
        Calculate fallback distance and ETA using Haversine.

        Average assumed speed = 30 km/h.
        """

        distance_km = haversine_km(
            origin_latitude,
            origin_longitude,
            atm.latitude,
            atm.longitude,
        )

        average_speed_kmh = 30.0

        eta_minutes = (
            distance_km
            / average_speed_kmh
        ) * 60

        return {
            "distanceKm": round(
                distance_km,
                2,
            ),
            "etaMinutes": round(
                eta_minutes,
                1,
            ),
            "distanceSource": "HAVERSINE_FALLBACK",
        }

    def serialize_candidate(
        self,
        atm: ATM,
        mapping_result: dict,
        haversine_distance: float,
        requested_amount: Optional[float] = None,
    ) -> dict:
        """
        Convert an ATM candidate into the API response format.

        availableCashBalance is returned only when
        requestedAmount was provided.
        """

        result = {
            "atmId": atm.atm_id,
            "branchName": atm.branch_name,
            "latitude": atm.latitude,
            "longitude": atm.longitude,
            "distanceKm": mapping_result["distanceKm"],
            "etaMinutes": mapping_result["etaMinutes"],
            "distanceSource": mapping_result["distanceSource"],
            "status": atm.status,
            "cashStatus": atm.cash_status,
            "services": atm.get_supported_services(),
        }

        if requested_amount is not None:
            result["availableCashBalance"] = (
                atm.current_cash_balance
            )

        return result

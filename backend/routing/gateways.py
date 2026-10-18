import requests
from django.conf import settings

from common.geo import haversine_km


class MappingGateway:
    """
    Wrapper around the Google Maps Distance Matrix API.

    Provides:
    - get_distance_matrix()
    - get_eta()
    - get_distance_and_eta() for backward compatibility
    - fallback_haversine()
    """

    GOOGLE_MAPS_URL = (
        "https://maps.googleapis.com/maps/api/distancematrix/json"
    )

    def __init__(self, api_key=None, timeout=2):
        self.api_key = (
            api_key
            if api_key is not None
            else getattr(settings, "GOOGLE_MAPS_API_KEY", "")
        )
        self.timeout = timeout

    def get_distance_matrix(self, origin, destinations):
        """
        Get road distance and ETA from Google Maps.

        origin:
            (latitude, longitude)

        destinations:
            list of (latitude, longitude)

        Returns:
            list of dictionaries, one per destination.
        """

        if not self.api_key:
            return None

        if not destinations:
            return []

        origin_lat, origin_lng = origin

        destination_string = "|".join(
            f"{lat},{lng}"
            for lat, lng in destinations
        )

        params = {
            "origins": f"{origin_lat},{origin_lng}",
            "destinations": destination_string,
            "key": self.api_key,
        }

        try:
            response = requests.get(
                self.GOOGLE_MAPS_URL,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

            if data.get("status") != "OK":
                return None

            rows = data.get("rows", [])

            if not rows:
                return None

            elements = rows[0].get("elements", [])

            if len(elements) != len(destinations):
                return None

            results = []

            for element in elements:
                if element.get("status") != "OK":
                    return None

                distance_meters = element["distance"]["value"]
                duration_seconds = element["duration"]["value"]

                results.append(
                    {
                        "distanceKm": round(
                            distance_meters / 1000,
                            2,
                        ),
                        "etaMinutes": round(
                            duration_seconds / 60,
                            1,
                        ),
                        "distanceSource": "GOOGLE_MAPS",
                    }
                )

            return results

        except (
            requests.RequestException,
            KeyError,
            TypeError,
            ValueError,
        ):
            return None

    def get_eta(self, origin, destination):
        """
        Get distance and ETA for one destination.
        """

        results = self.get_distance_matrix(
            origin,
            [destination],
        )

        if not results:
            return None

        return results[0]

    def get_distance_and_eta(
        self,
        origin_lat,
        origin_lng,
        destination_lat,
        destination_lng,
    ):
        """
        Backward-compatible wrapper used by existing code/tests.
        """

        return self.get_eta(
            (origin_lat, origin_lng),
            (destination_lat, destination_lng),
        )

    def fallback_haversine(
        self,
        origin_lat,
        origin_lng,
        destination_lat,
        destination_lng,
    ):
        """
        Calculate straight-line distance when Google Maps fails.
        """

        distance_km = haversine_km(
            origin_lat,
            origin_lng,
            destination_lat,
            destination_lng,
        )

        # Approximate urban driving speed.
        average_speed_kmh = 30.0

        eta_minutes = (
            distance_km / average_speed_kmh
        ) * 60

        return {
            "distanceKm": round(distance_km, 2),
            "etaMinutes": round(eta_minutes, 1),
            "distanceSource": "HAVERSINE_FALLBACK",
        }
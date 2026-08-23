# backend/common/geo.py
"""
Shared geo utilities. Not owned by any one person in the team table, so
this lives in common/. Added here because atms/views.py needs a radius
filter for GET /atms?lat=&lng=&radiusKm=.

سارة — feel free to import this directly for routing/services.py's
fallbackHaversine() instead of re-implementing it; same formula, same
units (km), no reason to duplicate it.
"""
import math

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two lat/lng points, in kilometers."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c
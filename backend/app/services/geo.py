import math
from typing import Tuple


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in kilometres between two lat/lng points."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def add_days_offset_bounds(lat: float, lng: float, meters: Tuple[float, float]) -> Tuple[float, float, float, float]:
    """Bounding box (min_lat, min_lng, max_lat, max_lng) for a metres radius."""
    km = meters[0]
    dlat = km / 111.0
    dlon = km / (111.0 * max(math.cos(math.radians(lat)), 0.01))
    return lat - dlat, lng - dlon, lat + dlat, lng + dlon
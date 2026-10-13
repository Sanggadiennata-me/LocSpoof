"""
Geodetic and distance calculation utilities using the Haversine formula.
"""

import math
from typing import Optional
from locspoof.core.models import Coordinates


def haversine_distance_km(coord1: Coordinates, coord2: Coordinates) -> float:
    """
    Calculate the great circle distance between two points on the earth
    using the Haversine formula.
    
    Returns:
        Distance in kilometers.
    """
    # Earth radius in kilometers
    r = 6371.0

    lat1 = math.radians(coord1.latitude)
    lon1 = math.radians(coord1.longitude)
    lat2 = math.radians(coord2.latitude)
    lon2 = math.radians(coord2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2.0) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance = r * c
    return round(distance, 2)

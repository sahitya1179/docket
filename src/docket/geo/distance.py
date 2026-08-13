"""Great-circle distance, for testing an agenda item against a group's boundary.

Impact filtering asks "is this parcel near the people we represent?" — at
neighborhood scale (hundreds of metres to a few km) the haversine formula is
accurate to well under a metre, so there is no reason to pull in a projection
library.
"""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_M = 6_371_008.8


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance between two WGS84 points, in metres."""
    p1, p2 = radians(lat1), radians(lat2)
    dphi = p2 - p1
    dlambda = radians(lon2 - lon1)

    a = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * asin(sqrt(a))


def within_radius(lat1: float, lon1: float, lat2: float, lon2: float, radius_m: float) -> bool:
    return haversine_m(lat1, lon1, lat2, lon2) <= radius_m

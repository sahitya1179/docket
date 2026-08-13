"""Geocoding tests — offline, against a committed cache of real lookups.

The fixture cache holds genuine Census and Nominatim responses captured on
2026-08-13, so these assert the real behaviour of both providers without
hitting the network (and without abusing Nominatim's usage policy).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from docket.geo import Geocoder, haversine_m, within_radius

CACHE_ROOT = Path(__file__).parent / "fixtures" / "geocache"

# Standard street addresses — Census resolves these.
CENSUS_OK = [
    "1600 Pennsylvania Ave NW, Washington, DC 20500",
    "3301 East 12th St, Oakland, CA",
    "1 Broadway, Oakland, CA",
    "5714 Martin Luther King Jr Way, Oakland, CA",
]

# Non-standard forms — Census returns zero matches; the fallback rescues them.
CENSUS_MISSES = [
    "1 Frank H Ogawa Plaza, Oakland, CA 94612",
    "2100 Telegraph Ave, Oakland, CA",
]

OAKLAND_CITY_HALL = "1 Frank H Ogawa Plaza, Oakland, CA 94612"


@pytest.fixture(scope="module")
def geo():
    with Geocoder(offline=True, cache_root=CACHE_ROOT) as g:
        yield g


# ------------------------------------------------------------------ geocoding


@pytest.mark.parametrize("address", CENSUS_OK + CENSUS_MISSES)
def test_every_sample_address_resolves(geo, address):
    """A miss silently drops an agenda item, so the whole sample must resolve."""
    assert geo.geocode(address).found


def test_match_rate_is_total(geo):
    results = [geo.geocode(a) for a in CENSUS_OK + CENSUS_MISSES]
    assert sum(r.found for r in results) == len(results)


def test_census_handles_ordinary_oakland_addresses(geo):
    """Guards against over-correcting: Census is not broken for Oakland."""
    for address in CENSUS_OK:
        assert geo.geocode(address).provider == "census"


def test_fallback_rescues_what_census_drops(geo):
    """Regression: these two return zero Census matches and must fall through."""
    for address in CENSUS_MISSES:
        result = geo.geocode(address)
        assert result.provider == "nominatim"
        assert result.found


def test_results_carry_usable_coordinates(geo):
    result = geo.geocode(OAKLAND_CITY_HALL)
    # Oakland sits near 37.8 N, -122.27 W.
    assert 37.6 < result.latitude < 38.0
    assert -122.4 < result.longitude < -122.1


def test_offline_geocoder_refuses_unknown_addresses(geo):
    """An offline miss is a gap in the fixture, not a silent empty result."""
    with pytest.raises(LookupError):
        geo.geocode("999 Nowhere Rd, Atlantis, XX")


# ------------------------------------------------------------------- distance


def test_distance_between_two_known_oakland_points(geo):
    hall = geo.geocode(OAKLAND_CITY_HALL)
    telegraph = geo.geocode("2100 Telegraph Ave, Oakland, CA")
    metres = haversine_m(
        hall.latitude, hall.longitude, telegraph.latitude, telegraph.longitude
    )
    # Measured 685 m; allow slack for provider-level coordinate drift.
    assert 400 < metres < 1000


def test_identical_points_are_zero_apart():
    assert haversine_m(37.8, -122.27, 37.8, -122.27) == pytest.approx(0.0)


def test_within_radius_brackets_the_boundary(geo):
    hall = geo.geocode(OAKLAND_CITY_HALL)
    telegraph = geo.geocode("2100 Telegraph Ave, Oakland, CA")
    args = (hall.latitude, hall.longitude, telegraph.latitude, telegraph.longitude)
    assert within_radius(*args, radius_m=1000)
    assert not within_radius(*args, radius_m=100)

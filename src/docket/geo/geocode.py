"""Address → coordinates, with a fallback chain.

The US Census geocoder is free and keyless, and handles ordinary street
addresses well — including in Oakland (`3301 E 12th St`, `1 Broadway`,
`5714 Martin Luther King Jr Way` all resolve).

Where it fails is **non-standard address forms**. Verified 2026-08-13, both
return zero matches:

    1 Frank H Ogawa Plaza, Oakland CA   (a plaza, not a numbered street)
    2100 Telegraph Ave, Oakland CA      (resolves only as a named venue)

That was a 2-in-6 miss rate on a realistic sample. Since impact filtering is
the product's core differentiator, a silent geocode miss is a silently dropped
agenda item — the failure mode with no downstream recovery — so anything Census
misses falls through to OpenStreetMap's Nominatim, which resolved both.

Census is still tried first: it is faster and has no rate limit.

Nominatim's usage policy caps us at ~1 request/second and discourages bulk use,
so every lookup is cached permanently on disk. After the first pass over a
jurisdiction the rate limit stops mattering.
"""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

import httpx

from ..cache import DiskCache
from ..config import settings
from ..models import GeocodeResult

log = logging.getLogger(__name__)

CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Nominatim asks for >= 1s between requests from a single client.
_NOMINATIM_MIN_INTERVAL = 1.1


class _RateLimiter:
    """Serializes calls and enforces a minimum gap between them."""

    def __init__(self, min_interval: float) -> None:
        self.min_interval = min_interval
        self._lock = threading.Lock()
        self._last = 0.0

    def wait(self) -> None:
        with self._lock:
            gap = time.monotonic() - self._last
            if gap < self.min_interval:
                time.sleep(self.min_interval - gap)
            self._last = time.monotonic()


_nominatim_limiter = _RateLimiter(_NOMINATIM_MIN_INTERVAL)


class Geocoder:
    """Census first, Nominatim on miss, everything cached forever."""

    def __init__(
        self,
        timeout: float = 30.0,
        offline: bool = False,
        cache_root: Path | None = None,
    ) -> None:
        self.cache = DiskCache("geocode", root=cache_root)
        self.offline = offline
        self._client = httpx.Client(
            timeout=timeout,
            headers={"User-Agent": settings.nominatim_user_agent},
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Geocoder:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ------------------------------------------------------------------ public

    def geocode(self, address: str) -> GeocodeResult:
        """Resolve one address. Always returns a result; check `.found`."""
        key = address.strip().lower()

        cached = self.cache.get(key)
        if cached is not None:
            return GeocodeResult(**cached)

        if self.offline:
            # Tests run offline against the committed cache. A miss here means
            # the fixture cache is incomplete, not that the address is bad.
            raise LookupError(f"offline geocoder has no cached entry for {address!r}")

        result = self._census(address)
        if not result.found:
            log.debug("census miss, falling back to nominatim: %s", address)
            result = self._nominatim(address)

        self.cache.set(key, result.model_dump())
        return result

    # --------------------------------------------------------------- providers

    def _census(self, address: str) -> GeocodeResult:
        try:
            response = self._client.get(
                CENSUS_URL,
                params={
                    "address": address,
                    "benchmark": "Public_AR_Current",
                    "format": "json",
                },
            )
            response.raise_for_status()
            matches = response.json()["result"]["addressMatches"]
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            log.debug("census error for %r: %s", address, exc)
            return GeocodeResult(query=address, found=False, provider="census")

        if not matches:
            return GeocodeResult(query=address, found=False, provider="census")

        best = matches[0]
        return GeocodeResult(
            query=address,
            found=True,
            provider="census",
            latitude=best["coordinates"]["y"],
            longitude=best["coordinates"]["x"],
            matched_address=best.get("matchedAddress"),
        )

    def _nominatim(self, address: str) -> GeocodeResult:
        _nominatim_limiter.wait()
        try:
            response = self._client.get(
                NOMINATIM_URL,
                params={"q": address, "format": "json", "limit": 1},
            )
            response.raise_for_status()
            results = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            log.debug("nominatim error for %r: %s", address, exc)
            return GeocodeResult(query=address, found=False, provider="nominatim")

        if not results:
            return GeocodeResult(query=address, found=False, provider="nominatim")

        best = results[0]
        return GeocodeResult(
            query=address,
            found=True,
            provider="nominatim",
            latitude=float(best["lat"]),
            longitude=float(best["lon"]),
            matched_address=best.get("display_name"),
        )

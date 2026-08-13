"""Legistar ingest — the hybrid client.

Most Legistar cities expose a free, keyless JSON API at webapi.legistar.com.
Some block it (verified: NYC and Philadelphia return 403, Chicago returns 500),
so those fall back to HTML scraping via `scraper-legistar`.

Every response is cached to disk on first fetch (PROTOCOLS.md P4).
"""

from __future__ import annotations

import logging
from datetime import datetime

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..cache import DiskCache
from ..models import AgendaItem, Attachment, Meeting, Stage
from .sections import assign_stages

log = logging.getLogger(__name__)

BASE_URL = "https://webapi.legistar.com/v1"

# Some Legistar tenants reject requests without a browser-ish User-Agent.
HEADERS = {
    "User-Agent": "docket-hackathon/0.1 (+https://github.com/sahitya1179/docket)",
    "Accept": "application/json",
}

# Cities verified to block the JSON API (tested 2026-08-13).
API_BLOCKED = {"nyc", "phila", "chicago"}


class LegistarAPIUnavailable(RuntimeError):
    """The JSON API refused us for this city — use the scraper fallback."""


class LegistarClient:
    """Reads meetings and agenda items for one Legistar city."""

    def __init__(self, city: str, timeout: float = 30.0) -> None:
        self.city = city.lower()
        self.cache = DiskCache(f"legistar/{self.city}")
        self._client = httpx.Client(headers=HEADERS, timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> LegistarClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ---------------------------------------------------------------- fetching

    @retry(
        retry=retry_if_exception_type(httpx.TransportError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=8),
        reraise=True,
    )
    def _get(self, path: str, params: dict | None = None) -> list[dict]:
        url = f"{BASE_URL}/{self.city}/{path}"
        cache_key = f"{url}?{sorted((params or {}).items())}"

        cached = self.cache.get(cache_key)
        if cached is not None:
            log.debug("cache hit: %s", path)
            return cached

        response = self._client.get(url, params=params)
        if response.status_code in (401, 403, 500):
            raise LegistarAPIUnavailable(
                f"{self.city}: JSON API returned {response.status_code}. "
                "Use the scraper fallback for this city."
            )
        response.raise_for_status()

        data = response.json()
        self.cache.set(cache_key, data)
        return data

    # ------------------------------------------------------------------ public

    def get_meetings(self, limit: int = 20) -> list[Meeting]:
        """Most recent meetings first, without their agenda items."""
        rows = self._get(
            "events",
            {"$top": limit, "$orderby": "EventDate desc"},
        )
        return [self._to_meeting(row) for row in rows]

    def get_agenda_items(self, event_id: int) -> list[AgendaItem]:
        """Every agenda line for one meeting, including procedural boilerplate.

        Filtering happens downstream in `ingest.triage` so the raw record stays
        auditable — a brief must be traceable to what the city actually published.
        """
        rows = self._get(
            f"events/{event_id}/eventitems",
            {"AgendaNote": 1, "MinutesNote": 1, "Attachments": 1},
        )
        return parse_agenda_items(rows, self.city, event_id)

    def get_meeting_with_items(self, event_id: int) -> Meeting:
        meetings = {m.event_id: m for m in self.get_meetings(limit=100)}
        meeting = meetings.get(event_id) or Meeting(event_id=event_id, city=self.city)
        meeting.items = self.get_agenda_items(event_id)
        return meeting

    # ------------------------------------------------------------ normalizing

    def _to_meeting(self, row: dict) -> Meeting:
        return Meeting(
            event_id=row["EventId"],
            city=self.city,
            date=_parse_date(row.get("EventDate")),
            body_name=_clean(row.get("EventBodyName")),
            agenda_url=row.get("EventAgendaFile") or None,
            minutes_url=row.get("EventMinutesFile") or None,
        )


# --------------------------------------------------------------------- parsing


def parse_agenda_items(rows: list[dict], city: str, event_id: int) -> list[AgendaItem]:
    """Turn raw Legistar rows into typed items with stages assigned.

    Split out from the client so tests can run against committed fixtures with
    no network access.
    """
    items = [_to_item(row, city, event_id) for row in rows]
    # Stage comes from the section an item sits under, not its own wording.
    return assign_stages(items)


def _to_item(row: dict, city: str, event_id: int) -> AgendaItem:
    title = _clean(row.get("EventItemTitle")) or ""
    return AgendaItem(
        id=f"{city}-{row['EventItemId']}",
        city=city,
        event_id=event_id,
        agenda_number=_clean(row.get("EventItemAgendaNumber")),
        matter_file=_clean(row.get("EventItemMatterFile")),
        title=title,
        action_name=_clean(row.get("EventItemActionName")),
        stage=infer_stage(title, row.get("EventItemActionName")),
        attachments=_attachments(row),
    )


# --------------------------------------------------------------------- helpers


def _clean(value: str | None) -> str | None:
    """Legistar pads fields with whitespace and returns empty strings for null."""
    if value is None:
        return None
    cleaned = " ".join(value.split())
    return cleaned or None


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _attachments(row: dict) -> list[Attachment]:
    # Field name varies across Legistar tenants; check the known spellings.
    raw = (
        row.get("EventItemMatterAttachments")
        or row.get("EventItemAttachments")
        or []
    )
    out = []
    for att in raw:
        if isinstance(att, dict) and att.get("MatterAttachmentHyperlink"):
            out.append(
                Attachment(
                    name=_clean(att.get("MatterAttachmentName")) or "attachment",
                    url=att["MatterAttachmentHyperlink"],
                )
            )
    return out


def infer_stage(title: str, action_name: str | None) -> Stage:
    """First-pass structural guess. The LLM extractor refines this in Phase 2."""
    haystack = f"{title} {action_name or ''}".lower()

    if "public hearing" in haystack:
        return Stage.PUBLIC_HEARING
    if "consent" in haystack:
        return Stage.CONSENT
    if any(k in haystack for k in ("informational report", "receive and file")):
        return Stage.INFORMATIONAL
    if any(k in haystack for k in ("ordinance", "resolution", "motion", "adopt")):
        return Stage.ACTION
    return Stage.UNKNOWN

"""Boilerplate triage — the cheap filter that runs before any model call.

An Oakland council agenda returns ~78 "items", but a meaningful share are
procedural: Zoom dial-in instructions, definitions of terms, roll call, ADA
notices, section headers, adjournment. Sending those to a model wastes tokens on
every nightly run.

**The signal is the matter file.** Verified against Oakland event 9560: all 61
items carrying a matter file number (e.g. `26-0889`) are real legislative
business; all 17 without one are procedural. Legistar assigns a matter file when
an item is an actual legislative matter, so this is a structural property of the
system rather than a guess about wording.

Items dropped here are returned alongside the kept ones so a drop is always
auditable — a false drop is otherwise invisible, and invisible failures are the
ones that sink this project.
"""

from __future__ import annotations

from ..models import AgendaItem

# Phrases that only ever appear in procedural text. Used as a secondary check
# for cities whose Legistar tenant is less disciplined about matter files.
BOILERPLATE_MARKERS = (
    "public participation",
    "definition of terms",
    "definitions of terms",
    "roll call",
    "call to order",
    "adjournment",
    "open forum",
    "americans with disabilities act",
    "zoom.us",
    "speaker card",
    "ecomment",
    "hanging of banners",
    "council acknowledgments",
)


def is_boilerplate(item: AgendaItem) -> bool:
    """True when an item is procedural rather than votable business.

    Primary rule: no matter file → not a legislative matter. Section headers
    ("CONSENT CALENDAR (CC) ITEMS:") are caught by this too, which is correct —
    they organize the agenda, they aren't voted on.
    """
    if item.matter_file:
        return False

    return True


def looks_procedural(item: AgendaItem) -> bool:
    """Keyword check, kept separate from the matter-file rule.

    Used to sanity-check the primary rule on a new city: if a city's items lack
    matter files but don't match these markers, the matter-file assumption
    doesn't hold there and needs re-verifying before trusting the pipeline.
    """
    haystack = item.title.lower()
    return any(marker in haystack for marker in BOILERPLATE_MARKERS)


def triage(items: list[AgendaItem]) -> tuple[list[AgendaItem], list[AgendaItem]]:
    """Split into (kept, dropped). Both returned so drops stay auditable."""
    kept, dropped = [], []
    for item in items:
        (dropped if is_boilerplate(item) else kept).append(item)
    return kept, dropped

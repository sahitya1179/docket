"""Section-aware stage assignment.

Oakland's agenda is hierarchical, and the hierarchy is encoded in the agenda
numbers. A bare integer is a section header; dotted children belong to it:

    6     CONSENT CALENDAR (CC) ITEMS:            <- header
    6.1   Approval Of The Draft Minutes...        <- consent item
    6.2   Declaration Of A Local Emergency...     <- consent item

So an item's stage comes from the section it sits under, not from keywords in
its own title. This matters: keyword matching reads "ACTION ON OTHER NON-CONSENT
CALENDAR ITEMS:" as a consent section because the word is a substring.

Consent items are the point of this whole project — they pass in one block with
no discussion unless someone pulls them — so getting this classification right
is load-bearing, not cosmetic.
"""

from __future__ import annotations

import re

from ..models import AgendaItem, Stage

_SECTION_NUMBER = re.compile(r"^\d+$")

# Order matters: NON-CONSENT must be tested before CONSENT.
_HEADER_PATTERNS: tuple[tuple[str, Stage], ...] = (
    ("non-consent", Stage.ACTION),
    ("public hearing", Stage.PUBLIC_HEARING),
    ("consent calendar", Stage.CONSENT),
    ("consent agenda", Stage.CONSENT),
    ("informational", Stage.INFORMATIONAL),
    ("ceremonial", Stage.INFORMATIONAL),
)


def is_section_header(item: AgendaItem) -> bool:
    """A header numbers itself with a bare integer and carries no matter file."""
    return (
        item.matter_file is None
        and item.agenda_number is not None
        and bool(_SECTION_NUMBER.match(item.agenda_number))
    )


def stage_from_header(title: str) -> Stage | None:
    haystack = title.lower()
    for needle, stage in _HEADER_PATTERNS:
        if needle in haystack:
            return stage
    return None


def assign_stages(items: list[AgendaItem]) -> list[AgendaItem]:
    """Propagate each section header's stage down to its dotted children.

    Items are returned in place with `stage` set. Anything that doesn't sit
    under a recognizable header keeps whatever the per-item guess produced.
    """
    section_stages: dict[str, Stage] = {}

    # First pass: find the headers.
    for item in items:
        if is_section_header(item):
            stage = stage_from_header(item.title)
            if stage is not None:
                section_stages[item.agenda_number] = stage  # type: ignore[index]
            # A header organizes the agenda; it is never itself voted on. Clear
            # any per-item keyword guess so it can't be counted as real business
            # — "Modifications To The Agenda ... Consent Calendar ..." otherwise
            # reads as a consent item.
            item.stage = Stage.UNKNOWN

    # Second pass: children inherit from their parent section.
    for item in items:
        if not item.agenda_number or "." not in item.agenda_number:
            continue
        parent = item.agenda_number.split(".", 1)[0]
        if parent in section_stages:
            item.stage = section_stages[parent]

    # Third pass: a stage only means something for votable business. Procedural
    # text keeps no stage, so it can never be counted as an agenda item —
    # "Approval of the Consent Agenda" otherwise keyword-matches into the
    # consent count despite being a procedural line, not a matter.
    for item in items:
        if not item.is_substantive:
            item.stage = Stage.UNKNOWN

    return items

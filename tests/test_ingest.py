"""Ingest tests — offline, against a committed fixture of real Oakland data.

The fixture is the raw Legistar response for Oakland event 9560 (a concurrent
ORSA / City Council meeting, July 21 2026). Real data, no network, no model.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from docket.ingest import (
    assign_stages,
    is_section_header,
    looks_procedural,
    parse_agenda_items,
    stage_from_header,
    triage,
)
from docket.models import Stage

FIXTURE = Path(__file__).parent / "fixtures" / "oakland_9560_eventitems.json"


@pytest.fixture(scope="module")
def items():
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return parse_agenda_items(rows, city="oakland", event_id=9560)


# ------------------------------------------------------------------- ingestion


def test_fixture_parses_every_row(items):
    assert len(items) == 78, "Oakland 9560 is known to have 78 agenda rows"


def test_every_item_has_a_title(items):
    assert all(item.title for item in items)


# --------------------------------------------------------------------- triage


def test_triage_splits_substantive_from_procedural(items):
    kept, dropped = triage(items)
    assert len(kept) == 61
    assert len(dropped) == 17
    assert len(kept) + len(dropped) == len(items)


def test_everything_kept_has_a_matter_file(items):
    kept, _ = triage(items)
    assert all(item.matter_file for item in kept)


def test_nothing_dropped_has_a_matter_file(items):
    """The failure mode with no downstream recovery is dropping real business."""
    _, dropped = triage(items)
    assert not any(item.matter_file for item in dropped)


def test_dropped_items_are_recognizably_procedural(items):
    """Sanity-check the matter-file rule against independent keyword evidence.

    If this ratio collapses on a new city, the matter-file assumption doesn't
    hold there and the pipeline needs re-verifying before it can be trusted.
    """
    _, dropped = triage(items)
    procedural = [i for i in dropped if looks_procedural(i)]
    assert len(procedural) / len(dropped) >= 0.5


# ------------------------------------------------------------------- sections


def test_section_headers_are_bare_integers(items):
    headers = [i for i in items if is_section_header(i)]
    assert headers, "expected at least one section header"
    assert all("." not in h.agenda_number for h in headers)


def test_non_consent_header_is_not_read_as_consent():
    """Regression: substring matching classified 'NON-CONSENT' as consent."""
    assert stage_from_header("ACTION ON OTHER NON-CONSENT CALENDAR ITEMS:") is Stage.ACTION
    assert stage_from_header("CONSENT CALENDAR (CC) ITEMS:") is Stage.CONSENT


def test_consent_items_inherit_stage_from_their_header(items):
    """6.x items sit under 'CONSENT CALENDAR (CC) ITEMS:' and must inherit it."""
    consent = [i for i in items if i.stage is Stage.CONSENT]
    assert len(consent) == 24
    assert all(i.agenda_number and i.agenda_number.startswith("6.") for i in consent)


def test_section_headers_carry_no_stage(items):
    """A header organizes the agenda and is never voted on, so it has no stage.

    Regression: 'Modifications To The Agenda ... Consent Calendar ...' was being
    keyword-matched into the consent count.
    """
    headers = [i for i in items if is_section_header(i)]
    assert all(h.stage is Stage.UNKNOWN for h in headers)


def test_consent_items_are_the_headline_signal(items):
    """Consent items pass in one block with no discussion — the whole premise."""
    kept, _ = triage(items)
    consent = [i for i in kept if i.stage is Stage.CONSENT]
    assert len(consent) >= 20, "a typical Oakland meeting buries 20+ items in consent"


def test_assign_stages_is_idempotent(items):
    before = [i.stage for i in items]
    after = [i.stage for i in assign_stages(items)]
    assert before == after

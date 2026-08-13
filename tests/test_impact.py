"""Impact-scoring tests — real agenda titles from Oakland.

These assert *behaviour the product depends on*, not the score of the baseline
on labeled data. The baseline's accuracy is measured by scripts/eval.py against
the human holdout, and deliberately not asserted here: the rules were written
after labeling the training set, so a test pinning that number would be pinning
a contaminated result.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from docket.impact import DEMO_ORG, dedupe_by_matter, duplicate_counts, score_item
from docket.ingest import parse_agenda_items, triage
from docket.models import AgendaItem, Stage

FIXTURE = Path(__file__).parent / "fixtures" / "oakland_9560_eventitems.json"


def item(
    title: str, stage: Stage = Stage.ACTION, matter: str | None = "26-0001"
) -> AgendaItem:
    return AgendaItem(
        id="test-1", city="oakland", event_id=1, title=title, stage=stage, matter_file=matter
    )


@pytest.fixture(scope="module")
def real_items():
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    kept, _ = triage(parse_agenda_items(rows, city="oakland", event_id=9560))
    return kept


# --------------------------------------------------------------------- scoring


def test_parcel_sale_scores_relevant():
    score = score_item(item("Subject: Sale Of 319 Chester Street From: Housing"), DEMO_ORG)
    assert score.relevant


def test_planning_code_change_scores_relevant():
    """No address, but it changes what neighbours may build. Mission-match."""
    title = (
        "Subject: 2026 Miscellaneous Planning Code Amendments ... Updating The "
        "Accessory Dwelling Unit Regulations For Consistency With State Law"
    )
    assert score_item(item(title), DEMO_ORG).relevant


def test_routine_minutes_score_irrelevant():
    assert not score_item(
        item("Approval Of The Draft Minutes From July 7, 2026"), DEMO_ORG
    ).relevant


def test_personnel_items_score_irrelevant():
    for title in (
        "Subject: Severance Package ... Severance Agreement Between The City "
        "And Jestin Johnson",
        "Subject: Appointment To Head Start Advisory Board",
    ):
        assert not score_item(item(title), DEMO_ORG).relevant


def test_recurring_emergency_renewal_scores_irrelevant():
    """Renewed every meeting; alerting each time trains users to ignore alerts."""
    title = (
        "Subject: Declaration Of A Local Emergency On Homelessness From: Office Of The "
        "Council President Recommendation: Adopt A Resolution Renewing And Continuing "
        "The City Council's Declaration"
    )
    assert not score_item(item(title), DEMO_ORG).relevant


def test_every_decision_carries_a_reason():
    """An alert a volunteer cannot act on is worse than no alert."""
    score = score_item(item("Subject: Sale Of 319 Chester Street"), DEMO_ORG)
    assert score.reasons
    assert all(isinstance(r, str) and r for r in score.reasons)


def test_consent_calendar_breaks_ties_upward():
    """A consequential item hiding on consent is the highest-value alert."""
    title = "Subject: Final Tract Map No. 8697 Located At 8750 Mountain Boulevard"
    as_consent = score_item(item(title, stage=Stage.CONSENT), DEMO_ORG)
    as_action = score_item(item(title, stage=Stage.ACTION), DEMO_ORG)
    assert as_consent.value >= as_action.value


def test_large_sums_alone_do_not_make_an_item_relevant():
    """Money is an amplifier, not a trigger — otherwise every contract alerts."""
    title = (
        "Subject: Collision Repair Contracts ... Not-To-Exceed One Million "
        "Four Hundred Thousand Dollars ($1,400,000)"
    )
    assert not score_item(item(title), DEMO_ORG).relevant


def test_scores_every_real_item_without_crashing(real_items):
    scores = [score_item(i, DEMO_ORG) for i in real_items]
    assert len(scores) == len(real_items)


def test_baseline_does_not_flag_everything(real_items):
    """A classifier that says yes to all 61 items has filtered nothing."""
    flagged = [i for i in real_items if score_item(i, DEMO_ORG).relevant]
    share = len(flagged) / len(real_items)
    assert 0.15 <= share <= 0.75, f"baseline flagged {share:.0%} of real items"


# ---------------------------------------------------------------------- dedupe


def test_dedupe_collapses_repeated_matters():
    items = [
        item("Broadway Streetscape Improvements", matter="26-0100"),
        item("Broadway Streetscape Improvements", matter="26-0100"),
        item("Sale Of 319 Chester Street", matter="26-0200"),
    ]
    assert len(dedupe_by_matter(items)) == 2


def test_dedupe_keeps_items_without_a_matter_file():
    items = [
        item("Something procedural", matter=None),
        item("A real matter", matter="26-0300"),
    ]
    assert len(dedupe_by_matter(items)) == 2


def test_duplicate_counts_reports_only_repeats():
    items = [
        item("A", matter="26-0100"),
        item("A again", matter="26-0100"),
        item("B", matter="26-0200"),
    ]
    assert duplicate_counts(items) == {"26-0100": 2}


def test_single_meeting_has_no_duplicate_matters(real_items):
    """Duplication happens across meetings, not within one."""
    assert duplicate_counts(real_items) == {}

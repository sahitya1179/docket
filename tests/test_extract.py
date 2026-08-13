"""Extraction tests — real strings taken from Oakland 9560 agenda titles."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from docket.extract import (
    candidate_places,
    extract_amounts,
    has_geographic_reference,
    largest_amount,
    validate_candidates,
)
from docket.ingest import parse_agenda_items, triage

FIXTURE = Path(__file__).parent / "fixtures" / "oakland_9560_eventitems.json"


@pytest.fixture(scope="module")
def substantive():
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    kept, _ = triage(parse_agenda_items(rows, city="oakland", event_id=9560))
    return kept


# --------------------------------------------------------------------- amounts


@pytest.mark.parametrize(
    "text,expected",
    [
        ("A total of $45,000.00 for the year", [45000.0]),
        ("Not To Exceed $202,500", [202500.0]),
        ("In The Amount Of $12,399,039", [12399039.0]),
        ("$1.2 million grant", [1_200_000.0]),
        ("$3 billion bond", [3_000_000_000.0]),
        ("Between $490,000 and $510,000", [490000.0, 510000.0]),
        ("No money mentioned here", []),
    ],
)
def test_amount_shapes(text, expected):
    assert extract_amounts(text) == expected


def test_largest_amount_picks_the_headline_figure():
    text = "Award A Contract For $45,000 With A Contingency Of $1.2 million"
    assert largest_amount(text) == 1_200_000.0


def test_largest_amount_is_none_when_there_is_no_money():
    assert largest_amount("Reaffirming The Sanctuary City Policy") is None


def test_amounts_appear_across_real_agenda_items(substantive):
    """Measured: 24 of 61 substantive items carry a dollar figure."""
    with_money = [i for i in substantive if extract_amounts(i.title)]
    assert 15 <= len(with_money) <= 40


# ---------------------------------------------------------------------- places


def test_numbered_address_is_extracted():
    title = "Subject: Sale Of 319 Chester Street From: Housing And Community Development"
    assert "319 Chester Street" in candidate_places(title)


def test_article_words_are_stripped_from_street_names():
    """Regression: regex captured 'In The Wood Street' and 'At The Grand Avenue'."""
    assert candidate_places("Activities In The Wood Street D-WS-9 Zone") == ["Wood Street"]
    assert candidate_places("Improvements At The Grand Avenue Corridor") == ["Grand Avenue"]


def test_numbered_address_subsumes_the_bare_street_name():
    """'319 Chester Street' and 'Chester Street' are one place, not two."""
    places = candidate_places("The Sale Of A City-Owned Parcel At 319 Chester Street")
    assert places == ["319 Chester Street"]


def test_neighborhoods_are_recognized():
    assert "West Oakland" in candidate_places("The Alliance For West Oakland Development")
    assert "Fruitvale" in candidate_places("AC Transit Fruitvale Corridor Project")


def test_bare_suffix_is_not_a_place():
    assert candidate_places("Street improvements generally") == []


def test_citywide_items_yield_no_place():
    """These must fall through to mission-match, not proximity."""
    for title in (
        "Reaffirming The City Of Oakland's Sanctuary City Policy",
        "Amendment To Ordinance No. 12187 C.M.S. (The Salary Ordinance)",
    ):
        assert not has_geographic_reference(title)


def test_validated_candidates_are_geocoder_ready():
    assert validate_candidates(["319 Chester Street"]) == ["319 Chester Street, Oakland, CA"]


def test_geographic_coverage_matches_what_was_measured(substantive):
    """~18% of substantive items reference a place. Guards the pitch claim.

    If this drifts far, the two-filter design in DECISIONS.md needs revisiting —
    the honest claim depends on this number.
    """
    with_place = [i for i in substantive if has_geographic_reference(i.title)]
    share = len(with_place) / len(substantive)
    assert 0.10 <= share <= 0.40, f"geographic share moved to {share:.0%}"

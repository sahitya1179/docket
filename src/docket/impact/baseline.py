"""A transparent, rules-only relevance classifier.

This exists to be beaten. Before spending model calls on impact scoring, we
need to know what a few honest heuristics achieve on the same data — otherwise
an LLM scoring 80% looks impressive without anyone knowing that keyword matching
already scored 78%.

It also keeps the pipeline runnable end to end while Bedrock access is pending,
and it stays in the final system as a cheap pre-filter and a fallback when the
model is unavailable.

Signals come from labeling 84 real items (see LABELING-GUIDE.md). The strongest
by far: of 16 items where place detection fired, 14 were labeled relevant.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..extract import candidate_places, largest_amount
from ..models import AgendaItem, Stage
from .org import OrgProfile

# Phrases that reliably mark an item as internal or procedural. Matched against
# the whole title, so they are written to be specific rather than clever.
NEGATIVE_PATTERNS: tuple[tuple[str, float], ...] = (
    (r"approval of the draft minutes", -3.0),
    (r"determination of schedule", -3.0),
    (r"review of draft agendas", -3.0),
    (r"\bseverance\b", -2.5),
    (r"employment agreement|compensation package", -2.5),
    (r"salary ordinance|job classification", -2.5),
    (r"confirming (?:the )?(?:the mayor's )?appointment|appointment to the", -2.5),
    (r"selection panel|slate of two commissioners", -2.5),
    (r"renewing (?:and continuing )?the city council's declaration", -2.5),
    (r"grand jury report", -2.5),
    (r"compromise and settle|city attorney file no", -2.0),
    (r"in support of (?:assembly bill|senate bill|ab|sb)\s*\d+", -2.0),
    (r"strategic plan one-year update|roadmap to fiscal health", -2.0),
    (r"reimburse certain expenditures", -1.5),
    (r"memorandum of understanding with the (?:california|bay area)", -1.5),
)

# Phrases that mark an item as something a neighborhood group shows up for.
POSITIVE_PATTERNS: tuple[tuple[str, float], ...] = (
    (r"planning code|zoning|accessory dwelling|subdivision map|tract map", 3.0),
    (r"\bsale of\b|city-owned parcel|tax sale|ground lease", 3.0),
    (r"streetscape|street connection|signal priority|wayfinding", 2.5),
    (r"encampment|homeless", 2.0),
    (r"code enforcement|vacant property|blight", 2.0),
    (r"general municipal election|ballot|electors of the city", 2.0),
    (r"surveillance technolog|license plate reader", 2.0),
    (r"paratransit|supportive housing|community services block grant", 1.5),
    (r"\bmural\b|\bpark\b|\blibrary\b", 1.5),
    # "collision" alone matches "Collision Repair Contracts" — body-shop work on
    # the city fleet, not street safety. Require the traffic sense explicitly.
    (r"traffic safety|safe oakland streets|traffic collision|vision zero", 1.5),
)

# Money only matters above a threshold, and only alongside something local.
LARGE_AMOUNT = 1_000_000.0

# Chosen by sweeping the training set — which the rules were written against, so
# treat it as provisional. Re-check on the human holdout before trusting it.
DEFAULT_THRESHOLD = 1.5


@dataclass
class Score:
    """A relevance decision that can explain itself.

    The reasons list is not decoration — an unexplained alert is one a volunteer
    cannot act on, and the same reasons feed the drafted brief later.
    """

    value: float
    relevant: bool
    reasons: list[str] = field(default_factory=list)


def score_item(
    item: AgendaItem, org: OrgProfile, threshold: float = DEFAULT_THRESHOLD
) -> Score:
    title = item.title
    lowered = title.lower()
    total = 0.0
    reasons: list[str] = []

    # 1. Geography — the strongest single signal in the labeled data.
    places = candidate_places(title)
    if places:
        total += 2.5
        reasons.append(f"names a specific place ({places[0]})")

    if org.mentions_our_area(title):
        total += 2.0
        reasons.append("names an area the group covers")

    # 2. Subject matter.
    for pattern, weight in POSITIVE_PATTERNS:
        if re.search(pattern, lowered):
            total += weight
            reasons.append(f"subject matter: {pattern.split('|')[0].strip(chr(92) + 'b')}")
            break

    # 3. Mission match against the group's own stated interests.
    hits = [i for i in org.interests if i.lower() in lowered]
    if hits:
        total += 1.0
        reasons.append(f"matches stated interest: {hits[0]}")

    # 4. Money, but only when something else already ties it here.
    amount = largest_amount(title)
    if amount and amount >= LARGE_AMOUNT and total > 0:
        total += 1.0
        reasons.append(f"large sum (${amount:,.0f})")

    # 5. Procedural and internal business.
    for pattern, weight in NEGATIVE_PATTERNS:
        if re.search(pattern, lowered):
            total += weight
            reasons.append("routine or internal business")
            break

    # 6. Consent calendar tiebreak. A consequential item hiding on consent is
    # the highest-value alert this product can send, so borderline consent
    # items get nudged over rather than under.
    if item.stage is Stage.CONSENT and 0 < total < threshold:
        total += 0.5
        reasons.append("on the consent calendar, so it would pass without discussion")

    return Score(value=total, relevant=total >= threshold, reasons=reasons)


def classify(
    items: list[AgendaItem], org: OrgProfile, threshold: float = DEFAULT_THRESHOLD
) -> list[Score]:
    return [score_item(i, org, threshold) for i in items]

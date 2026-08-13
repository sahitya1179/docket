"""Dollar amounts from agenda prose.

Unlike place references, money in agenda text is genuinely well-patterned:
52 matches across 24 of the 61 substantive items in Oakland 9560. So this stays
on regex rather than costing a model call on every item, every night.

Amounts matter for impact scoring in their own right — a neighborhood group
cares more about a $12M contract than a $450 reimbursement, independent of where
it lands.
"""

from __future__ import annotations

import re

# $45,000.00 · $202,500 · $12,399,039 · $1.2 million · $3 billion
_AMOUNT = re.compile(
    r"\$\s?(?P<num>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"(?:\s*(?P<scale>million|billion|thousand))?",
    re.IGNORECASE,
)

_SCALES = {"thousand": 1_000, "million": 1_000_000, "billion": 1_000_000_000}


def extract_amounts(text: str) -> list[float]:
    """Every dollar figure in `text`, normalized to whole dollars.

    Returns them in the order they appear, duplicates included — repetition is
    meaningful (an amount restated in the recommendation is usually the headline
    figure), and de-duplicating here would throw that away.
    """
    out: list[float] = []
    for match in _AMOUNT.finditer(text):
        raw = match.group("num").replace(",", "")
        try:
            value = float(raw)
        except ValueError:  # pragma: no cover — regex shouldn't allow this
            continue

        scale = match.group("scale")
        if scale:
            value *= _SCALES[scale.lower()]
        out.append(value)
    return out


def largest_amount(text: str) -> float | None:
    """The headline figure, or None. Used as an impact-scoring signal."""
    amounts = extract_amounts(text)
    return max(amounts) if amounts else None

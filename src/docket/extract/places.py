"""Place references from agenda prose.

Measured on Oakland 9560: only 18% of substantive items carry any geographic
reference, and regex alone extracts them badly — it captured "In The Wood
Street", "For The Fruitvale Avenue" and "At The Grand Avenue", dragging article
words into street names and producing strings no geocoder will resolve.

So this is a two-stage design:

1. **Candidate generation (here, regex).** Cheap, deterministic, testable
   offline. Over-generates on purpose — recall matters more than precision at
   this stage, because a place the candidate pass misses can never be recovered.
2. **Validation (LLM, `validate_candidates`).** Trims the article words, drops
   false positives, and resolves the ones regex cannot see at all. Only runs on
   items that produced candidates, so most items cost nothing.

Stage 2 needs Bedrock access. Until then `validate_candidates` falls back to a
deterministic cleanup so the pipeline runs end to end.
"""

from __future__ import annotations

import re

# Leading words that regex keeps gluing onto street names.
_LEADING_NOISE = re.compile(
    r"^(?:in|on|at|for|to|of|the|and|from|between|near|along)\s+",
    re.IGNORECASE,
)

_SUFFIXES = (
    "Street",
    "St",
    "Avenue",
    "Ave",
    "Road",
    "Rd",
    "Boulevard",
    "Blvd",
    "Way",
    "Drive",
    "Dr",
    "Place",
    "Pl",
    "Court",
    "Ct",
    "Lane",
    "Ln",
    "Plaza",
    "Parkway",
    "Pkwy",
    "Circle",
    "Terrace",
)
_SUFFIX_RE = "|".join(_SUFFIXES)

# 319 Chester Street · 8750 Mountain Boulevard
_NUMBERED = re.compile(
    rf"\b(?P<text>\d{{1,5}}\s+[A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){{0,3}}"
    rf"\s+(?:{_SUFFIX_RE})\b)"
)

# Chester Street · Mountain Boulevard · Grand Avenue (no house number)
_NAMED = re.compile(
    rf"\b(?P<text>[A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){{0,2}}"
    rf"\s+(?:{_SUFFIX_RE})\b)"
)

_NEIGHBORHOOD = re.compile(
    r"\b(?P<text>(?:West|East|North|South|Downtown|Uptown)\s+Oakland"
    r"|Chinatown|Fruitvale|Rockridge|Temescal|Jack London(?:\s+Square)?"
    r"|Lake Merritt|Coliseum)\b"
)


def _clean(candidate: str) -> str:
    prior = None
    text = candidate.strip()
    while text != prior:
        prior = text
        text = _LEADING_NOISE.sub("", text).strip()
    return text


def candidate_places(text: str) -> list[str]:
    """Possible place references, most specific first, de-duplicated.

    Over-generates deliberately — validation is stage two's job.
    """
    seen: dict[str, None] = {}

    for pattern in (_NUMBERED, _NAMED, _NEIGHBORHOOD):
        for match in pattern.finditer(text):
            cleaned = _clean(match.group("text"))
            # A bare suffix ("Street") survives cleanup but means nothing.
            if cleaned and cleaned not in _SUFFIXES:
                seen.setdefault(cleaned, None)

    # A numbered address subsumes the bare street name it contains.
    candidates = list(seen)
    subsumed = {
        shorter
        for longer in candidates
        for shorter in candidates
        if shorter != longer and longer.endswith(shorter)
    }
    return [c for c in candidates if c not in subsumed]


def has_geographic_reference(text: str) -> bool:
    """Cheap gate — is it worth spending a model call on this item at all?"""
    return bool(candidate_places(text))


def validate_candidates(candidates: list[str], city: str = "Oakland, CA") -> list[str]:
    """Stage two. Deterministic for now; becomes an LLM call once Bedrock lands.

    Returns geocoder-ready strings. The fallback keeps the pipeline runnable and
    is deliberately conservative — it cleans, it does not invent.
    """
    return [f"{c}, {city}" for c in candidates]

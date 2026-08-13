"""Collapse repeated matters.

Discovered while labeling: the same matter appears at committee and again at
council, sometimes three times. Broadway Streetscape appeared 3x across the
124-item sample, the BAAQMD grant 3x, the Grand Jury response 3x.

Alerting three times on one decision is how you train someone to ignore alerts,
so items are grouped by `matter_file` — Legistar's stable identifier for a
legislative matter — and only the most recent occurrence is surfaced.
"""

from __future__ import annotations

from ..models import AgendaItem


def dedupe_by_matter(items: list[AgendaItem]) -> list[AgendaItem]:
    """One item per matter file, keeping the last occurrence seen.

    Items without a matter file pass through untouched: they have no stable
    identity to group on, and triage should have removed them already.
    """
    by_matter: dict[str, AgendaItem] = {}
    passthrough: list[AgendaItem] = []

    for item in items:
        if not item.matter_file:
            passthrough.append(item)
        else:
            by_matter[item.matter_file] = item

    return [*by_matter.values(), *passthrough]


def duplicate_counts(items: list[AgendaItem]) -> dict[str, int]:
    """How many times each matter appears. Used to report the collapse ratio."""
    counts: dict[str, int] = {}
    for item in items:
        if item.matter_file:
            counts[item.matter_file] = counts.get(item.matter_file, 0) + 1
    return {k: v for k, v in counts.items() if v > 1}

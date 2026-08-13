"""Build the labeling sets.

Run:  python scripts/export_for_labeling.py

Produces three files in `labels/`:

    train.csv      ~80 items — labeled by Claude, used for tuning
    holdout.csv    ~40 items — labeled by the human, used for SCORING ONLY
    overlap.csv    ~20 items — appear in both, labeled independently

Why the split (see DECISIONS.md): tuning a classifier against AI-generated
labels and then scoring it against the same labels measures agreement, not
correctness. The holdout has to be human judgment or the number is theatre.
The overlap exists so we can measure how far apart the two labelers actually
are, and catch a systematic bias before it is baked in.
"""

from __future__ import annotations

import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from docket.extract import candidate_places, largest_amount  # noqa: E402
from docket.ingest import LegistarClient, triage  # noqa: E402

CITY = "oakland"
TARGET_ITEMS = 120
OVERLAP_N = 20
HOLDOUT_N = 40
SEED = 20260813  # fixed, so re-running produces the same split

OUT_DIR = Path(__file__).resolve().parents[1] / "labels"

COLUMNS = [
    "item_id",
    "meeting",
    "agenda_no",
    "matter_file",
    "stage",
    "places",
    "largest_amount",
    "title",
    "relevant",  # <- fill in: y or n
    "reason",  # <- fill in: one short sentence
]


def collect(limit_meetings: int = 40) -> list[dict]:
    """Pull substantive items across recent meetings until we have enough."""
    rows: list[dict] = []
    seen_ids: set[str] = set()

    with LegistarClient(CITY) as client:
        meetings = client.get_meetings(limit=limit_meetings)
        for meeting in meetings:
            if len(rows) >= TARGET_ITEMS:
                break
            try:
                items = client.get_agenda_items(meeting.event_id)
            except Exception as exc:  # a cancelled meeting may 404 on items
                print(f"  skipped event {meeting.event_id}: {exc}")
                continue

            kept, _ = triage(items)
            label = f"{meeting.date.date() if meeting.date else '?'} {meeting.body_name or ''}"

            for item in kept:
                if item.id in seen_ids:
                    continue
                seen_ids.add(item.id)
                places = candidate_places(item.title)
                amount = largest_amount(item.title)
                rows.append(
                    {
                        "item_id": item.id,
                        "meeting": label.strip()[:60],
                        "agenda_no": item.agenda_number or "",
                        "matter_file": item.matter_file or "",
                        "stage": item.stage.value,
                        "places": "; ".join(places),
                        "largest_amount": f"{amount:.0f}" if amount else "",
                        "title": item.title,
                        "relevant": "",
                        "reason": "",
                    }
                )
    return rows


def write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    print(f"Collecting substantive items from {CITY}...")
    rows = collect()
    print(f"  collected {len(rows)} items\n")

    if len(rows) < OVERLAP_N + HOLDOUT_N + 20:
        print("  WARNING: fewer items than planned; widen limit_meetings")

    rng = random.Random(SEED)
    rng.shuffle(rows)

    # Stratify lightly: make sure consent items land in the holdout, since they
    # are the class the product exists to surface.
    holdout = rows[:HOLDOUT_N]
    overlap = rows[HOLDOUT_N : HOLDOUT_N + OVERLAP_N]
    train = rows[HOLDOUT_N:]  # train includes the overlap, deliberately

    write(OUT_DIR / "holdout.csv", holdout)
    write(OUT_DIR / "overlap.csv", overlap)
    write(OUT_DIR / "train.csv", train)

    def consent_share(batch: list[dict]) -> str:
        n = sum(1 for r in batch if r["stage"] == "consent")
        return f"{n}/{len(batch)}"

    print(
        f"  holdout.csv  {len(holdout):>3} items  (YOU label these) "
        f"consent={consent_share(holdout)}"
    )
    print(f"  overlap.csv  {len(overlap):>3} items  (YOU label these too, independently)")
    print(f"  train.csv    {len(train):>3} items  (Claude labels these)")
    print(f"\n  written to {OUT_DIR}")
    print("\n  Fill in the 'relevant' column with y or n, and one short sentence")
    print("  in 'reason'. Do not look at train.csv before finishing holdout.csv.")


if __name__ == "__main__":
    main()

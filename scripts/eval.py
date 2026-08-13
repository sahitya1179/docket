"""Score a relevance classifier against labeled data.

Run:  python scripts/eval.py                  # train set (Claude's labels)
      python scripts/eval.py --set holdout    # holdout (human labels) - THE number
      python scripts/eval.py --agreement      # how far apart the two labelers are

The holdout score is the only one that counts. The train score is a development
signal — tuning against it and then quoting it would be measuring agreement with
the labeler, not correctness. See DECISIONS.md.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from docket.impact import DEMO_ORG, score_item  # noqa: E402
from docket.models import AgendaItem, Stage  # noqa: E402

LABELS_DIR = ROOT / "labels"


@dataclass
class Metrics:
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.tn + self.fn

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def accuracy(self) -> float:
        return (self.tp + self.tn) / self.total if self.total else 0.0


def load(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(f"missing {path} — run scripts/export_for_labeling.py first")
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    labeled = [r for r in rows if r.get("relevant", "").strip().lower() in ("y", "n")]
    if not labeled:
        sys.exit(f"{path.name} has no labels yet — fill in the 'relevant' column")
    if len(labeled) < len(rows):
        print(f"  note: {len(rows) - len(labeled)} of {len(rows)} rows unlabeled, skipping\n")
    return labeled


def to_item(row: dict) -> AgendaItem:
    try:
        stage = Stage(row["stage"])
    except ValueError:
        stage = Stage.UNKNOWN
    return AgendaItem(
        id=row["item_id"],
        city="oakland",
        event_id=0,
        agenda_number=row["agenda_no"] or None,
        matter_file=row["matter_file"] or None,
        title=row["title"],
        stage=stage,
    )


def evaluate(rows: list[dict], threshold: float) -> tuple[Metrics, list[tuple[dict, bool]]]:
    m = Metrics()
    mistakes: list[tuple[dict, bool]] = []

    for row in rows:
        truth = row["relevant"].strip().lower() == "y"
        predicted = score_item(to_item(row), DEMO_ORG, threshold).relevant

        if predicted and truth:
            m.tp += 1
        elif predicted and not truth:
            m.fp += 1
            mistakes.append((row, True))
        elif not predicted and truth:
            m.fn += 1
            mistakes.append((row, False))
        else:
            m.tn += 1

    return m, mistakes


def report(name: str, m: Metrics) -> None:
    print(
        f"  {name:<10} n={m.total:<4} "
        f"precision={m.precision:.0%}  recall={m.recall:.0%}  "
        f"F1={m.f1:.0%}  accuracy={m.accuracy:.0%}"
    )
    print(f"             tp={m.tp} fp={m.fp} tn={m.tn} fn={m.fn}")


def agreement() -> None:
    """Compare the two labelers on the overlap set."""
    overlap = load(LABELS_DIR / "overlap.csv")
    train = {r["item_id"]: r for r in load(LABELS_DIR / "train.csv")}

    shared = [(r, train[r["item_id"]]) for r in overlap if r["item_id"] in train]
    if not shared:
        sys.exit("no shared items between overlap.csv and train.csv")

    agree = sum(
        1
        for human, claude in shared
        if human["relevant"].lower() == claude["relevant"].lower()
    )
    rate = agree / len(shared)

    print(f"\n  Labeler agreement: {agree}/{len(shared)} ({rate:.0%})\n")
    if rate < 0.75:
        print("  LOW AGREEMENT. Claude's training labels encode a different standard")
        print("  than yours. Re-read LABELING-GUIDE.md together before trusting the")
        print("  train set — the holdout score governs regardless.\n")

    for human, claude in shared:
        if human["relevant"].lower() != claude["relevant"].lower():
            print(f"  [{human['relevant']} vs {claude['relevant']}] {human['title'][:78]}")
            print(f"       you:    {human['reason'][:76]}")
            print(f"       claude: {claude['reason'][:76]}\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="train", choices=["train", "holdout", "overlap"])
    ap.add_argument("--threshold", type=float, default=1.0)
    ap.add_argument("--sweep", action="store_true", help="try a range of thresholds")
    ap.add_argument("--agreement", action="store_true")
    ap.add_argument("--errors", action="store_true", help="list misclassified items")
    args = ap.parse_args()

    if args.agreement:
        agreement()
        return

    rows = load(LABELS_DIR / f"{args.set}.csv")
    positives = sum(1 for r in rows if r["relevant"].lower() == "y")
    print(
        f"\n  BASELINE (rules only) on {args.set}: "
        f"{len(rows)} items, {positives} labeled relevant ({positives / len(rows):.0%})\n"
    )

    if args.sweep:
        for t in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
            m, _ = evaluate(rows, t)
            report(f"t={t}", m)
        return

    m, mistakes = evaluate(rows, args.threshold)
    report(args.set, m)

    if args.set == "train":
        print(
            "\n  ⚠ TRAIN SCORE IS CONTAMINATED — do not quote it anywhere.\n"
            "    The baseline rules were written after labeling these same items,\n"
            "    so they encode the labeler's decisions. This measures internal\n"
            "    consistency, not generalization. Expect the holdout to be lower;\n"
            "    the holdout is the only number that means anything."
        )

    if args.errors:
        print("\n  --- misclassified ---")
        for row, was_false_positive in mistakes:
            kind = "FP" if was_false_positive else "FN"
            print(f"  [{kind}] {row['title'][:80]}")


if __name__ == "__main__":
    main()

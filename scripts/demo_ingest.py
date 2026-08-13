"""Demo: what Docket sees when it reads one real Oakland council meeting.

Run:  python scripts/demo_ingest.py

This is the ingest layer end to end against live public data — no mocks. It is
also the shot worth filming: the consent-calendar count is the whole premise of
the project in one number.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from docket.ingest import LegistarClient, triage  # noqa: E402
from docket.models import Stage  # noqa: E402

CITY = "oakland"
EVENT_ID = 9560  # Concurrent ORSA / City Council meeting, 21 July 2026

BAR = "=" * 78


def main() -> None:
    print(BAR)
    print("  DOCKET — reading a real Oakland City Council agenda packet")
    print(BAR)

    with LegistarClient(CITY) as client:
        started = time.perf_counter()
        items = client.get_agenda_items(EVENT_ID)
        elapsed = (time.perf_counter() - started) * 1000

        kept, dropped = triage(items)

        print(f"\n  Source: Legistar public API — city '{CITY}', event {EVENT_ID}")
        print(f"  Fetched {len(items)} agenda rows in {elapsed:.0f} ms\n")

        print("  " + "-" * 74)
        print(f"  {len(dropped):>3} procedural rows discarded before any model call")
        print(f"  {len(kept):>3} real legislative matters kept")
        print("  " + "-" * 74)

        print("\n  Discarded (never reaches a model — saves tokens every night):")
        for item in dropped[:5]:
            print(f"      · {item.title[:66]}")
        print(f"      · ... and {len(dropped) - 5} more")

        counts: dict[str, int] = {}
        for item in kept:
            counts[item.stage.value] = counts.get(item.stage.value, 0) + 1

        print("\n  How the real matters break down:")
        for stage, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f"      {stage:<16} {n:>3}")

        consent = [i for i in kept if i.stage is Stage.CONSENT]
        print("\n" + BAR)
        print(f"  {len(consent)} ITEMS ARE ON THE CONSENT CALENDAR")
        print("  They pass in a single vote, with no discussion,")
        print("  unless one person asks for one to be pulled.")
        print(BAR)

        print("\n  A few of them:\n")
        for item in consent[:5]:
            print(f"   [{item.agenda_number}]  file {item.matter_file}")
            print(f"        {item.title[:70]}")

        print("\n  Nobody reads 800 pages in 72 hours. That is the problem.\n")


if __name__ == "__main__":
    main()

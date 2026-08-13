# NEXT — where the last session stopped

Updated at the end of every session, and immediately on hitting a rate limit
(PROTOCOLS.md P11).

---

**Last updated:** 2026-08-13
**Current phase:** Phase 1 — Data spine + eval
**Phase 1 exit condition:** `eval.py` prints a precision/recall score

## Done

**Phase 0**
- ✅ Repo, MIT license, `.gitignore`, README with prior-art positioning
- ✅ `pyproject.toml`, venv, Python 3.14.4
- ⬜ AgentCore template deploy — **blocked on AWS CLI + credentials**

**Phase 1**
- ✅ `docket.cache.DiskCache` — content-addressed, atomic writes
- ✅ `docket.models` — `AgendaItem`, `Meeting`, `Stage`, `GeocodeResult`
- ✅ `docket.ingest` — Legistar client, triage, section-aware stages
- ✅ `docket.geo` — Census → Nominatim fallback, rate limiter, haversine
- ✅ `scripts/demo_ingest.py` + `scripts/replay.html` (footage-ready)
- ✅ **26 tests passing offline**, ruff clean

## What the real data taught us

1. **Matter file marks real business.** 61 items with one are legislative
   matters; 17 without are procedural. Agenda numbers do NOT work as a signal —
   "Call To Order" is item 1.
2. **Oakland agendas are hierarchical.** Item `6` is the "CONSENT CALENDAR"
   header; `6.1`–`6.x` inherit from it. Keyword matching read "NON-CONSENT
   CALENDAR" as consent — the exact inverse of what this product detects.
3. **Stage is meaningful only for substantive items**, or procedural lines
   inflate the consent count.
4. **Census geocoding is fine for ordinary Oakland addresses** (`1 Broadway`,
   `3301 E 12th St` both resolve). It fails on **non-standard forms** — plazas
   and some named venues. 2-in-6 miss rate on a realistic sample; Nominatim
   rescued both.

**Headline demo statistic: 24 of 61 real items in one Oakland meeting sit on
the consent calendar** — one vote, no discussion, unless someone pulls them.

## Next 3 concrete steps

1. **Address extraction** (`src/docket/extract/`): pull street addresses and
   dollar amounts out of agenda item titles so the geocoder has input. Start
   rules-based (regex for `NNNN Street Name`, `$N,NNN`), measure coverage on
   the 61 real items, then decide whether an LLM pass is needed.
2. **Labeling export** (`scripts/export_for_labeling.py`): emit 100–150 real
   items as a CSV the human can label relevant/not-relevant plus a one-line
   reason (YOUR-TASKS.md #7).
3. **`eval.py`**: score the impact classifier against the labeled holdout.
   This is the Phase 1 exit condition.

## Blocked on

- **AWS CLI install + credentials** (YOUR-TASKS.md #1). Blocks only the
  AgentCore deploy. Steps 1–3 above are unblocked.
- **Human labeling** gates step 3, not steps 1–2.

## Open items for the human

- Record the ingest clip (PROTOCOLS.md P5 recording queue) — deferred to
  evening, reproducible, fine
- Confirm the MIT LICENSE name ("Khaja Sahitya Sarabu")
- Public AWS Builder ID profile URL
- Send the 8–10 neighborhood-org emails (YOUR-TASKS.md #5)

## Note

Repo lives in a OneDrive-synced folder. Push every session (P6). On git object
corruption, re-clone from GitHub rather than repairing locally.

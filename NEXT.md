# NEXT — where the last session stopped

Updated at the end of every session, and immediately on hitting a rate limit
(PROTOCOLS.md P11).

---

**Last updated:** 2026-08-13
**Current phase:** Phase 1 — Data spine + eval (Phase 0 substantially done)
**Phase 1 exit condition:** `eval.py` prints a precision/recall score

## Done

**Phase 0**
- ✅ Repo initialized, MIT license, `.gitignore`, README with prior-art positioning
- ✅ Pushed to https://github.com/sahitya1179/docket
- ✅ `pyproject.toml`, venv, deps installed (Python 3.14.4)
- ⬜ AgentCore template deploy — **blocked on AWS CLI + credentials**

**Phase 1 (started early, since it needs no AWS access)**
- ✅ `docket.cache.DiskCache` — content-addressed, atomic writes
- ✅ `docket.models` — `AgendaItem`, `Meeting`, `Stage`, `Attachment`
- ✅ `docket.ingest.legistar` — JSON API client, retry, disk cache (3ms cached reads)
- ✅ `docket.ingest.triage` — matter-file rule, 61 kept / 17 dropped on Oakland 9560
- ✅ `docket.ingest.sections` — hierarchical stage inheritance
- ✅ 12 tests passing offline against a committed fixture; ruff clean

## What the real data taught us (drove two rewrites)

1. **Matter file is the signal for real business.** All 61 items with a matter
   file are legislative matters; all 17 without are procedural. My first
   heuristic assumed an agenda number meant real business — wrong, "Call To
   Order" is item 1.
2. **Oakland agendas are hierarchical.** Item `6` is the header "CONSENT
   CALENDAR (CC) ITEMS:"; `6.1`–`6.x` are its children. Stage must be inherited
   from the section, not keyword-matched — keyword matching read "ACTION ON
   OTHER **NON-CONSENT** CALENDAR ITEMS:" as a consent section.
3. **Stage is only meaningful for substantive items.** Procedural lines like
   "Approval of the Consent Agenda" otherwise inflate the consent count.

**Headline demo statistic: 24 of 61 items in one Oakland meeting sit on the
consent calendar** — passed in a single block with no discussion unless pulled.

## Next 3 concrete steps

1. **Geocoder** (`src/docket/geo/`): Census → OSM/Nominatim fallback, permanent
   disk cache, plus a test asserting a non-zero match rate on Oakland addresses
   (Census alone returns 0 for these — the known trap)
2. **Address extraction** from agenda item titles, so the geocoder has input
3. **Labeling export**: a CSV/JSONL of 100–150 real items for the human to label
   (YOUR-TASKS.md #7), then `eval.py` to score against the holdout

## Blocked on

- **AWS CLI install + credentials** (YOUR-TASKS.md #1). Blocks only the
  AgentCore deploy. Steps 1–3 above are unblocked.

## Open items for the human

- Confirm the MIT LICENSE name ("Khaja Sahitya Sarabu")
- Public AWS Builder ID profile URL (the `?tab=badges` link is the logged-in view)
- Send the 8–10 neighborhood-org emails (YOUR-TASKS.md #5)

## Note

Repo lives in a OneDrive-synced folder. Push every session (P6). On git object
corruption, re-clone from GitHub rather than repairing locally.

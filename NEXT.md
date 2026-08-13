# NEXT — where the last session stopped

Updated at the end of every session, and immediately on hitting a rate limit
(PROTOCOLS.md P11).

---

**Last updated:** 2026-08-13
**Current phase:** Phase 0 — Foundation
**Phase exit condition:** a deployed hello-world Strands agent on AgentCore Runtime

## Done so far

- ✅ Repo initialized, MIT license, `.gitignore`, README with prior-art positioning
- ✅ First commit pushed → https://github.com/sahitya1179/docket
- ✅ Planning docs committed (PLAN, PROTOCOLS, DECISIONS, PARKED, YOUR-TASKS)
- ✅ `requirements.txt`, `.env.example` with demo-mode safety flag

## Next 3 concrete steps

1. Clone the AWS fullstack AgentCore template into `infra/`, deploy it
   unmodified, confirm it runs end to end, then strip the sample
   calculator/weather tools — **requires Bedrock model access to be granted**
2. Build the hybrid Legistar client (`src/docket/ingest/legistar.py`): JSON API
   first, `scraper-legistar` fallback, disk fixture cache. Validate against
   Oakland event 9560 (78 items, known good)
3. Build the geocoder (`src/docket/geo/`): Census → OSM/Nominatim fallback,
   permanent disk cache, plus a test asserting a non-zero match rate on Oakland
   addresses (Census alone returns 0 for these — this is the known trap)

## Blocked on

- **Bedrock model access approval** — human task #1 in YOUR-TASKS.md. Step 1
  above cannot be tested until this is granted. Steps 2 and 3 are NOT blocked
  and can proceed in the meantime.

## Open items for the human

- Confirm the name on the MIT LICENSE is correct ("Khaja Sahitya Sarabu")
- Get the **public** AWS Builder ID profile URL (the `?tab=badges` link is the
  logged-in view, not the shareable one)
- Send the 8–10 neighborhood-org emails (YOUR-TASKS.md #5)

## Note

The repo lives inside a OneDrive-synced folder. OneDrive occasionally corrupts
`.git` during sync. Mitigation: push after every session (P6). If git ever
reports object corruption, re-clone from GitHub rather than repairing locally.

# Docket — project context for Claude Code

## Read these first, every session (PROTOCOLS.md P0)

1. `PLAN.md` — the build plan. The current phase and its exit condition govern all work.
2. `PROTOCOLS.md` — standing rules. These apply automatically and are not re-asked.
3. `DECISIONS.md` — settled calls. **Do not relitigate anything in here.**
4. `NEXT.md` — where the last session stopped.

At session start, state: today's date, current phase, the phase's exit condition,
and what this session will accomplish.

## What this is

Docket: an agent for the volunteer who runs a neighborhood association. It reads
the city's council agenda packet nightly, filters to items affecting the group's
specific geography, drafts a position letter and member alert, gates them behind
human approval, then files and tracks the outcome.

Hackathon: AWS "Agents for Humans" — Good Neighbor Agents track.
Deadline Sep 14 2026 5pm PT. Code freeze Sep 10. Submit Sep 12.

## The two differentiators (verified against live competitors)

1. **Per-address geocoded impact filtering** — every competitor filters by topic
2. **Approval-gated action package** — nobody drafts + gates + files

Outcome tracking is NOT a differentiator (CivicSummary already ships it).

## Hard rules

- **Never** build anything that can submit to a real city clerk. Demo mode ships
  with no submission credentials at all.
- **Never** put bulk JSON, full PDFs, or large dumps into context — script it,
  run it, print ≤20 lines.
- All external API calls cached to disk. All LLM calls cached by prompt hash.
- Tune on Haiku, validate on Sonnet.
- Record 30s of footage every time a feature first works (P5).
- The repo is public — no secrets, ever.

## Stack

Strands Agents (Graph + scoped Swarm + hooks) · Amazon Bedrock AgentCore
(Runtime, Memory, Gateway, Identity, Code Interpreter, Browser, Observability) ·
Legistar JSON API with `python-legistar-scraper` fallback · Census geocoder with
OSM/Nominatim fallback · Python 3.10+ · Windows dev machine (PowerShell).

## Verified facts (tested live — do not re-derive)

- Legistar JSON API is free, no key: works for Oakland, Mesa, Seattle
- NYC/Philadelphia return 403, Chicago 500 → use the HTML scraper for those
- One Oakland meeting = 78 structured agenda items with matter files + PDF URLs
- Census geocoder **fails on Oakland addresses** — OSM fallback is mandatory
- Nominatim: ~1 req/sec, discourages bulk → cache permanently

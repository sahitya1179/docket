# Docket — Build Plan (v2, corrected)

**Hackathon:** Agents for Humans (Devpost) · **Track:** Good Neighbor Agents
**Deadline:** Mon Sep 14, 2026, 5:00pm PT — **= 5:30am IST, Tue Sep 15**
**Today:** Aug 13, 2026 · **Code freeze:** Sep 10 · **Submit:** Sep 12
**Budget:** ~34–42 hours of human time

> Read this file at the start of every Claude Code session. See PROTOCOLS.md.

---

## 1. Positioning — lead with the prior art

**There are shipping products in this space. Name them first; a judge will find
them in 30 seconds and getting caught overclaiming is worse than not claiming.**

| Product | What it does | What it does NOT do |
|---|---|---|
| CivicSummary (weho.civicsummary.ai, ~$20/mo) | Plain-English agenda summaries, vote tracking, "One-Click Comments", an Accountability Tracker for staff follow-through | **No street-address filtering** (citywide/topic only). **Does not draft comments** — only submits user-written text |
| Next30Days (GeekWire, Apr 2026) | Legistar pipeline, topic-selected email digest 2×/week, Seattle + Bellevue | **No address filtering.** **No drafting, no submitting, no outcome tracking** |
| Citizen Portal AI / CivicDigest / SeeGov / Aware | Summaries, spending trackers, hyperlocal reports | Same gap |

**Do NOT claim outcome tracking as a differentiator** — CivicSummary's
Accountability Tracker already does it. It stays as a feature; it is not the pitch.

### The two real differentiators (both verified, not assumed)

1. **Location-aware impact filtering.** Everything above filters by *topic*
   (housing, transit, safety). Docket filters by **geocoded proximity to the
   group's streets**, falling back to mission-match for citywide items.

   Measured honestly on Oakland 9560: **18% of substantive items carry a
   geographic reference**, and those are the high-stakes ones — parcel sales,
   developments, zoning changes. The other 66% are genuinely citywide
   (Municipal Code, Salary Ordinance, Sanctuary City policy) and are caught by
   mission-match instead. Do not claim proximity filtering covers everything;
   claim it covers the items where geography is what makes them matter.
2. **The approval-gated action package.** Nobody drafts a comment in the group's
   voice, gates it behind a hook, and files it. This is also the Strands
   engineering story — and **AWS is judging Strands usage, not product novelty.**

### The quote to build the pitch around

Clayton, founder of Next30Days, on his own product's limit: there are tools that
summarize meetings, and nothing really tries to bridge the gap between giving
people the information and actually getting them to show up.

**A competitor naming the action layer as the unsolved problem is the strongest
validation available.** Open the video with the prior art, then this quote, then
show Docket closing that gap.

---

## 2. The problem (corrected — scoped, not overstated)

**In California, the Ralph M. Brown Act requires 72 hours' notice for regular
meetings** (24 for special, 1 for emergency). Other states differ — do not claim
a nationwide rule.

The stronger, verifiable point is the **consent calendar**: a block of items
passed in a single vote with no discussion. Any council member — or any member of
the public during the consent-comment period — can pull an item, one person, no
second, no vote. But the packet is 200–800 pages of legalese, so nobody reads it
and nothing gets pulled. This is how a six-figure sole-source contract gets
approved alongside the routine approval of minutes.

**Cite that failure mode.** A real, documented harm beats a rhetorical one.

---

## 3. The product

**For:** the unpaid volunteer who runs a neighborhood association or small
community nonprofit.

**Nightly, in the background:**
1. Pull new meetings + agenda items for the group's city
2. Strip boilerplate (Zoom instructions, definitions of terms)
3. Extract each real item → typed record (stage, addresses, amounts, matter file)
4. Geocode addresses, test against the group's boundary
5. Score impact against boundary + mission; discard the ~95% that is noise
6. For survivors: brief + drafted position letter + member alert + deadline
7. **Human approves** (hook-enforced) → then file, notify, calendar
8. After the meeting: read minutes, record the vote, follow the item forward

---

## 4. Verified technical foundation

Tested live before planning — not assumed.

| Assumption | Status | Evidence |
|---|---|---|
| Legistar JSON API free, no key | ✅ | Oakland, Mesa, Seattle returned data |
| Some cities block it | ⚠️ | NYC/Phila 403, Chicago 500 → scraper fallback |
| Agenda items come back structured | ✅ | Oakland event 9560 → 78 items w/ matter files |
| Agenda PDFs directly linkable | ✅ | `EventAgendaFile` gives a direct URL |
| Census geocoder free, no key | ⚠️ | DC matched; **both Oakland addresses returned 0 matches** |

**Consequence:** geocoding needs an OSM/Nominatim fallback from day one, with
disk caching. Nominatim rate-limits at ~1 req/sec and discourages bulk use —
cache every result permanently; after the first pass it is a non-issue.

---

## 5. Architecture

### Strands

**Graph (deterministic DAG)** — the nightly pipeline:

```
IngestNode   → fetch meetings + items (API, scraper fallback, disk cache)
TriageNode   → strip boilerplate (cheap model)
ExtractNode  → parallel, per item → typed AgendaItem (structured output)
GeoNode      → geocode (Census → OSM fallback), test against org boundary
ImpactNode   → score 0–1 against boundary + mission
  └─ SwarmNode → ONLY for gray-zone scores (0.4–0.7)
BriefNode    → plain-English brief, citations to source text
PackageNode  → position letter + member alert + one-pager
```

**Swarm** — gray-zone items only: `Researcher` / `Skeptic` / `PlainLanguageEditor`.

**Hooks — the differentiator:**
- `BeforeToolCallEvent` → **ApprovalGate**: any tool tagged `side_effect=True`
  raises without a valid approval token. The agent is autonomous right up to the
  doorway of speaking for the group — the hook *is* the doorway.
- `AfterToolCallEvent` → **CitationGuard**: every claim maps to source text or
  the brief is regenerated.

### AgentCore

Runtime (host + nightly EventBridge trigger) · Memory (org profile + item
history) · Gateway (Legistar/geocode as MCP) · Identity (email consent) ·
Code Interpreter (budget tables, one-pager) · Browser (no-API portals) ·
Observability (the "why was this flagged" trace = the trust UI).

### Data model

```
AgendaItem       id, city, event_id, meeting_date, body_name, item_number,
                 matter_file, title, raw_text, stage, addresses[], amounts[]
ImpactAssessment item_id, org_id, score, reasons[], matched_boundary,
                 distance_m, citations[]
TrackedItem      matter_file, org_id, status, history[], outcome
```

`stage ∈ {consent, action, public_hearing, informational}` — consent is the
highest-value signal.

---

## 6. Cost budget (do this in Phase 1, not Phase 4)

Volume: ~78 items/meeting × ~10 meetings/month ≈ **26 items/day**.
Estimated **~55k input / 10k output tokens per day** ≈ 1.65M in / 300k out per month.

| Model | First-party list | Est. monthly production cost |
|---|---|---|
| Haiku 4.5 | $1 / $5 per MTok | **~$3** |
| Sonnet 5 | $3 / $15 ($2/$10 intro thru Aug 31) | **~$10** |

Bedrock is partner-priced — verify on the AWS Bedrock pricing page.

**Production is trivial. Development is what kills the credits.** A 150-item eval
at ~2k tokens/item is ~300k input per run; 200 tuning runs = 60M tokens =
**$60 on Haiku, $180 on Sonnet**. That torches the $50 credits.

**Mandatory mitigations, built in Phase 1:**
- **Response cache** keyed by `(prompt_hash, model)` — re-running the eval only
  re-invokes prompts that actually changed
- **Fixture cache** for all Legistar + geocode calls
- Tune on **Haiku**, validate on **Sonnet**

---

## 7. Reuse (all legitimate, all disclosed in README)

| Component | Source | License | Saves |
|---|---|---|---|
| Infra scaffolding | `aws-samples/sample-amazon-bedrock-agentcore-fullstack-webapp` | MIT-0 | ~20h |
| Legistar HTML scraper | `opencivicdata/python-legistar-scraper` | BSD-3 | ~7h |
| Geocoding | Census API + `censusgeocode`, OSM fallback | Public/MIT | ~4h |
| Data modeling reference | DataMade Councilmatic (read, don't fork) | MIT | ~2h |

Rules permit "frameworks, libraries, starter templates, and AI coding assistants."
Pre-existing code must be disclosed → a "Built with" section covers it.

---

## 8. Phases

### Phase 0 — Foundation (Aug 13–14, ~4h)
- `git init`, MIT `LICENSE` at root, first commit
- **Request Bedrock model access — day one, it can take time to approve**
- Deploy the AWS fullstack template unmodified; confirm it runs; strip sample tools
- `CLAUDE.md` with architecture
- **Budget a full day for AgentCore, not 2 hours** — it's new; IAM and docs will bite
- **Exit:** a deployed hello-world Strands agent on AgentCore Runtime

### Phase 1 — Data spine + eval + cache (Aug 15–20, ~10h)
- Hybrid Legistar client (JSON API → HTML scraper fallback), disk-cached
- Boilerplate triage filter
- Geocoder: Census → OSM fallback, permanent disk cache
- **LLM response cache** keyed by prompt hash + model
- **Hand-label 100–150 agenda items, split train/holdout** (4–6h human work)
- `eval.py` prints precision/recall against the holdout
- **Token-cost measurement on a real run** — record actual $/run
- **Exit:** `eval.py` prints a score. Autonomous iteration unlocked.

### Phase 2 — Agent core (Aug 21–27, ~10h)
- Typed extraction via structured output
- Impact scoring, tuned against the eval until ≥85% on the **holdout**
- Strands Graph wiring
- ApprovalGate + CitationGuard hooks
- Brief + position letter + member alert drafting
- **Exit:** one command turns a real meeting into an approval-pending package

### Phase 3 — Product + deploy (Aug 28–Sep 3, ~8h)
- Web UI: onboarding, digest, approval screen, item detail with citations
- AgentCore Memory, Gateway, Identity wired
- EventBridge nightly trigger; email notifications
- **Exit:** public URL, running nightly on its own

### Phase 4 — Differentiators + hardening (Sep 4–9, ~7h)
- Swarm for gray-zone items
- Outcome tracking (a feature, not the pitch)
- Member Q&A over the tracked corpus
- Second city
- Demo mode: read-only, preloaded, **cannot submit to real clerks**
- **Exit:** a judge with no login can use it in 60 seconds

### Phase 5 — Freeze + submit (Sep 10–12, ~5h)
- **Sep 10: CODE FREEZE. No new features.**
- Edit video from footage captured throughout (Claude writes script, you narrate)
- README, Mermaid architecture diagram, Devpost copy
- builder.aws blog post (#AgentsforHumans) if ahead — up to +0.6
- **Sep 12: submit.** Sep 13–14 is buffer, not workspace.

---

## 9. Division of labor

**Claude Code:** all application code, hybrid client, extraction, graph, hooks,
UI, eval harness, caches, tests, README, Mermaid diagram, video script, Devpost
copy, blog draft.

**You:** AWS account + **Bedrock model access approval**, running deploys,
**hand-labeling 100–150 items**, recording voiceover and screen, YouTube upload,
Devpost entry, AWS Builder ID, org outreach emails, and the product judgment calls.

---

## 10. Risks

| Risk | Mitigation |
|---|---|
| Geocoder gaps silently drop items | OSM fallback + a test asserting non-zero match rate |
| Dev token spend burns $50 credits | Response cache + Haiku for tuning (Phase 1) |
| Scope creep past freeze | Sep 10 freeze is absolute; all of Phase 4 is droppable |
| Pro rate limits stall a session | Fixture caching; one module per session; no bulk data in context |
| Accidental real filing during demo | Demo mode has no submission credentials; enforced by ApprovalGate |
| Video rushed at the end | Capture 30s of footage every time a feature works |
| Overfitting the classifier | 100–150 items with a held-out split; report holdout score only |
| AgentCore/IAM eats a day | Budgeted as a full day in Phase 0 |

---

## 11. Definition of done

- [ ] Public repo, MIT license detectable in GitHub About
- [ ] README with setup instructions that work on a clean machine
- [ ] Architecture diagram (Mermaid, renders on GitHub)
- [ ] Public YouTube video ≤5 min: demo + problem + audience + why it matters
- [ ] Live demo URL — free, no login, no restrictions, cannot file to real clerks
- [ ] AWS Builder ID
- [ ] Devpost submission complete
- [ ] Prior art named and pre-existing components disclosed

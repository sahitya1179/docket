# DECISIONS — settled, do not relitigate

Format: `YYYY-MM-DD — Decision — Why`

New evidence can overturn a decision, but only via a **new dated entry** saying
so. Never silently reverse.

---

**2026-08-13 — Build Docket (civic agenda agent), not the food bank shift matcher**
More original; verified free data source; the shift matcher is the first example
in the track's own inspiration text and will be crowded.

**2026-08-13 — Good Neighbor Agents track, built for the org, not the resident**
The track description centers organizations and the volunteers running them. An
individual-resident framing is Everyday Agents territory and would score worse on
track fit.

**2026-08-13 — Oakland as the primary city**
Legistar JSON API verified working; active civic tech community; agendas contain
consequential housing and policing items that demo well.

**2026-08-13 — Outcome tracking is a feature, NOT the differentiator**
CivicSummary ships an Accountability Tracker that already does this. Claiming
novelty here would be caught by any judge who searches for 30 seconds.

**2026-08-13 — The pitch leads with named prior art**
CivicSummary, Next30Days, Citizen Portal AI, CivicDigest all exist. Naming them
and stating precisely what's different signals research rather than naivety.

**2026-08-13 — Brown Act claim scoped to California only**
The 72-hour notice rule is California's Brown Act, not nationwide. A confidently
wrong nationwide legal claim in the opening line reads as unverified output.

**2026-08-13 — Use the AWS fullstack AgentCore template for infrastructure**
MIT-0, saves ~20h of the worst-compressing work (auth, IAM, CloudFront, Runtime).
Disclosed in the README under "Built with."

**2026-08-13 — Eval set is 100–150 items with a held-out split, not 25**
25 items overfits. Only the holdout score gets reported.

**2026-08-13 — Response cache + fixture cache built in Phase 1, not later**
Production inference is ~$3–10/month, but naive eval iteration can burn
$60–180 and torch the $50 credits. The cache is the mitigation.

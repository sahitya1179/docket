# Docket

**Your city votes in 72 hours. Docket already read the packet.**

An agent for the unpaid volunteer who runs a neighborhood association or small
community nonprofit. Docket reads the city council agenda packet every night,
surfaces only the items that affect the group's specific streets, drafts a
position letter and member alert, waits for a human to approve, then files and
tracks the outcome.

Built with [Strands Agents](https://strandsagents.com/) and
[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) for the
**Agents for Humans** hackathon — Good Neighbor Agents track.

> 🚧 **Under active development.** Hackathon submission due Sep 14, 2026.

---

## The problem

In California, the Ralph M. Brown Act requires 72 hours' notice before a regular
council meeting. What gets posted is a 200–800 page PDF packet of municipal
legalese on a Legistar portal.

Buried inside is the **consent calendar** — a block of items passed in a single
vote with no discussion. Any council member, or any member of the public during
the consent-comment period, can pull an item out for debate. One person. No
second. No vote required.

But nobody reads 800 pages in 72 hours, so nothing gets pulled. That is how a
six-figure sole-source contract gets approved alongside the routine approval of
the previous meeting's minutes.

---

## Prior art, and what's actually different

This space has shipping products, and it would be dishonest to pretend otherwise:

| Product | What it does |
|---|---|
| [CivicSummary](https://weho.civicsummary.ai/) | Plain-English agenda summaries, vote tracking, one-click comment submission, staff-accountability tracking |
| [Next30Days](https://www.geekwire.com/2026/can-ai-revive-democracy-former-amazon-product-manager-builds-tool-to-spark-civic-engagement/) | Legistar pipeline, topic-selected email digests, Seattle + Bellevue |
| Citizen Portal AI, CivicDigest, SeeGov, Aware | Summaries, spending trackers, hyperlocal reports |

**Docket differs in two specific ways:**

1. **Per-address impact filtering.** Every product above filters by *topic* —
   housing, transit, public safety. Docket filters by geocoded proximity to a
   specific parcel, combined with the organization's stated mission.

2. **The approval-gated action package.** No existing tool drafts a comment in
   the group's voice, gates it behind human approval, and then files it.
   CivicSummary submits text the user wrote; Next30Days doesn't submit at all.

The founder of Next30Days described the gap himself: there are tools that
summarize meetings, and nothing really tries to bridge the gap between giving
people the information and actually getting them to show up.

That gap is what Docket is for.

---

## How it works

```
Nightly →  Ingest      fetch meetings + agenda items (Legistar API, scraper fallback)
           Triage      strip boilerplate (Zoom instructions, definitions)
           Extract     each item → typed record (stage, addresses, amounts)
           Geocode     resolve addresses, test against the group's boundary
           Impact      score relevance; discard the ~95% that is noise
           Brief       plain-English summary, every claim cited to source text
           Package     position letter + member alert + deadline

Human   →  approve / edit                    ← enforced by a Strands hook

Then    →  file · notify members · calendar the hearing
Later   →  read the minutes, record the vote, follow the item forward
```

The human approval step is enforced by a `BeforeToolCallEvent` hook: any tool
that speaks on the organization's behalf raises unless a valid approval token is
present. The agent is fully autonomous right up to the doorway of acting in
someone's name — and the hook is the doorway.

---

## Safety

**Docket's demo mode cannot file anything to a real city clerk.** It ships with
no submission credentials at all — the absence of credentials is the enforcement,
not a config flag. Live filing is an explicit, human-triggered action on a
configured deployment.

---

## Status

| Phase | Status |
|---|---|
| 0 · Foundation | 🔨 In progress |
| 1 · Data spine + eval harness | ⬜ |
| 2 · Agent core (Graph, hooks, drafting) | ⬜ |
| 3 · Product + AgentCore deploy | ⬜ |
| 4 · Swarm, outcome tracking, Q&A | ⬜ |
| 5 · Freeze + submit | ⬜ |

---

## Built with

| Component | Source | License |
|---|---|---|
| Infrastructure scaffolding | [aws-samples/sample-amazon-bedrock-agentcore-fullstack-webapp](https://github.com/aws-samples/sample-amazon-bedrock-agentcore-fullstack-webapp) | MIT-0 |
| Legistar HTML scraper | [opencivicdata/python-legistar-scraper](https://github.com/opencivicdata/python-legistar-scraper) | BSD-3 |
| Geocoding | US Census Geocoder + OpenStreetMap/Nominatim | Public domain / ODbL |
| Agent framework | [Strands Agents](https://strandsagents.com/) | Apache-2.0 |

Data comes from public municipal records via the Legistar Web API.

---

## License

MIT — see [LICENSE](LICENSE).

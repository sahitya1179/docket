# PROTOCOLS — how we stay on plan

These are standing rules. They apply to every session, automatically, without
being re-asked. If a protocol conflicts with something said mid-session, the
protocol wins unless you explicitly override it.

---

## P0 — Session start (every single time)

At the start of every Claude Code session, before any code:
1. Read `PLAN.md` and `PROTOCOLS.md`
2. Read `DECISIONS.md` (settled calls — do not relitigate these)
3. State in one line: **today's date, current phase, and the phase's exit condition**
4. State what this session will accomplish

If the session cannot be tied to the current phase's exit condition, say so
before writing code.

---

## P1 — Drift detection and recovery

**Drift = work that does not move the current phase toward its exit condition.**

Check for drift at three moments: before starting a task, after any task that
took more than ~30 minutes, and at session end.

**Three drift signals:**
- The work isn't listed in the current phase
- The current phase's exit condition hasn't moved in 2+ hours of work
- We're building something because it's interesting, not because the plan needs it

**Recovery, in order:**
1. **Stop.** Do not finish the current tangent "since we're here."
2. **Name it out loud** — one sentence: "This is drift: we're doing X, the phase needs Y."
3. **Classify it:**
   - *Blocking* — the plan can't proceed without it → do it, and log it in `DECISIONS.md`
   - *Valuable but not blocking* → write it in `PARKED.md`, return to plan
   - *Neither* → drop it entirely
4. **Restate the exit condition** and resume the nearest task that serves it.

**Never** silently expand scope. Every deviation gets named before it gets done.

---

## P2 — Scope creep

Any new feature idea during Phases 0–4 goes to `PARKED.md`, not into the build.
`PARKED.md` is reviewed exactly once, at the start of Phase 4, and only items
that strengthen a judging criterion get pulled in.

**After Sep 10, `PARKED.md` is closed.** Nothing comes out of it.

---

## P3 — Blocked or stuck

If any single problem consumes more than **45 minutes** with no progress:
1. Stop and write down what was tried
2. Ask: is this on the critical path to the phase's exit condition?
   - **No** → cut it, log in `DECISIONS.md`, move on
   - **Yes** → find the simplest thing that unblocks (a stub, a hardcode, a
     different library) and mark it `# TODO(phase-N)` in the code
3. Never let one problem eat a day. Every phase has a droppable version.

---

## P4 — Cost guard

- Never send bulk JSON, full PDFs, or large file dumps into context. Write a
  script, run it, print a summary of ≤20 lines.
- All external API responses (Legistar, geocoding) are cached to disk on first fetch.
- All LLM calls go through the response cache keyed by `(prompt_hash, model)`.
- Tune on Haiku. Validate on Sonnet. Never tune on Sonnet.
- Check AWS billing every Monday. If spend exceeds $15 total before Sep 1, stop
  and re-check the caches before continuing.

---

## P5 — Video footage (the most-forgotten protocol)

**Every time a feature works for the first time, capture 30 seconds of it.**

Save to `footage/` named `YYYY-MM-DD-what-it-shows.mp4`. On Sep 11 you will be
scanning filenames, not watching clips to identify them.

Reason: on Sep 10 you need footage of features working. Re-staging a demo from
scratch takes 6–10 hours; editing existing footage takes ~4.

### When recording may be deferred (added 2026-08-13)

The real risk is **losing a state you cannot reproduce**. So:

- **Reproducible feature** — there is a committed script, cached data, or a
  committed fixture that regenerates the exact output on demand → recording may
  be **batched later**, as long as it happens before the Sep 10 freeze. Add the
  clip to the Recording queue below so it isn't forgotten.
- **Non-reproducible moment** — a live deploy, a one-off API response, a
  transient UI state, anything depending on a service that may change → record
  **immediately**. This is the case P5 was written for.

Batching reproducible clips into one evening session is usually *more* efficient
than stopping mid-build for each one.

### Recording queue

Clips owed, all reproducible. Clear before Sep 10.

- [ ] `ingest-consent-calendar` — run `python scripts/demo_ingest.py`, or open
      `scripts/replay.html` and press SPACE (fullscreen with F11)

---

## P6 — Commit and backup

- Commit at the end of every work session, minimum. Small commits are fine.
- Push to GitHub the same day. **A local-only repo is not a backup.**
- Never commit `.env`, AWS keys, tokens, or the `cache/` directory.
- The repo is public from day one — so nothing secret ever goes in it, ever.

---

## P7 — Safety (non-negotiable)

- **Nothing in this project may submit a public comment, email, or form to a
  real city clerk during development or demo.** Ever.
- Demo mode ships with no submission credentials at all — the absence of
  credentials is the enforcement, not a config flag.
- The ApprovalGate hook blocks every `side_effect=True` tool without a token.
- Say this out loud in the video. Restraint reads as maturity to judges.

---

## P8 — Freeze protocol

**Sep 10 is the code freeze. It is absolute.**

After freeze, the only permitted changes are:
- Fixing a crash in the demo path
- README / documentation / diagram
- Video and submission materials

Not permitted after freeze: new features, refactors, "quick improvements,"
dependency upgrades, or anything in `PARKED.md`.

If something is broken on Sep 10 and can't be fixed without a new feature,
**cut the feature from the demo and the video** rather than building past freeze.

---

## P9 — Decision log

`DECISIONS.md` records every settled call: what was decided, why, and the date.

Once something is in `DECISIONS.md`, it is not re-argued. If new evidence
genuinely overturns it, add a new dated entry saying so — do not silently reverse.

This exists because re-litigating settled decisions is the single biggest
time sink in a solo project under deadline.

---

## P10 — Verification (no claiming done without evidence)

A task is "done" only when there is evidence: a passing test, a printed output,
a screenshot, a deployed URL that loads.

- Never report a feature as working based on the code looking correct.
- If tests fail, say so and show the output.
- If a step was skipped, say it was skipped.
- "It should work" is not done.

---

## P11 — Rate limits (Claude Pro)

When a session hits a usage limit:
1. Commit and push whatever exists right now
2. Write the next 2–3 concrete steps into `NEXT.md`
3. Stop — do not resume in a degraded, contextless state

Next session begins with P0, reads `NEXT.md`, and continues.

Keep sessions scoped to one module. Clear between modules rather than running one
enormous session whose full context is re-paid on every turn.

---

## P12 — Weekly check (every Monday, 10 minutes)

1. Are we on the phase the plan says we should be on for today's date?
2. If behind: what gets cut? (Answer from Phase 4 first — it's all droppable.)
3. Is there footage for every feature built this week? (P5)
4. AWS spend check (P4)
5. Is everything pushed to GitHub? (P6)

If behind by more than 3 days at any Monday check, **cut scope immediately** —
do not plan to "catch up." Catching up never happens.

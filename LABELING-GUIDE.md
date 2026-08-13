# Labeling guide

**Both labelers use this document.** The overlap-agreement number is only
meaningful if we are answering the same question.

If you disagree with anything here, change it and tell me — the rubric is a
product decision, and it is yours. Re-labeling the training set costs my time,
not yours, so correcting this is cheap right up until `eval.py` runs.

---

## The question you are answering

> *Imagine you are the volunteer who runs a neighborhood association in
> Oakland. This item is on next week's council agenda. Would you want an alert
> about it?*

Not "is this important to the city." Not "is this interesting." **Would this
group want to know.**

Mark `y` or `n` in the `relevant` column, and write one short sentence in
`reason` explaining the call.

---

## Mark `y` when any of these is true

**1. It touches a specific place.**
A parcel sale, a development, a zoning change, a street closure, a permit — for
somewhere a neighborhood group could walk to. The `places` column shows what was
detected, but trust the title over the column.

*Example:* "Sale Of 319 Chester Street" → `y` — a city-owned parcel changing
hands is exactly what neighbors organize about.

**2. It changes the rules everywhere, including here.**
Planning code amendments, tenant protections, ADU rules, sanctuary policy,
police policy. No address, but it lands on every block.

*Example:* "2026 Miscellaneous Planning Code Amendments ... Updating Accessory
Dwelling Unit Regulations" → `y` — changes what neighbors can build.

**3. It is large money with local consequences.**
A big contract, bond, or budget line for services people actually see —
paving, parks, libraries, policing, homelessness response.

**4. It is on the consent calendar AND matches 1–3.**
Consent items pass in one block with no discussion. A consequential item hiding
on consent is the single highest-value alert this product can send. When
genuinely torn on a consent item, lean `y`.

---

## Mark `n` when

**Internal administration.** Salary ordinances, job classifications, staff
appointments, procedural rules, contract paperwork with no visible service
attached.

**Ceremonial.** Proclamations, commendations, recognitions, declarations of
awareness months.

**Routine governance.** Minutes approval, re-authorizing an existing emergency
declaration for the Nth time, technical corrections to prior ordinances.

**Regional or state matters** where the council is only sending a letter or
taking a position, with no local action.

---

## Hard cases — pick a side and note it

- **Emergency re-declarations** (homelessness, AIDS epidemic, cannabis) — these
  recur every meeting. Default `n`: it is a routine renewal, and alerting on it
  every time trains the user to ignore alerts. Note it if you disagree.
- **Election consolidation / ballot measures** — default `y`. What appears on
  the ballot affects everyone and has a hard deadline.
- **Grant acceptances** — `y` if the money buys something visible locally,
  `n` if it funds internal operations.
- **Labor agreements** — default `n` unless service levels visibly change.

---

## What matters most in your labels

**The `reason` sentence is not paperwork.** It is what teaches the classifier.
Write it the way you would explain the call to a neighbor:

- Good: "Rezones a parcel two blocks from homes; changes what can be built."
- Good: "On consent, so it passes silently, and it closes a street for a year."
- Weak: "Not relevant."
- Weak: "Administrative."

A one-word reason gives the model nothing to learn from.

---

## Ground rules

1. **Do not open `train.csv` before finishing `holdout.csv` and `overlap.csv`.**
   Seeing my labels first contaminates the comparison and the eval loses its
   meaning.
2. Label in a few sittings, not one — judgment drifts when tired.
3. If an item genuinely could go either way, pick one and say so in the reason.
   Disagreement we can see is useful; a blank is not.

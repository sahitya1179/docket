# YOUR TASKS — the human track

Everything here is something **only you can do**. Claude Code cannot do any of it.
Work through it in order. Each item says how to know you're finished.

**⚠️ THE DEADLINE IN YOUR TIME ZONE**
Sep 14, 5:00 PM Pacific = **Sep 15, 5:30 AM India Standard Time**.
So your last full working day is **Sunday Sep 14 (IST)** — but we are submitting
**Sep 12** and treating Sep 13–14 as emergency buffer only.

---

## TODAY — Aug 13 (do these first, ~90 minutes)

### 1. Request Bedrock model access ⚠️ MOST URGENT
This can take hours or days to approve. Everything else is blocked behind it.

- Go to the AWS Console → search "Bedrock" → open it
- Set region to **us-east-1** (top right corner)
- Left sidebar → **Model access** → **Modify model access**
- Tick **all Anthropic Claude models**
- Submit the request

**Done when:** the Anthropic models show status "Access granted." If it says
"In progress," that's fine — check again tomorrow morning.

### 2. Create your AWS Builder ID
- Go to the AWS Builder ID sign-up page and register with your email
- Save the profile URL in a notes file

**Done when:** you can log in and see your Builder ID profile page.

### 3. Register on Devpost
- Create a Devpost account
- Go to the Agents for Humans hackathon page and click **Register**
- Do NOT wait until submission day to register

**Done when:** the hackathon page shows you as registered.

### 4. Create the GitHub repository
- Create a **new public repository** named `docket`
- Do not initialize with anything — Claude Code will push the first commit
- Copy the repo URL and paste it into a notes file

**Done when:** the empty public repo exists and you have its URL.

### 5. Send the neighborhood-org emails ⚠️ TIME-SENSITIVE
Reply rates are low, so send **8–10**, not 2. Send them today — every day of
delay costs you a reply.

Find Oakland neighborhood associations, small nonprofits, or tenants' groups.
Search: `Oakland neighborhood association` / `Oakland community organization`.
Look for a contact email on their site or Facebook page.

Send each one this (adjust the name):

> Subject: Free tool that reads Oakland council agendas for your group
>
> Hi — I'm building a free tool for the AWS Agents for Humans hackathon that
> reads Oakland's city council agenda packets every night and flags only the
> items that affect a specific neighborhood, then drafts a public comment your
> group can review and send.
>
> I'm not selling anything and I'm not asking for money or data. I'd love 15
> minutes to ask what you actually need, and I'd credit your group in the demo
> if you're willing. Would that be OK?
>
> Thanks,
> [your name]

**Done when:** 8–10 emails are sent. Track replies in a notes file.
**If nobody replies:** that's fine. The project is not blocked. You'll model a
realistic org profile instead and say so honestly in the video.

---

## THIS WEEK — Aug 14–20

### 6. Be available to run deploys
When Claude Code asks you to run a deploy command, run it and paste back the
output — including errors. Errors are useful; don't hide them.

### 7. Hand-label 100–150 agenda items ⚠️ THE MOST IMPORTANT THING YOU DO
Budget **4–6 hours**. Split it across several sittings; don't do it in one go
or your judgment drifts.

Claude Code will give you a file with real Oakland agenda items. For each one,
mark:
- **Relevant / Not relevant** to a neighborhood association
- **One short sentence: why**

That "why" is what teaches the agent. Write it like you'd explain to a neighbor.

Examples of what good labels look like:
- *Relevant* — "Rezones a parcel two blocks from residents; changes what can be built."
- *Relevant* — "On the consent calendar, so it passes silently unless pulled."
- *Not relevant* — "Routine approval of prior meeting minutes."
- *Not relevant* — "Zoom dial-in instructions, not an agenda item at all."

**Done when:** every item has a label and a one-line reason.
**Why this matters:** this is the quality ceiling for the entire project. The
agent can never be better at judging relevance than your labels are.

---

## ONGOING — every week until Sep 10

### 8. Monday check (10 minutes, every Monday)
Ask Claude Code: *"Run the Monday check from PROTOCOLS.md P12."*
Then read the answer and decide what to cut if you're behind.

### 9. Watch the AWS bill
AWS Console → **Billing** → **Cost Explorer**, once a week.
If total spend passes **$15** before Sep 1, tell Claude Code to stop and audit
the caches.

### 10. Keep the footage folder growing
Every time Claude Code says a feature works, record 30 seconds of your screen
showing it. Save it in `footage/`.

Windows: press **Win + Alt + R** to start/stop recording (Xbox Game Bar).
Or install OBS Studio if you prefer.

**This is the single easiest thing to forget and the most expensive to skip.**

---

## Sep 10–12 — SUBMISSION WEEK

### 11. Record the video (Sep 11, budget 4 hours)
Claude Code writes the script. You do the rest.

Rules:
- **Maximum 5 minutes.** Going over can disqualify you. Time it.
- Must cover: (1) the problem, (2) who it's for, (3) why it matters, plus a
  working end-to-end demo
- Screen recording + your voiceover is fine — you don't need to be on camera
- Say out loud that demo mode cannot file to real city clerks

Steps:
1. Read the script aloud once to check the timing
2. Record the screen while narrating
3. Re-record any section that's unclear — don't try to fix it in editing
4. Trim the dead air

### 12. Upload the video (Sep 11)
- Upload to YouTube
- Set visibility to **PUBLIC** — not Unlisted, not Private ⚠️
- Copy the link

**Done when:** you can open the link in a private/incognito window and it plays.

### 13. Final repo check (Sep 12)
Open your repo on GitHub in an incognito window and verify:
- [ ] It is **public**
- [ ] The **MIT license shows in the right-hand About panel**
- [ ] The README renders and the architecture diagram displays
- [ ] There are **no secrets** anywhere in the files

### 14. Submit on Devpost (Sep 12)
Fill in every field:
- [ ] Project description
- [ ] Public GitHub repo URL
- [ ] Public YouTube video URL
- [ ] Live demo URL
- [ ] AWS Builder ID
- [ ] Track: **Good Neighbor Agents**

Then **click Submit.** A saved draft is not a submission. ⚠️

**Done when:** Devpost shows the project as Submitted.

### 15. Optional bonus (only if fully done)
Write a builder.aws blog post about the build with hashtag **#AgentsforHumans**.
Worth up to +0.6 points. Claude Code drafts it; you post it.
**Only do this if everything above is finished and submitted.**

---

## THE FIVE THINGS THAT WOULD SINK YOU

1. Not requesting Bedrock model access today — it blocks everything
2. Forgetting to record footage as you go — costs 6+ hours at the end
3. Video longer than 5 minutes, or left Unlisted instead of Public
4. Repo private, or the license not detectable in the About panel
5. Saving the Devpost draft but never clicking Submit

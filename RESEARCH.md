# RESEARCH.md — Faceless YouTube Shorts Automation (Step 0)

Research date: 2026-10-25. Sources are a mix of official Google/YouTube pages (high
confidence, cited) and third-party creator-economy reporting (flagged as estimates —
numbers vary 5-10x between sources and should be treated as directional, not exact).

---

## 1. Niche recommendation

### Pick: **Finance & economics FACTS — not financial advice**
Format: third-person educational content — "how money/banking/markets actually work,"
economic history, how index funds work, historical market events, company/wealth
trivia, etc. Explicitly NOT "5 tips to invest," "you should buy X," or any persona
claiming to be a financial expert.

**Why this and not straight "finance tips" (which ranks higher on every RPM chart):**

Finance/investing/legal/insurance consistently top every CPM/RPM ranking (long-form
CPM commonly cited at $15-$50 for finance vs. $3-$8 for general content; advertisers
in fintech/banking/investment pay a premium). On Shorts specifically the premium
shrinks a lot — estimates for Shorts RPM run $0.03-$0.15/1,000 views generically vs.
maybe $0.08-$0.45/1,000 for finance — but finance still comes out ahead or roughly tied
with every other niche examined.

**However**, two things make the "advice" framing a bad idea for this project
specifically:

1. **YouTube policy risk.** On July 16, 2026 YouTube clarified its non-monetizable
   "inauthentic content" rules into three buckets, one being: *AI personas discussing
   sensitive topics — finance, legal, health* presented as a human expert giving
   advice. This is enforced at the **whole-channel level** — too much of this content
   type can make your entire channel ineligible for ads, not just flag one video. A
   100%-scripted, AI-voiced channel confidently telling viewers what to do with their
   money is close to the exact pattern this rule targets.
2. **Legal/regulatory risk.** Regulators in several countries (India's SEBI, Australia's
   ASIC, South Korea's FSS) are actively enforcing against unlicensed financial advice
   on YouTube. A disclaimer ("not financial advice") is a weak defense — the legal test
   is usually whether a reasonable viewer would interpret it as a recommendation, not
   whether a disclaimer was shown.

Facts/history/explainer framing (no advice, no persona-as-expert) sidesteps both risks
while still sitting in or adjacent to the highest-RPM content category, and it's easy to
produce entirely from licensed stock footage (currency, markets, city skylines,
archival photos, generated charts) with no identifiable real people.

**Runner-up 1: Real estate / economics "did you know" facts.** Similar ad-demand
profile and same facts-only safety, decent stock footage availability, possibly smaller
audience than finance.

**Runner-up 2: History facts.** Lower RPM ceiling, but the most mature, lowest-risk
format of all (archival image + narration is extremely well-trodden), huge archival
asset availability, zero advice/liability exposure. Good fallback if finance-facts
proves too saturated.

**Explicitly avoid regardless of RPM:**
- Specific financial/investment/legal/medical advice or recommendations.
- Any AI persona implying it's a licensed professional or named expert.
- "Make money online" content — frequently flagged under the same policy as
  low-value/template content.

**My honest take:** this is the one place I'd push back if you wanted to go straight for
the highest-RPM "finance tips" format — it's the single biggest policy/legal risk in
the whole plan, for a relatively small RPM gain over the facts-only framing. I'd rather
build something that survives a policy review than chase an extra fraction of a cent
per 1,000 views.

**Caveat on all RPM numbers above:** none of this is official YouTube data — it's
industry-blog estimation, and sources disagree by 5-10x. Recommend wiring up the
YouTube Analytics job (already in your plan) from day one so we replace these guesses
with real numbers within 4-6 weeks of launch.

---

## 2. YouTube Partner Program — Shorts monetization rules

**Eligibility (verify against the live Help Center page right before building — these
numbers are reported by third parties, not independently confirmed by me against
YouTube's current page):**
- Ad-revenue-sharing tier: 1,000 subscribers + (4,000 public watch hours in 12 months
  OR 10M Shorts views in 90 days), no active strikes, 2FA on, AdSense linked,
  supported country.
- A reported Feb 1, 2027 threshold increase (8,000 hours / 20M Shorts views for new
  applicants) is **unconfirmed against YouTube's own announcement** — re-check this
  closer to when the channel would apply, since it could land right in your launch
  window.

**Shorts ad revenue mechanics:**
- Shorts revenue comes from a shared pool (not per-video ads), split **45% creator /
  55% YouTube** — the reverse of the 55/45 long-form split. This figure traces to
  YouTube's 2023 announcement; I found no 2026 source confirming a change, but also no
  fresh confirmation — check the official "How Shorts monetization works" page
  directly before relying on it financially.
- If a Short uses licensed music, part of the pool is split off to music publishers
  before creators get paid — **using no music keeps more of the pool**, which also
  conveniently avoids copyright-claim risk entirely. Recommend the pipeline never adds
  background music, or only uses music explicitly licensed for monetized use.
- Reported Shorts RPM: roughly $0.03-$0.15 per 1,000 views for generic content,
  $0.08-$0.45 for finance-adjacent. These are blog estimates, not official figures.

---

## 3. "Inauthentic content" policy — the most important thing to design around

Verified directly against `support.google.com/youtube/answer/1311392`.

YouTube renamed this policy from "Repetitious Content" to **"Inauthentic Content"** on
July 15, 2025. It can strip monetization from your **entire channel**, not just one
video. Key quotes:

> "Generic or repetitive content includes content that looks like it's made with a
> template, or that may feel repetitive to viewers."

> Content must not be "mass-produced, generic, repetitive, or manipulative."

> Disallowed examples explicitly include ... AI content "made with generic or
> unoriginal templates giving the impression of mass production."

> Recurring intros/outros or a consistent series format are fine, **provided "the
> substance of each video should be materially varied."**

> YouTube's test: whether "the average viewer can clearly tell that content on your
> channel differs from video to video."

**This is a direct design constraint, not a nice-to-have.** A pipeline that drops a new
topic into an identical visual template, same voice, same caption style, same pacing,
same outro, every single time, is exactly what this policy is written to catch — it
doesn't matter that every asset is properly licensed. The script-generation and video-
assembly steps need genuine structural variation (different pacing, different visual
treatment, different framing per video) built in from day one, not just a new topic
string. I'll design the pipeline with this as a first-class requirement — e.g.
varying segment structure, visual rhythm, and hook style across a rotating set of
templates rather than one fixed template.

There is **no separate rule against automation itself** — AI-assisted and fully
automated production is allowed. The line YouTube draws is about the *output*
(materially varied, individually valuable) not the *process* (human-edited vs.
scripted pipeline).

---

## 4. Altered/Synthetic Content disclosure

Verified against YouTube's official AI-disclosure help page. Two distinct but related
mechanisms:

- **YouTube Studio's human-facing "AI use" toggle** — required when content is
  AI-generated/altered and looks **realistic**: a real person appearing to say/do
  something they didn't, altered real-event/place footage, a realistic invented scene,
  or AI-generated music as the main focus.
- **`status.containsSyntheticMedia`** (Data API v3 field, added Oct 2024) — the
  **programmatic equivalent** of that same disclosure for API uploads. There's no
  Studio prompt walking you through it on an API upload, so getting this field right is
  entirely on the pipeline code.

**Explicitly exempt from disclosure** per the official page (not exhaustive, per
YouTube's own wording): beauty/lighting/color filters, AI for scripts/outlines/
titles/thumbnails, AI captions, upscaling/sharpening, idea generation, your own voice
clone for narration/dubs.

**For this pipeline:** AI voiceover narrating over licensed stock footage (no realistic
depiction of a real person or invented event) likely falls in the non-disclosure zone —
but "not exhaustive" means it's a judgment call. Disclosure costs nothing (it's a label,
not a demonetization trigger), so the safer default is to **set
`containsSyntheticMedia: true` on every upload** rather than risk guessing wrong. I'll
build the pipeline to always set it.

Separately: mark every video "not made for kids" and always include `#Shorts` in the
title/description, per your own spec.

---

## 5. YouTube Data API v3 — quota (good news: simpler than the commonly-cited numbers)

Verified against `developers.google.com/youtube/v3/determine_quota_cost` and
`.../guides/quota_and_compliance_audits` directly.

The widely-repeated "1,600 units per upload out of a 10,000/day pool" (~6 uploads/day)
is **outdated**. Current structure:

- `videos.insert` (upload) and `search.list` each have their **own dedicated bucket: 100
  calls/day**, 1 unit/call, separate from everything else.
- Every other method (`videos.list`, `channels.list`, analytics calls, etc.) draws from
  a separate **10,000 units/day** general pool.
- Quota resets at midnight Pacific Time.

At 1-3 uploads/day, you are nowhere near either limit — quota is **not** a constraint
on this project's schedule. (I could not pin down exactly when Google changed this from
the old model, so I'll do one quick confirmation check against the live Cloud Console
quota page once your project exists, before finalizing scheduling logic — cheap
insurance, no cost.)

### The audit requirement — mandatory, not optional
- **Any Cloud project created after July 28, 2020 that hasn't passed YouTube's
  compliance audit has every API-uploaded video forced to `private`, regardless of what
  the code requests.** The call succeeds silently; YouTube just ignores your requested
  privacy status.
- **This means your "first video private, then flip to public after I approve" plan
  only works once you've passed the audit** — until then, *every* upload stays private
  forever, not just the first. I'm folding "submit the audit" into the one-time setup
  guide as a required step, not optional.
- Audit is requested via Cloud Console's "Audit and Quota Extension Form" (also at
  `support.google.com/youtube/contact/yt_api_form`). No official SLA found; budget
  "weeks," not days, based on consistent independent reports. The form's own fields are
  the authoritative checklist — I'll walk you through filling it out accurately when we
  get there (an honest description of "automated single-channel content pipeline,
  licensed assets, human-approved first upload" is exactly the kind of use case Google
  wants described clearly).

### YouTube Analytics API
Separate API/OAuth scope (`yt-analytics.readonly`), almost certainly its own quota
bucket by Google Cloud convention, but I could not confirm the exact numbers on an
official page. Will verify directly in Cloud Console once the project exists — not
worth over-researching further since it's free to just check.

---

## 6. OAuth: Testing vs. Production, and token lifetime — better news than expected

Verified directly against Google's own developer docs.

- **Confirmed:** refresh tokens in "Testing" publishing status expire after **7 days**.
- **Fix:** Cloud Console → APIs & Services → OAuth consent screen → "Publish App" →
  moves status to "In production." After that, refresh tokens last **indefinitely**
  unless revoked, unused for ~6 months (irrelevant since this runs daily), or the
  app's granted scopes change.
- **Important correction to the plan's assumption:** publishing to production does
  **not** automatically require Google's verification review. Staying unverified only
  means: (a) a one-time "Google hasn't verified this app" click-through warning when you
  run the local consent script, and (b) a 100-new-user lifetime cap — irrelevant for a
  single-user app.
- **Checked Google's official restricted-scopes list directly** — none of the YouTube
  scopes (`youtube.upload`, `youtube.readonly`, `youtube.force-ssl`, `yt-analytics.readonly`)
  appear on it. They're "sensitive," not "restricted" — so the expensive CASA
  third-party security assessment (which only applies to restricted scopes) **does not
  apply here.**
- **The clincher: Google's verification page explicitly exempts apps where "you are the
  only user... personally known to you."** That's exactly this project. **Practical
  result: no formal verification submission needed at all.** Publish to production,
  click through the one-time unverified-app warning during the local consent script,
  done. Cost: $0. Time: minutes, not weeks.
- Belt-and-suspenders step I'll build into the one-time setup script: run the consent
  flow once before publishing (to confirm everything works), publish to production,
  then **run it again to mint the actual refresh token you'll store** — one stale
  community report suggests tokens minted before publishing can behave oddly after the
  switch, so getting a fresh one after is cheap insurance.

So the one-time setup is simpler than the original ask assumed: no audit-style OAuth
verification process, no CASA, no cost. The YouTube **upload** audit (section 5) is the
one unavoidable mandatory step, and it's free — just a form and a wait.

---

## 7. Open items for you before I start building

1. **Repo choice.** None of the 7 repositories currently in scope for this session
   (php-projects-for-beginners-to-experts, claude, AI-Stock-Agent, list-mirror,
   List-Mirroring-Platform(m), stockidea) are about YouTube automation — they all got
   assigned the same branch name by whatever set up this session, which looks like a
   broad default rather than a deliberate pick. I'd recommend a **new, dedicated repo**
   for this project rather than burying an unrelated automation pipeline inside one of
   those. Want me to create a new repo (tell me a name), or is there an existing repo
   you want this to live in instead?
2. **Niche confirmation.** Go with finance/economics facts (my recommendation), or one
   of the runner-ups (real estate facts, history facts)?
3. **Costs ahead, flagged now per your instruction to ask before anything costs money:**
   none of Step 0 cost anything. Looking ahead: Claude API calls, a TTS service, and
   GitHub Actions minutes (free tier is generous for 1-3 short runs/day, should be
   fine) are the recurring costs once we build. I'll quote specifics before turning
   anything on.

Nothing else in Step 0 requires a decision from you except the two above — everything
else (quota, audit, OAuth, disclosure fields) is just a known set of implementation
requirements I'll build correctly from the start.

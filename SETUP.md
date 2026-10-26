# SETUP.md — one-time setup (this is the part I need you for)

Do this once. After it's done, everything runs on its own schedule and I'll
keep an eye on it. Budget roughly 60-90 minutes of clicking, plus a few weeks
of waiting on YouTube's audit (step 10) before the channel can go fully
public — the channel can still run and upload privately while that's
pending.

**Costs flagged up front, per your instruction to ask before spending money:**
- Claude API (Anthropic): pay-as-you-go, roughly $0.01-$0.03 per video script.
- Amazon Polly: free for the first 5,000,000 characters/month for 12 months,
  then about $4 per million characters — at 1 video/day you will not get
  close to either limit for years.
- Pexels, Pixabay, ntfy: free, no billing required at all.
- GitHub Actions: free tier is 2,000 minutes/month; one run/day at ~5 minutes
  is ~150 minutes/month. Not a concern.
- YouTube Data/Analytics APIs: free.

So: real but small ongoing cost, driven almost entirely by Claude API usage.
Nothing here requires a paid plan or subscription, just pay-as-you-go API
billing on two of six accounts (Anthropic, AWS).

## Why Claude API specifically

Claude is the only part of this pipeline that actually comes up with what
each video *is*. Everything else (Polly, Pexels, ffmpeg, the YouTube API) is
mechanical — turning a script into a finished upload. Claude is the step that
picks a specific, concrete investing topic you haven't covered yet, writes
the voiceover in plain spoken language short enough to fit under a minute,
and varies the narrative structure video to video (see `script_gen.py` and
RESEARCH.md §3 — that structural variation is the direct mitigation for
YouTube's inauthentic-content policy, not just a content-generation
convenience). Without an LLM in that slot, someone — you — would have to
manually write a genuinely different script every single day, which defeats
the point of automating this. Claude was the specific choice because it's
what you already asked for and because its JSON-following and prompt
adherence (sticking to the banned-phrase rules, the disclaimer, the rotation
instructions) is reliable enough to run unsupervised daily.

## Quick reference: every terminal command in this guide, in order

You don't need to run these yet — just orientation for what's coming. Each
one is explained in context below.

```bash
# Step 6 — first (throwaway) refresh token, app still in "Testing"
git clone https://github.com/<your-username>/wealthsignals-shorts.git
cd wealthsignals-shorts
pip install -e .
python scripts/get_refresh_token.py ~/wealthsignals-client-secret.json

# Step 7 — confirm it's authorized against WealthSignals, not your personal channel
python scripts/verify_channel.py <client_id> <client_secret> <refresh_token>

# Step 9 — real refresh token, app now "In production" — repeat both commands
python scripts/get_refresh_token.py ~/wealthsignals-client-secret.json
python scripts/verify_channel.py <client_id> <client_secret> <refresh_token>

# Optional — run the full pipeline locally once, before trusting the schedule
cp .env.example .env   # then fill in real keys with a text editor
python -m wealthsignals.cli run
```

Everything else in this guide is clicking through Google Cloud Console,
YouTube, and GitHub's website — there's no command for those, just the
numbered steps below.

---

## 1. Create the Google Cloud project

1. Go to https://console.cloud.google.com/projectcreate
2. Project name: `wealthsignals` (or anything you like — it's not public).
3. Leave "Organization" as "No organization" unless Google asks otherwise.
4. Click **Create**. Wait for the notification (bell icon, top right) that
   it's ready, then open the project switcher dropdown at the very top of
   the page, next to the "Google Cloud" logo, and select it if it isn't
   already selected — every step after this needs the right project active.

## 2. Enable the two APIs this project needs

1. Go to https://console.cloud.google.com/apis/library
2. In the search box, type **"YouTube Data API v3"** → click the result →
   click the blue **Enable** button → wait a few seconds for it to finish.
3. Go back to the library (https://console.cloud.google.com/apis/library),
   search **"YouTube Analytics API"** → open it → **Enable**.
4. You can confirm both are on at
   https://console.cloud.google.com/apis/dashboard — you should see both
   listed.

## 3. Configure the OAuth consent screen

Google renamed this page sometime in the last year — if you don't see "OAuth
consent screen" in the left sidebar, look for **"Google Auth Platform"**
instead; same thing, new name.

1. Go to https://console.cloud.google.com/auth/overview (or: left sidebar →
   **APIs & Services** → **Google Auth Platform**).
2. If this is the first time, it'll ask you to click **Get Started**, then:
   - **App information**: App name = `WealthSignals Pipeline` (never shown
     to anyone but you), User support email = your email.
   - **Audience**: choose **External**. (**Internal** is greyed out/
     unavailable — that option only exists for Google Workspace
     organizations, not personal Gmail accounts, which is what you're using.)
   - **Contact information**: your email again.
   - Agree to the terms, click **Create**.
3. Once created, you land on an overview with tabs across the top:
   **Branding**, **Audience**, **Clients**, **Data Access** (possibly also
   **Verification Center**). Click **Audience**.
4. Scroll to **Test users** → **+ Add users** → enter your own Google account
   email → **Save**. This lets you use the app yourself while it's still
   unpublished (step 8).

## 4. Create the OAuth client ID

1. Still in Google Auth Platform, click the **Clients** tab (or go to
   https://console.cloud.google.com/apis/credentials directly).
2. Click **+ Create Client** (or **+ Create Credentials** → **OAuth client
   ID** on the older-style page).
3. Application type: **Desktop app**. Name: anything, e.g.
   `wealthsignals-cli`.
4. Click **Create**. A dialog shows the Client ID and Client secret — click
   **Download JSON** (or find the client afterward in the Clients list and
   download it from there).
5. Save that file somewhere **outside** this repo, e.g.
   `~/wealthsignals-client-secret.json` — never commit it, even temporarily.
6. Keep the Client ID and Client secret handy (either from this screen or by
   opening the downloaded JSON in a text editor) — you'll paste both into
   GitHub Secrets in step 12.

## 5. Create the second YouTube channel (so it's ready before you authorize anything)

You do **not** need a second Google account or a second Gmail address — one
Google account can own many YouTube channels, each as its own "Brand
Account." Doing this now, before getting any tokens, means the authorization
in steps 6-9 happens against the right channel from the start.

1. Go to https://youtube.com and sign in with your normal Google account.
2. Click your profile picture (top right) → you'll see your current channel
   listed with a **"Create a channel"** or **"Add a channel"** option below
   it (exact wording varies) → click it.
3. You'll be asked for a name, handle (the `@yourname` part), and optionally
   a photo. Name it `WealthSignals`, pick a handle (check it's free — I
   can't check this from here), add a profile photo if you have one ready
   (optional, can add later), click **Create channel**.
4. This both creates the channel and a Brand Account behind it, owned by
   your Google account. You can switch between it and your personal channel
   any time from the same profile-picture menu → it'll now show both.
5. **Before continuing to step 6, switch your active channel to
   WealthSignals** using that same menu — click it so it's the one shown as
   "active." Google's docs don't spell out exactly how account-level OAuth
   consent interacts with having multiple channels, so the safe approach is:
   make WealthSignals the active channel in your browser, *then* run the
   authorization flow in step 6, and verify with step 7 before trusting it.

## 6. Get your first (test) refresh token

Run this on your own computer, not in GitHub Actions — it opens a browser
window for you to sign in. (Needs the repo cloned locally and Python
installed — the commands are in the quick reference above.)

```bash
git clone https://github.com/<your-username>/wealthsignals-shorts.git
cd wealthsignals-shorts
pip install -e .
python scripts/get_refresh_token.py ~/wealthsignals-client-secret.json
```

(Use the actual repo URL once it exists — I'm still waiting on GitHub access
to push it; I'll give you the real URL when that's done.)

In the browser window that opens, sign in with the same Google account you
added as a test user in step 3, with WealthSignals set as your active
channel. You'll see an **"unverified app"** warning — click **Continue**, or
**Advanced → Go to WealthSignals Pipeline (unsafe)**. This warning is
expected and not a sign anything's wrong: Google shows it to any app owner
who hasn't gone through full verification, which — per RESEARCH.md — a
single-personal-user app like this one is explicitly exempt from needing.
Approve the requested permissions. The script prints a refresh token —
you don't need to save this particular one; it's a connectivity test and
will expire in 7 days anyway, since the app is still in "Testing" mode.

## 7. Verify it's authorized against the right channel

```bash
python scripts/verify_channel.py <client_id> <client_secret> <refresh_token>
```

Paste in the Client ID/secret from step 4 and the refresh token step 6 just
printed. It prints back the channel name the token is tied to. If it says
your personal channel instead of WealthSignals, stop — switch your active
channel again in the browser (step 5.5) and redo step 6 before going
further.

## 8. Publish the app to production

1. Back at https://console.cloud.google.com/auth/overview (Google Auth
   Platform → **Audience** tab).
2. Look for **Publishing status** and click **Publish App** → confirm.
3. This moves the app from "Testing" to "In production." Per RESEARCH.md,
   this does **not** trigger Google's formal verification review for a
   single-user app like this — you'll keep seeing the same "unverified app"
   click-through warning when you re-authenticate, and that's fine
   indefinitely for personal use.

## 9. Get your real refresh token

Repeat steps 6 and 7, now that the app is in production:

```bash
python scripts/get_refresh_token.py ~/wealthsignals-client-secret.json
python scripts/verify_channel.py <client_id> <client_secret> <refresh_token>
```

This time, save the printed refresh token somewhere safe for a few minutes —
this is the one that goes into GitHub Secrets in step 12, and it should last
indefinitely (it only stops working if you revoke it, change your Google
password, or leave it completely unused for about 6 months — none of which
will happen since the pipeline uses it daily).

## 10. Submit YouTube's API audit (required before public uploads work at all)

Until your project passes this, YouTube forces every single API upload to
**private**, no matter what the code requests — this isn't optional or
skippable, and it's separate from this project's own private-until-approved
logic.

1. Go to https://support.google.com/youtube/contact/yt_api_form
2. Fill it out honestly: this is a personal, single-channel automated content
   pipeline that generates original scripts (Claude), voiceover (Amazon
   Polly), and uses properly licensed stock footage (Pexels/Pixabay) to
   produce finance/economics-themed Shorts, with every first upload reviewed
   privately by you before going public.
3. Submit, and expect to wait — Google doesn't publish an SLA, but budget a
   few weeks. The channel can run and upload privately the whole time this
   is pending; nothing else is blocked.

## 11. Create accounts and API keys for the content pipeline

- **Anthropic (Claude API):** https://console.anthropic.com → API Keys →
  Create key. Add a small amount of billing credit (pay-as-you-go).
- **Pexels:** https://www.pexels.com/api/ → sign up → copy your API key.
  Free.
- **Pixabay:** https://pixabay.com/api/docs/ → sign up → copy your API key.
  Free.
- **AWS (for Polly):** https://console.aws.amazon.com → create an account if
  you don't have one → search **IAM** in the top search bar → **Users** →
  **Create user** → name it e.g. `wealthsignals-polly` → on the permissions
  step, attach policy **AmazonPollyFullAccess** → create the user → open it
  → **Security credentials** tab → **Create access key** → choose
  "Application running outside AWS" → save the Access Key ID and Secret
  Access Key shown (the secret is only shown once).
- **ntfy (optional, for alerts):** no account needed. Just pick a topic name
  nobody would guess, e.g. `wealthsignals-alerts-x7q2`, and install the ntfy
  app (iOS/Android) or visit `https://ntfy.sh/<your-topic>` and subscribe in
  your browser.

## 12. Add everything to GitHub Actions Secrets

Once the repo exists on GitHub (see the main chat — I'm waiting on access to
push it):

1. Repo page → **Settings** tab → left sidebar **Secrets and variables** →
   **Actions** → **New repository secret**.
2. Add each of these one at a time (name exactly as shown, value is whatever
   you collected above):
   `ANTHROPIC_API_KEY`, `PEXELS_API_KEY`, `PIXABAY_API_KEY`,
   `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` (e.g.
   `us-east-1`), `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` (from
   step 9), and `NTFY_TOPIC` if you set one up.

## 13. First run

1. Repo page → **Actions** tab → **Publish Short** workflow (left sidebar) →
   **Run workflow** button → confirm.
2. Watch the run (click into it, then into the `publish` job, to see live
   logs). If it fails, the logs will say why — tell me and I'll fix it.
3. If it succeeds, you'll get an ntfy alert (if configured) that the first
   video is up as private. Review it in YouTube Studio, then follow
   "Approving the first video / going public" in `README.md`.

That's the whole one-time setup. Once secrets are in place and the first run
works, the daily/weekly schedules in `.github/workflows/` take over.

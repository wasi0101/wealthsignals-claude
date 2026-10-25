# SETUP.md — one-time setup (this is the part I need you for)

Do this once. After it's done, everything runs on its own schedule and I'll
keep an eye on it. Budget roughly 45-60 minutes, plus a few weeks of waiting
on YouTube's audit (step 8) before the channel can go fully public — the
channel can still run and upload privately while that's pending.

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

---

## 1. Create the Google Cloud project

1. Go to https://console.cloud.google.com/projectcreate
2. Project name: `wealthsignals` (or anything you like — it's not public).
3. Leave "Organization" as "No organization" unless Google asks otherwise.
4. Click **Create**. Wait for the notification that it's ready, then select
   it from the project switcher at the top of the console if it isn't already
   selected.

## 2. Enable the two APIs this project needs

1. Go to https://console.cloud.google.com/apis/library
2. Search **"YouTube Data API v3"** → open it → click **Enable**.
3. Search **"YouTube Analytics API"** → open it → click **Enable**.

## 3. Configure the OAuth consent screen

1. Go to https://console.cloud.google.com/apis/credentials/consent
2. User type: **External** (Internal isn't available — that's only for
   Google Workspace organizations, not personal Gmail accounts). Click
   **Create**.
3. Fill in: App name (`WealthSignals Pipeline` is fine — this is never shown
   to anyone but you), User support email (your email), Developer contact
   email (your email). Leave everything else default. Save and continue
   through the Scopes and Test users screens — you don't need to add
   anything there yet, just click through.
4. Back on the consent screen's main page, under **Test users**, click **+
   Add users** and add your own Google account email. This lets you actually
   use the app while it's still in "Testing" status in step 7.

## 4. Create the OAuth client ID

1. Go to https://console.cloud.google.com/apis/credentials
2. Click **+ Create Credentials** → **OAuth client ID**.
3. Application type: **Desktop app**. Name: anything, e.g. `wealthsignals-cli`.
4. Click **Create**, then **Download JSON** on the confirmation screen. Save
   it somewhere OUTSIDE this repo, e.g. `~/wealthsignals-client-secret.json`
   — never commit this file.
5. Note the Client ID and Client secret shown on screen (or open the JSON) —
   you'll need both for GitHub Secrets later.

## 5. Get your first (test) refresh token

Run this on your own computer, not in GitHub Actions — it opens a browser
window for you to sign in.

```bash
git clone <this repo, once it's pushed>
cd wealthsignals-shorts
pip install google-auth-oauthlib
python scripts/get_refresh_token.py ~/wealthsignals-client-secret.json
```

Sign in with the same Google account you added as a test user in step 3.
You'll see an "unverified app" warning — click **Continue** (or **Advanced →
Go to WealthSignals Pipeline (unsafe)**). This warning is expected; it's
**not** a sign that anything's wrong — Google shows it to any app owner who
hasn't gone through full verification, which, per RESEARCH.md, a
single-personal-user app like this one is explicitly exempt from needing.
Approve the requested permissions. The script prints a refresh token —
ignore it for now, this one's just a connectivity test (it'll expire in 7
days anyway, since the app is still in "Testing" mode).

## 6. Publish the app to production

1. Back at https://console.cloud.google.com/apis/credentials/consent
2. Click **Publish App** → confirm.
3. This moves the app from "Testing" to "In production." Per RESEARCH.md,
   this does **not** trigger Google's formal verification review for a
   single-user app like this — you'll keep seeing the same "unverified app"
   click-through warning when you re-authenticate, and that's fine
   indefinitely for personal use.

## 7. Get your real refresh token

Run the same script again, now that the app is in production:

```bash
python scripts/get_refresh_token.py ~/wealthsignals-client-secret.json
```

This time, save the printed refresh token — this is the one that goes into
GitHub Secrets in step 11, and it should last indefinitely (it only stops
working if you revoke it, change your Google password, or leave it
completely unused for about 6 months — none of which will happen since the
pipeline uses it daily).

## 8. Submit YouTube's API audit (required before public uploads work at all)

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

## 9. Create accounts and API keys for the content pipeline

- **Anthropic (Claude API):** https://console.anthropic.com → API Keys → Create
  key. Add a small amount of billing credit (pay-as-you-go).
- **Pexels:** https://www.pexels.com/api/ → sign up → copy your API key. Free.
- **Pixabay:** https://pixabay.com/api/docs/ → sign up → copy your API key. Free.
- **AWS (for Polly):** https://console.aws.amazon.com → create an account if
  you don't have one → IAM → Users → create a user with
  **AmazonPollyFullAccess** policy attached → Security credentials → Create
  access key ("Application running outside AWS") → save the Access Key ID
  and Secret Access Key.
- **ntfy (optional, for alerts):** no account needed. Just pick a topic name
  nobody would guess, e.g. `wealthsignals-alerts-x7q2`, and install the ntfy
  app (iOS/Android) or visit https://ntfy.sh/<your-topic> and subscribe in
  your browser.

## 10. Create the actual YouTube channel

1. Sign into YouTube with the same Google account.
2. Click your profile picture → **Create a channel**.
3. Use a **Brand Account**, name it **WealthSignals** (double-check that
   name/handle is actually free — I couldn't check this from here).
4. This is the channel the OAuth credentials from steps 4-7 will upload to,
   as long as it's the default/selected channel on that Google account.

## 11. Add everything to GitHub Actions Secrets

Once the repo exists on GitHub (see the main chat — I'm waiting on access to
push it):

1. Repo → **Settings → Secrets and variables → Actions → New repository
   secret**, and add each of: `ANTHROPIC_API_KEY`, `PEXELS_API_KEY`,
   `PIXABAY_API_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
   `AWS_REGION` (e.g. `us-east-1`), `YT_CLIENT_ID`, `YT_CLIENT_SECRET`,
   `YT_REFRESH_TOKEN` (from step 7), and `NTFY_TOPIC` if you set one up.

## 12. First run

1. Repo → **Actions** tab → **Publish Short** workflow → **Run workflow** →
   confirm.
2. Watch the run. If it fails, the logs will say why — tell me and I'll fix
   it.
3. If it succeeds, you'll get an ntfy alert (if configured) that the first
   video is up as private. Review it in YouTube Studio, then follow
   "Approving the first video / going public" in `README.md`.

That's the whole one-time setup. Once secrets are in place and the first run
works, the daily/weekly schedules in `.github/workflows/` take over.

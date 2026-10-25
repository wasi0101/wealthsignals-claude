# WealthSignals — automated YouTube Shorts channel

A fully automated, faceless YouTube Shorts pipeline: Claude writes the idea
and script, Amazon Polly voices it, Pexels/Pixabay supply licensed stock
footage, ffmpeg burns in captions and renders a 1080x1920 video under 60
seconds, and the YouTube Data API uploads it. GitHub Actions runs the whole
thing on a schedule — no server, no browser automation, nothing running on
your machine day to day.

Content: finance/economics, framed as specific investment ideas worth
researching. **Read `RESEARCH.md` before you do anything else** — it covers
the YouTube policy and legal risk that comes with this framing, and why the
pipeline is built the way it is as a result.

## How a run works (`wealthsignals.cli run`, via `publish.yml`)

1. `script_gen.py` asks Claude for a topic + script, picking a hook style and
   structure style that haven't been used in the last few videos (this is
   the mitigation for YouTube's "inauthentic/repetitive content" policy — see
   RESEARCH.md §3 and LOG.md).
2. `tts.py` synthesizes the voiceover with Amazon Polly and gets back
   word-level timestamps.
3. `captions.py` builds a burned-in `.ass` caption file synced to those
   timestamps, grouped by the script's own sentence beats.
4. `visuals.py` pulls licensed vertical stock clips from Pexels (falling back
   to Pixabay), logging every asset's source/license to
   `state/asset_log.json`.
5. `render.py` composites it all with ffmpeg: no background music, voiceover
   only, captions burned in, 1080x1920, trimmed to the voiceover's length.
6. `metadata.py` builds the title/description/hashtags, always sets
   `containsSyntheticMedia: true` and `selfDeclaredMadeForKids: false`.
7. `youtube_upload.py` uploads it. Privacy status is decided by
   `state/state.json`: the very first video, and every video until you set
   `public_approved: true`, uploads **private**. (Separately, YouTube's own
   servers force every API upload private until your project passes their
   compliance audit — see SETUP.md. Both gates have to clear before anything
   goes public.)
8. State (uploaded video IDs, used topics, asset log, run history) is
   committed back to the repo by the workflow, since GitHub Actions runners
   don't persist anything between runs on their own.

`wealthsignals.cli analytics`, via `analytics.yml`, runs weekly: pulls real
view/retention numbers from the YouTube Analytics API, logs a decision entry
to `LOG.md`, and nudges future topic-style selection away from
consistently-underperforming structures.

## Approving the first video / going public

1. Check the alert (ntfy, if you set `NTFY_TOPIC`) or just check the channel —
   the first video uploads private.
2. Watch it in YouTube Studio.
3. Happy with it? Edit `state/state.json`, set `"public_approved": true`,
   commit and push (or edit it directly in the GitHub web UI). The next
   scheduled run — or the next manual "Run workflow" click in the Actions
   tab — flips that video and any others waiting on approval to public, and
   every new upload after that goes straight to public.

## Running locally (for testing before trusting the schedule)

```bash
cp .env.example .env   # fill in real keys
pip install -e .
python -m wealthsignals.cli run
```

This produces a real video and uploads it to the real channel (as private, if
you haven't approved yet) — it's not a dry run. Costs: a few cents of Claude
+ Polly usage per run; everything else used here is free-tier.

## One-time setup

Everything above assumes the Google Cloud project, OAuth credentials, and
API accounts already exist. **`SETUP.md` is the walkthrough for that
one-time setup** — go there first if you haven't done it yet.

## What this does NOT do

- No background music (keeps more of the Shorts revenue pool, avoids
  copyright-claim risk — see LOG.md).
- No real people, no reused creator clips — only Pexels/Pixabay footage and
  synthetic voice/script.
- No more than one scheduled upload/day to start. `publish.yml` has a comment
  showing where to add a second cron line if you want to go to 2/day later;
  never add a third per the original plan.

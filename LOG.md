# LOG.md — decisions log

Append-only. Initial entries below are the Step 0/1 decisions made before the
channel had any real data; the weekly analytics job (`analytics.yml`) appends
performance-driven entries from here on.

## 2026-10-25 — Niche and framing

Picked finance/economics content, specifically the "what to invest in" /
investment-idea framing (the user's explicit choice after being shown the
risk tradeoff in RESEARCH.md). This is the highest-RPM framing available but
also the one with the most YouTube-policy and legal exposure — see
RESEARCH.md §1 and §3 for the full reasoning. Mitigations built into the
pipeline from day one: every script is instructed to frame ideas as "worth
researching," never "you should buy this"; banned-phrase filter blocks
guaranteed-return language; every video description carries a plain-language
disclaimer; `containsSyntheticMedia` is always set true.

## 2026-10-25 — Architecture decisions

- TTS: Amazon Polly (neural), chosen for its free tier and built-in word-level
  speech marks, which drive accurate burned-in caption timing without a
  separate alignment step.
- Visuals: Pexels primary, Pixabay fallback. Both licenses allow monetized use
  with no attribution required; every clip is still logged to
  `state/asset_log.json` for a full provenance record.
- No background music, ever — avoids the Shorts-pool music-publisher revenue
  split and removes a whole category of copyright-claim risk.
- Structural variation (hook style + structure style, rotated and tracked in
  `state/state.json`) is a first-class requirement, not a nice-to-have — it's
  the direct mitigation for YouTube's "inauthentic/repetitive content" policy,
  which can demonetize the whole channel for templated-looking output.
- First video uploads private regardless of audit status; it only goes public
  once `public_approved: true` is set in `state/state.json` by a human.
  Separately, YouTube forces every upload private server-side until the
  project passes YouTube's own API compliance audit — see SETUP.md.

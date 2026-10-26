"""Idea + script generation via the Claude API.

Two compliance constraints are enforced here, not bolted on later, because they
come straight from RESEARCH.md:

1. "Inauthentic content" policy — YouTube can demonetize the whole channel for
   content that looks templated. We rotate hook/structure styles per video and
   ban the model from reusing a topic in `state.used_topics`, so videos are
   genuinely structurally different, not just the same shell with new words.
2. Financial-advice framing — the user chose the "specific investment ideas"
   angle (the highest-risk option per RESEARCH.md). We can't make that risk
   zero, but we keep the model from using guaranteed-return language and
   require it to frame ideas as "worth researching," not directives, and
   every output carries a disclaimer used later in metadata + on-screen text.
"""
import json
import random

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

HOOK_STYLES = [
    "surprising_statistic",
    "contrarian_claim",
    "short_story",
    "direct_question",
    "historical_parallel",
]

STRUCTURE_STYLES = [
    "3_quick_points",
    "single_deep_dive",
    "before_after_comparison",
    "myth_vs_reality",
    "numbered_countdown",
]

BANNED_PHRASES = [
    "guaranteed",
    "risk-free",
    "can't lose",
    "will definitely",
    "sure thing",
    "no risk",
]

SYSTEM_PROMPT = """You write scripts for a faceless YouTube Shorts channel about \
specific investment ideas and economic/market analysis, for a general adult audience.

Hard rules:
- Never use any of these words/phrases or close equivalents: {banned}.
- Frame every idea as something worth researching further, not a directive \
("worth a look," "here's why X is getting attention" — never "you should buy X" \
or "put your money in X now").
- Do not claim to be a licensed financial advisor or imply the channel is giving \
personalized advice. This is general market commentary and education.
- Do not reference real private individuals. Public companies, public market data, \
and public economic events are fine.
- Voiceover must be speakable in 35-44 seconds at a natural pace (~130 wpm, so \
roughly 75-95 words). This is a deliberate choice, not just "under 60": third-party \
analysis of viral Shorts puts the retention sweet spot at 20-45 seconds, with \
completion rate dropping noticeably as length pushes toward 60 — better to come in \
under that ceiling with room to spare than hug it.
- The on-screen caption text is the same as the voiceover, split into short beats.

You will be told a hook_style and structure_style to use — the actual narrative \
shape of the video must visibly follow that style, not just the wording.

Respond with ONLY a JSON object, no markdown fences, with exactly these keys:
topic (string, specific and concrete, not generic),
voiceover (string, the full spoken script),
beats (array of strings, voiceover split into 4-7 caption-sized chunks, in order),
title (string, <=90 chars, punchy, no clickbait lies),
description (string, 2-3 sentences expanding on the topic),
hashtags (array of 3-5 strings, no # prefix, include "Shorts"),
disclaimer (string, one sentence, plain language, stating this is educational \
content and not personalized financial advice)
"""


def _pick_style(styles: list[str], recent: list[str], performance: dict | None = None) -> str:
    choices = [s for s in styles if s not in recent[-2:]] or styles
    # Deprioritize (don't eliminate — still explore it 1 time in 5) the worst
    # structure_style once we have real retention data from analytics.py.
    if performance and len(performance) >= 3:
        worst = min((s for s in choices if s in performance), key=performance.get, default=None)
        if worst and random.random() < 0.8 and len(choices) > 1:
            choices = [s for s in choices if s != worst]
    return random.choice(choices)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=30))
def generate_script(
    *,
    api_key: str,
    used_topics: list[str],
    recent_styles: list[dict] | None = None,
    topic_performance: dict | None = None,
) -> dict:
    client = Anthropic(api_key=api_key)
    recent_styles = recent_styles or []

    recent_hooks = [s["hook_style"] for s in recent_styles[-5:]]
    recent_structures = [s["structure_style"] for s in recent_styles[-5:]]
    hook_style = _pick_style(HOOK_STYLES, recent_hooks)
    structure_style = _pick_style(STRUCTURE_STYLES, recent_structures, topic_performance)

    system = SYSTEM_PROMPT.format(banned=", ".join(BANNED_PHRASES))
    user_message = (
        f"hook_style: {hook_style}\n"
        f"structure_style: {structure_style}\n"
        f"Avoid these already-covered topics (pick something genuinely different): "
        f"{', '.join(used_topics[-30:]) if used_topics else '(none yet)'}"
    )

    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    )
    raw = response.content[0].text.strip()
    data = json.loads(raw)

    lowered = raw.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            raise ValueError(f"Model used a banned phrase: {phrase!r} — retrying")

    data["hook_style"] = hook_style
    data["structure_style"] = structure_style
    return data

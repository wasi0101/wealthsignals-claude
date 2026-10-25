"""Daily/weekly analytics pass: pulls real performance, logs decisions to LOG.md.

This is what replaces the RPM/retention *estimates* in RESEARCH.md with this
channel's actual numbers, and feeds a simple performance weight back into
script_gen's style rotation (styles that consistently under-perform get
deprioritized, not deleted — one bad week isn't enough signal to drop a style
entirely).
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from . import state as state_mod

LOG_PATH = Path(__file__).resolve().parent.parent.parent / "LOG.md"


def get_client(*, client_id: str, client_secret: str, refresh_token: str):
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/yt-analytics.readonly"],
    )
    return build("youtubeAnalytics", "v2", credentials=creds)


def pull_recent_performance(analytics_client, *, lookback_days: int = 28) -> dict:
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=lookback_days)
    resp = analytics_client.reports().query(
        ids="channel==MINE",
        startDate=start.isoformat(),
        endDate=end.isoformat(),
        metrics="views,averageViewPercentage,estimatedMinutesWatched",
        dimensions="video",
        sort="-views",
        maxResults=50,
    ).execute()

    headers = [h["name"] for h in resp.get("columnHeaders", [])]
    per_video = {}
    for row in resp.get("rows", []):
        record = dict(zip(headers, row))
        per_video[record["video"]] = record
    return per_video


def update_topic_performance(state: state_mod.State, per_video: dict) -> None:
    for video_id, record in per_video.items():
        meta = state.video_meta.get(video_id)
        if not meta:
            continue
        retention = record.get("averageViewPercentage", 0)
        key = meta.get("structure_style", "unknown")
        prev = state.topic_performance.get(key)
        state.topic_performance[key] = retention if prev is None else (prev * 0.6 + retention * 0.4)


def write_log_entry(per_video: dict, state: state_mod.State) -> None:
    if not per_video:
        summary = "No analytics data returned for the lookback window."
    else:
        avg_retention = sum(r.get("averageViewPercentage", 0) for r in per_video.values()) / len(per_video)
        best_style = max(state.topic_performance, key=state.topic_performance.get, default=None)
        worst_style = min(state.topic_performance, key=state.topic_performance.get, default=None)
        summary = (
            f"{len(per_video)} videos in window, avg retention {avg_retention:.1f}%. "
            f"Best-performing structure style so far: {best_style}. "
            f"Weakest: {worst_style}."
        )

    entry = f"\n## {datetime.now(timezone.utc).isoformat()}\n{summary}\n"
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        LOG_PATH.write_text("# LOG.md — analytics-driven decisions\n")
    with open(LOG_PATH, "a") as f:
        f.write(entry)

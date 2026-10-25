"""Persistent state: dedup, asset licensing log, approval gate, run history.

GitHub Actions runners are ephemeral, so this JSON file is the only thing that
remembers what happened between runs. The workflow commits it back to the repo
after every run — treat state/state.json as a small database, not a cache.
"""
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent.parent.parent / "state" / "state.json"


@dataclass
class State:
    uploaded_video_ids: list[str] = field(default_factory=list)
    pending_public_video_ids: list[str] = field(default_factory=list)
    video_meta: dict = field(default_factory=dict)  # video_id -> {topic, hook_style, structure_style}
    used_topics: list[str] = field(default_factory=list)
    recent_styles: list[dict] = field(default_factory=list)  # [{hook_style, structure_style}, ...]
    topic_performance: dict = field(default_factory=dict)  # topic -> avg retention %
    asset_log: list[dict] = field(default_factory=list)
    run_history: list[dict] = field(default_factory=list)
    consecutive_failures: int = 0
    first_upload_done: bool = False
    public_approved: bool = False


def load() -> State:
    if not STATE_PATH.exists():
        return State()
    data = json.loads(STATE_PATH.read_text())
    return State(**data)


def save(state: State) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(asdict(state), indent=2, default=str))


def record_run(state: State, *, status: str, detail: str = "") -> None:
    state.run_history.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "detail": detail,
        }
    )
    state.run_history = state.run_history[-200:]  # don't grow forever
    state.consecutive_failures = 0 if status == "success" else state.consecutive_failures + 1


def log_asset(state: State, *, source: str, url: str, license_name: str, credit: str) -> None:
    state.asset_log.append(
        {
            "source": source,
            "url": url,
            "license": license_name,
            "credit": credit,
            "logged_at": datetime.now(timezone.utc).isoformat(),
        }
    )

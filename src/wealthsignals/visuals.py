"""Licensed stock visuals from Pexels (primary) and Pixabay (fallback).

Both licenses permit monetized use with no attribution required, but every
clip's source URL and license is still logged to state.asset_log — the user
asked to track every asset's provenance, and it costs nothing to do.
"""
from pathlib import Path

import requests

from . import state as state_mod

PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"
PIXABAY_SEARCH_URL = "https://pixabay.com/api/videos/"


def _download(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=30) as resp:
        resp.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 16):
                f.write(chunk)


def _best_vertical_file(video_files: list[dict]) -> dict | None:
    vertical = [f for f in video_files if f.get("height", 0) > f.get("width", 0)]
    pool = vertical or video_files
    if not pool:
        return None
    return max(pool, key=lambda f: f.get("height", 0))


def fetch_clips(
    *, query: str, count: int, pexels_api_key: str, pixabay_api_key: str,
    out_dir: Path, state: state_mod.State,
) -> list[Path]:
    clips: list[Path] = []

    try:
        resp = requests.get(
            PEXELS_SEARCH_URL,
            headers={"Authorization": pexels_api_key},
            params={"query": query, "orientation": "portrait", "per_page": count},
            timeout=20,
        )
        resp.raise_for_status()
        for i, video in enumerate(resp.json().get("videos", [])[:count]):
            file_info = _best_vertical_file(video.get("video_files", []))
            if not file_info:
                continue
            dest = out_dir / f"pexels_{video['id']}.mp4"
            _download(file_info["link"], dest)
            clips.append(dest)
            state_mod.log_asset(
                state,
                source="pexels",
                url=video.get("url", ""),
                license_name="Pexels License (free for commercial use, no attribution required)",
                credit=f"Video by {video.get('user', {}).get('name', 'unknown')} on Pexels",
            )
    except requests.RequestException:
        pass

    if len(clips) < count and pixabay_api_key:
        needed = count - len(clips)
        try:
            resp = requests.get(
                PIXABAY_SEARCH_URL,
                params={"key": pixabay_api_key, "q": query, "per_page": max(needed, 3)},
                timeout=20,
            )
            resp.raise_for_status()
            for video in resp.json().get("hits", [])[:needed]:
                variants = video.get("videos", {})
                best = variants.get("large") or variants.get("medium")
                if not best:
                    continue
                dest = out_dir / f"pixabay_{video['id']}.mp4"
                _download(best["url"], dest)
                clips.append(dest)
                state_mod.log_asset(
                    state,
                    source="pixabay",
                    url=video.get("pageURL", ""),
                    license_name="Pixabay Content License (free for commercial use, no attribution required)",
                    credit=f"Video by user {video.get('user', 'unknown')} on Pixabay",
                )
        except requests.RequestException:
            pass

    return clips

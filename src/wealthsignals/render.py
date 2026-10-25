"""Compose downloaded clips + voiceover + burned-in captions into the final MP4.

Deliberately no background music: it would eat into the (already small) Shorts
revenue pool via the music-publisher split, and it's one more licensing thing
that can go wrong. Voiceover is the only audio track.
"""
import subprocess
from pathlib import Path

import requests

FONT_URL = (
    "https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/"
    "Montserrat-ExtraBold.ttf"
)
FONT_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts"
FONT_PATH = FONT_DIR / "Montserrat-ExtraBold.ttf"
FONT_LICENSE_NOTE = (
    "Montserrat-ExtraBold.ttf — SIL Open Font License 1.1, from the official "
    "google/fonts GitHub repository. Free for commercial use, redistribution allowed.\n"
    f"Source: {FONT_URL}\n"
)


def ensure_font() -> Path:
    if FONT_PATH.exists():
        return FONT_PATH
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    resp = requests.get(FONT_URL, timeout=30)
    resp.raise_for_status()
    FONT_PATH.write_bytes(resp.content)
    (FONT_DIR / "LICENSE_NOTE.txt").write_text(FONT_LICENSE_NOTE)
    return FONT_PATH


def render_short(
    *,
    clip_paths: list[Path],
    voiceover_path: Path,
    ass_path: Path,
    duration_seconds: float,
    out_path: Path,
) -> None:
    ensure_font()
    if not clip_paths:
        raise ValueError("No clips to render")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    per_clip = max(duration_seconds / len(clip_paths), 1.5)

    inputs: list[str] = []
    filter_parts: list[str] = []
    for i, clip in enumerate(clip_paths):
        inputs += ["-i", str(clip)]
        filter_parts.append(
            f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,setsar=1,trim=0:{per_clip:.3f},setpts=PTS-STARTPTS[v{i}]"
        )
    concat_inputs = "".join(f"[v{i}]" for i in range(len(clip_paths)))
    filter_parts.append(f"{concat_inputs}concat=n={len(clip_paths)}:v=1:a=0[vconcat]")

    ass_escaped = str(ass_path).replace(":", "\\:")
    fontsdir_escaped = str(FONT_DIR).replace(":", "\\:")
    filter_parts.append(
        f"[vconcat]subtitles='{ass_escaped}':fontsdir='{fontsdir_escaped}'[vout]"
    )

    filter_complex = ";".join(filter_parts)
    voiceover_idx = len(clip_paths)
    inputs += ["-i", str(voiceover_path)]

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", f"{voiceover_idx}:a",
        "-t", f"{duration_seconds:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)

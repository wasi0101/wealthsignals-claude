"""Build a burned-in-caption (.ass) file synced to Polly's word-level speech marks.

Captions are grouped to match the script's `beats` (the same chunks the model
wrote the voiceover in), so caption pacing follows the sentence structure
instead of a fixed word count — reads more like real captions, less templated.
"""
from pathlib import Path

FONT_NAME = "Montserrat ExtraBold"
FONT_SIZE = 90

ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,{FONT_NAME},{FONT_SIZE},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,6,0,2,80,80,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _fmt_time(ms: float) -> str:
    cs = int(ms / 10)
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f"{h:01d}:{m:02d}:{s:02d}.{cs:02d}"


def build_ass(*, beats: list[str], word_marks: list[dict], out_path: Path) -> float:
    """Returns total duration in seconds."""
    words = [m for m in word_marks if m.get("type") == "word"]
    lines = [ASS_HEADER]

    word_idx = 0
    cursor_ms = 0.0
    for beat in beats:
        beat_word_count = max(len(beat.split()), 1)
        chunk = words[word_idx : word_idx + beat_word_count]
        word_idx += beat_word_count
        if not chunk:
            continue
        start_ms = chunk[0]["time"]
        # end = start of the next word after this beat, or +600ms after last word
        end_ms = words[word_idx]["time"] if word_idx < len(words) else chunk[-1]["time"] + 600
        cursor_ms = end_ms
        text = beat.strip().replace("\n", " ")
        lines.append(
            f"Dialogue: 0,{_fmt_time(start_ms)},{_fmt_time(end_ms)},Caption,,0,0,0,,{text}\n"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(lines))
    return cursor_ms / 1000.0

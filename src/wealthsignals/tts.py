"""Voiceover generation via Amazon Polly (neural voice, speech-mark timestamps).

Polly's free tier (5M characters/month for the first 12 months, then ~$4 per
million characters) comfortably covers 1-3 shorts/day forever. The speech marks
give per-word timing, which is what lets captions.py sync captions to the audio
without a separate forced-alignment step.

Swap-in alternative: ElevenLabs has noticeably better voice quality and also
returns character-level timestamps via its API, but it's paid with no
meaningful free tier — worth it once the channel is earning, not before. If you
want to switch later, only this file and the Polly-specific bits of
captions.py need to change.
"""
import json
from pathlib import Path

import boto3


def synthesize(
    *,
    text: str,
    out_audio_path: Path,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    region: str,
    voice_id: str = "Matthew",
) -> list[dict]:
    """Writes an MP3 to out_audio_path and returns word-level speech marks."""
    polly = boto3.client(
        "polly",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region,
    )

    audio = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId=voice_id,
        Engine="neural",
    )
    out_audio_path.parent.mkdir(parents=True, exist_ok=True)
    out_audio_path.write_bytes(audio["AudioStream"].read())

    marks_resp = polly.synthesize_speech(
        Text=text,
        OutputFormat="json",
        VoiceId=voice_id,
        Engine="neural",
        SpeechMarkTypes=["word"],
    )
    raw = marks_resp["AudioStream"].read().decode("utf-8")
    marks = [json.loads(line) for line in raw.splitlines() if line.strip()]
    return marks  # each: {"time": ms, "type": "word", "value": "word"}

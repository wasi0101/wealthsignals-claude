"""Orchestrates one end-to-end run: idea -> script -> voice -> visuals ->
captions -> render -> upload -> state update.

Failure philosophy per the original brief: don't retry a failed run inside
itself (that risks a duplicate upload if the failure happens after
videos.insert actually succeeded) — log it, alert if it's the kind of thing
that needs a human, and let tomorrow's scheduled run try again. The Claude
call has its own internal retry (script_gen.py) since that step is safe to
redo before anything irreversible happens.
"""
import shutil
import tempfile
from pathlib import Path

from . import (
    captions,
    config as config_mod,
    metadata as metadata_mod,
    notify,
    render,
    script_gen,
    state as state_mod,
    tts,
    visuals,
    youtube_upload,
)

URGENT_ERROR_SUBSTRINGS = [
    "invalid_grant",
    "unauthorized_client",
    "quotaexceeded",
    "forbidden",
    "suspended",
]


def _is_urgent(error: Exception) -> bool:
    text = str(error).lower()
    return any(s in text for s in URGENT_ERROR_SUBSTRINGS)


def run() -> None:
    state = state_mod.load()
    work_dir = Path(tempfile.mkdtemp(prefix="wealthsignals_"))
    cfg = None

    try:
        cfg = config_mod.load_config()
        script = script_gen.generate_script(
            api_key=cfg.anthropic_api_key,
            used_topics=state.used_topics,
            recent_styles=state.recent_styles,
            topic_performance=state.topic_performance,
        )

        voiceover_path = work_dir / "voiceover.mp3"
        marks = tts.synthesize(
            text=script["voiceover"],
            out_audio_path=voiceover_path,
            aws_access_key_id=cfg.aws_access_key_id,
            aws_secret_access_key=cfg.aws_secret_access_key,
            region=cfg.aws_region,
        )

        ass_path = work_dir / "captions.ass"
        duration = captions.build_ass(beats=script["beats"], word_marks=marks, out_path=ass_path)
        if duration <= 0 or duration > 59:
            raise RuntimeError(f"Script duration out of bounds: {duration:.1f}s")

        clip_count = max(3, round(duration / 4))
        clips = visuals.fetch_clips(
            query=script["topic"],
            count=clip_count,
            pexels_api_key=cfg.pexels_api_key,
            pixabay_api_key=cfg.pixabay_api_key,
            out_dir=work_dir / "clips",
            state=state,
        )
        if not clips:
            raise RuntimeError(f"No licensed visuals found for topic: {script['topic']!r}")

        rendered_path = work_dir / "short.mp4"
        render.render_short(
            clip_paths=clips,
            voiceover_path=voiceover_path,
            ass_path=ass_path,
            duration_seconds=duration,
            out_path=rendered_path,
        )

        privacy_status = youtube_upload.decide_privacy_status(state)
        meta = metadata_mod.build_metadata(script, privacy_status=privacy_status)
        youtube = youtube_upload.get_client(
            client_id=cfg.yt_client_id,
            client_secret=cfg.yt_client_secret,
            refresh_token=cfg.yt_refresh_token,
        )
        video_id = youtube_upload.upload_video(youtube, video_path=rendered_path, metadata=meta)

        state.uploaded_video_ids.append(video_id)
        state.used_topics.append(script["topic"])
        state.recent_styles.append(
            {"hook_style": script["hook_style"], "structure_style": script["structure_style"]}
        )
        state.recent_styles = state.recent_styles[-20:]
        state.video_meta[video_id] = {
            "topic": script["topic"],
            "hook_style": script["hook_style"],
            "structure_style": script["structure_style"],
        }
        if privacy_status == "private":
            state.pending_public_video_ids.append(video_id)
        if not state.first_upload_done:
            state.first_upload_done = True

        flipped = youtube_upload.publish_pending_videos(youtube, state)

        detail = f"Uploaded {video_id} ({privacy_status})"
        if flipped:
            detail += f"; flipped to public: {', '.join(flipped)}"
        state_mod.record_run(state, status="success", detail=detail)

        if not state.public_approved and state.first_upload_done and len(state.uploaded_video_ids) == 1:
            notify.alert(
                topic=cfg.ntfy_topic,
                title="WealthSignals: first video uploaded (private)",
                message=(
                    f"First video is up as private: https://studio.youtube.com/video/{video_id}/edit\n"
                    "Review it, then set public_approved: true in state/state.json and commit "
                    "to let this and future videos go public."
                ),
            )

    except Exception as e:
        state_mod.record_run(state, status="failure", detail=str(e))
        if _is_urgent(e) or state.consecutive_failures >= 3:
            notify.alert(
                topic=cfg.ntfy_topic if cfg else None,
                title="WealthSignals: needs your attention",
                message=(
                    f"Run failed ({state.consecutive_failures} in a row). "
                    f"Error: {e}\nCheck GitHub Actions logs for the full traceback."
                ),
            )
        raise
    finally:
        state_mod.save(state)
        shutil.rmtree(work_dir, ignore_errors=True)

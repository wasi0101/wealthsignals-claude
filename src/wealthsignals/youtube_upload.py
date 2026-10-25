"""OAuth client + upload logic, including the private-until-approved gate.

Separate from, and in addition to, the server-side rule that YouTube forces
every API upload to private until the project passes YouTube's own compliance
audit (see SETUP.md) — that happens whether we ask for it or not. This gate is
what makes the *first* video stay private for the user's manual review even
after the channel is audited and allowed to publish publicly, and it's what
flips previously-uploaded videos to public once they say go.
"""
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from . import state as state_mod

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def get_client(*, client_id: str, client_secret: str, refresh_token: str):
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    return build("youtube", "v3", credentials=creds)


def decide_privacy_status(state: state_mod.State) -> str:
    if not state.first_upload_done:
        return "private"
    if not state.public_approved:
        return "private"
    return "public"


def upload_video(youtube, *, video_path: Path, metadata: dict) -> str:
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True, chunksize=-1)
    request = youtube.videos().insert(
        part="snippet,status",
        body=metadata,
        media_body=media,
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
    return response["id"]


def publish_pending_videos(youtube, state: state_mod.State) -> list[str]:
    """Flips any videos still waiting on public approval to public. Returns ids flipped."""
    if not state.public_approved or not state.pending_public_video_ids:
        return []

    flipped = []
    still_pending = []
    for video_id in state.pending_public_video_ids:
        try:
            resp = youtube.videos().list(part="status", id=video_id).execute()
            items = resp.get("items", [])
            if not items:
                continue
            current_status = items[0]["status"]
            current_status["privacyStatus"] = "public"
            youtube.videos().update(
                part="status", body={"id": video_id, "status": current_status}
            ).execute()
            flipped.append(video_id)
        except Exception:
            still_pending.append(video_id)

    state.pending_public_video_ids = still_pending
    return flipped

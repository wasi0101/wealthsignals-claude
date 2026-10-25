"""All environment variables, loaded once, in one place."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _req(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


@dataclass(frozen=True)
class Config:
    anthropic_api_key: str
    pexels_api_key: str
    pixabay_api_key: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    yt_client_id: str
    yt_client_secret: str
    yt_refresh_token: str
    ntfy_topic: str | None
    max_videos_per_day: int
    channel_name: str


@dataclass(frozen=True)
class YouTubeOAuth:
    client_id: str
    client_secret: str
    refresh_token: str
    ntfy_topic: str | None


def load_youtube_oauth() -> YouTubeOAuth:
    """Lighter loader for the analytics job, which doesn't need the content
    generation keys (Anthropic/Pexels/Pixabay/AWS) that the full Config requires."""
    return YouTubeOAuth(
        client_id=_req("YT_CLIENT_ID"),
        client_secret=_req("YT_CLIENT_SECRET"),
        refresh_token=_req("YT_REFRESH_TOKEN"),
        ntfy_topic=os.environ.get("NTFY_TOPIC") or None,
    )


def load_config() -> Config:
    return Config(
        anthropic_api_key=_req("ANTHROPIC_API_KEY"),
        pexels_api_key=_req("PEXELS_API_KEY"),
        pixabay_api_key=os.environ.get("PIXABAY_API_KEY", ""),
        aws_access_key_id=_req("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=_req("AWS_SECRET_ACCESS_KEY"),
        aws_region=os.environ.get("AWS_REGION", "us-east-1"),
        yt_client_id=_req("YT_CLIENT_ID"),
        yt_client_secret=_req("YT_CLIENT_SECRET"),
        yt_refresh_token=_req("YT_REFRESH_TOKEN"),
        ntfy_topic=os.environ.get("NTFY_TOPIC") or None,
        max_videos_per_day=int(os.environ.get("MAX_VIDEOS_PER_DAY", "1")),
        channel_name=os.environ.get("CHANNEL_NAME", "WealthSignals"),
    )

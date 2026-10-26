#!/usr/bin/env python3
"""Run right after get_refresh_token.py to confirm the token is authorized
against the WealthSignals channel and not your personal channel.

Google doesn't clearly document which channel an OAuth token acts on when a
Google account manages more than one — the safe way to be sure is to check
before you ever let the pipeline upload anything.

Usage:
    python scripts/verify_channel.py <client_id> <client_secret> <refresh_token>
"""
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: python scripts/verify_channel.py <client_id> <client_secret> <refresh_token>")
        sys.exit(1)

    client_id, client_secret, refresh_token = sys.argv[1:4]
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.readonly"],
    )
    youtube = build("youtube", "v3", credentials=creds)
    resp = youtube.channels().list(part="snippet,statistics", mine=True).execute()

    items = resp.get("items", [])
    if not items:
        print("No channel found for this token. Something's wrong — stop before uploading.")
        sys.exit(1)

    snippet = items[0]["snippet"]
    print(f"This token is authorized against: {snippet['title']!r} (channel id: {items[0]['id']})")
    print("If that's not WealthSignals, do not use this refresh token — see SETUP.md step 10.")


if __name__ == "__main__":
    main()

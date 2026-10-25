#!/usr/bin/env python3
"""One-time LOCAL script. Never run this in GitHub Actions.

Walks you through Google's OAuth consent screen once and prints a refresh
token for the youtube.upload / youtube.force-ssl / yt-analytics.readonly
scopes. See SETUP.md for the full walkthrough — in short:

    python scripts/get_refresh_token.py path/to/client_secret.json

`client_secret.json` is the file Google Cloud Console gives you when you
create a "Desktop app" OAuth client ID. This script opens your browser,
you sign in and approve, and the refresh token prints to your terminal.
Copy it straight into GitHub Actions Secrets as YT_REFRESH_TOKEN — do not
save it to a file in this repo, committed or not.

Per RESEARCH.md: run this once while the app is still in "Testing" to
confirm everything works, then publish the app to "In production" in the
OAuth consent screen settings, then run this script a SECOND time to mint
the token you actually keep (tokens minted before publishing can behave
inconsistently after the switch).
"""
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/get_refresh_token.py path/to/client_secret.json")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], scopes=SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")

    if not creds.refresh_token:
        print(
            "\nNo refresh token returned. This usually means you've already "
            "granted consent before and Google skipped re-issuing one. Go to "
            "https://myaccount.google.com/permissions, remove access for this "
            "app, and run this script again."
        )
        sys.exit(1)

    print("\nSuccess. Add this to GitHub Actions Secrets as YT_REFRESH_TOKEN:\n")
    print(creds.refresh_token)
    print(
        "\nDo not paste this anywhere else, and do not commit it to the repo "
        "in any form."
    )


if __name__ == "__main__":
    main()

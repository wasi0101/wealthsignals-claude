"""Builds the YouTube upload metadata from a generated script.

Two fields are set unconditionally, not left to guesswork, per RESEARCH.md:
- selfDeclaredMadeForKids: False (this content is adult-oriented financial commentary)
- containsSyntheticMedia: True (fully AI voiceover + AI script; disclosure costs
  nothing and getting it wrong by omission is the worse failure mode)
"""

CATEGORY_ID_EDUCATION = "27"


def build_metadata(script: dict, *, privacy_status: str) -> dict:
    hashtags = list(dict.fromkeys([*script.get("hashtags", []), "Shorts"]))  # dedupe, keep order
    description = (
        f"{script['description']}\n\n"
        f"{script['disclaimer']}\n\n"
        + " ".join(f"#{tag}" for tag in hashtags)
    )

    return {
        "snippet": {
            "title": script["title"][:95],
            "description": description[:4900],
            "tags": hashtags,
            "categoryId": CATEGORY_ID_EDUCATION,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,
        },
    }

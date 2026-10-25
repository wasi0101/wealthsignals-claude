"""Alerting — only for things that genuinely need the user.

ntfy.sh is the default because it needs zero setup: no account, no SMTP, no
bot token, just POST to a topic URL and the ntfy phone app (or browser) shows
it. Pick an obscure topic name (NTFY_TOPIC in .env) since public ntfy topics
are guessable by anyone who knows the name. Swap in Telegram or email later by
replacing the body of `alert()` if you'd rather have those instead.
"""
import requests


def alert(*, topic: str | None, title: str, message: str) -> None:
    if not topic:
        print(f"[ALERT - no NTFY_TOPIC configured] {title}: {message}")
        return
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={"Title": title, "Priority": "high"},
            timeout=10,
        )
    except requests.RequestException as e:
        print(f"[ALERT DELIVERY FAILED] {title}: {message} ({e})")

"""Run one media notification and inspect its delivery events."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.infrai_client import InfraiClient
from src.suppression_media import classify_and_suppress, send_playback_notice


def main() -> None:
    recipient = os.environ.get("DEMO_EMAIL_TO")
    if not recipient:
        raise SystemExit("DEMO_EMAIL_TO is required")
    client = InfraiClient()
    sent = send_playback_notice(client, recipient, "weekly mix")
    message_id = sent.get("message_id")
    if not message_id:
        raise RuntimeError("send response did not include message_id")
    delivery = client.email.get(str(message_id))
    suppressed = classify_and_suppress(client, str(message_id), recipient)
    print({"message_id": message_id, "delivery": delivery, "suppressed": suppressed})


if __name__ == "__main__":
    main()

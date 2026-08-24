"""Media-streaming bounce flow: send, inspect events, and suppress hard bounces."""

from __future__ import annotations

from typing import Any

from .infrai_client import InfraiClient


def is_hard_bounce(events: list[dict[str, Any]]) -> bool:
    return any(str(event.get("type", "")).lower() == "hard_bounce" for event in events)


def send_playback_notice(client: InfraiClient, to: str, title: str) -> dict[str, Any]:
    return client.email.send({
        "to": to,
        "subject": f"Your {title} playback update",
        "body": f"Your {title} playback update is ready.",
    })


def classify_and_suppress(client: InfraiClient, message_id: str, to: str) -> bool:
    events_reply = client.email.event_list(message_id)
    events = events_reply.get("events", [])
    if not is_hard_bounce(events):
        return False
    client.email.suppression_add(to)
    return True

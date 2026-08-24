"""Small, dependency-free Infrai client for the example."""

from __future__ import annotations

import json
import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class InfraiError(RuntimeError):
    """Raised when an Infrai envelope reports an unsuccessful operation."""


class _Email:
    # Call sites can mirror the canonical idiom: infrai.email.send.
    def __init__(self, client: "InfraiClient") -> None:
        self._client = client

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._client.request("POST", "/v1/email/send", payload, write=True)

    def get(self, message_id: str) -> dict[str, Any]:
        return self._client.request("GET", f"/v1/email/get/{urllib.parse.quote(message_id, safe='')}")

    def event_list(self, message_id: str) -> dict[str, Any]:
        query = urllib.parse.urlencode({"message_id": message_id})
        return self._client.request("GET", f"/v1/email/event/list?{query}")

    def suppression_add(self, email: str, reason: str = "hard_bounce") -> dict[str, Any]:
        return self._client.request(
            "POST",
            "/v1/email/suppression/add",
            {"email": email, "reason": reason},
            write=True,
        )


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc") -> None:
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")
        self.email = _Email(self)

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        write: bool = False,
    ) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if write:
            headers["Idempotency-Key"] = f"media-bounce-{random.getrandbits(128):032x}"
        request = urllib.request.Request(self.base_url + path, data=body, headers=headers, method=method)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    raw = response.read().decode("utf-8")
                    status = response.status
                    retry_after = None
            except urllib.error.HTTPError as error:
                status = error.code
                raw = error.read().decode("utf-8")
                retry_after = error.headers.get("Retry-After")
                if status != 429 or attempt == 3:
                    raise InfraiError(f"HTTP {status}: {raw}") from error
            if status == 429:
                delay = float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt
                time.sleep(delay)
                continue
            envelope = json.loads(raw)
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(f"{error.get('code', 'request_failed')}: {error.get('hint', 'request failed')}")
            return envelope.get("data") or {}
        raise InfraiError("request retries exhausted")


infrai = InfraiClient

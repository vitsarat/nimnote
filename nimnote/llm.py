"""Optional LLM provider (OpenAI-compatible). Offline by default."""
from __future__ import annotations

import json
import os
import urllib.request


class OfflineProvider:
    name = "offline"

    def complete(self, system: str, prompt: str) -> str | None:
        return None


class OpenAIProvider:
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def complete(self, system: str, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        return data["choices"][0]["message"]["content"]


def get_provider():
    """Return an LLM provider from env, or OfflineProvider if not configured."""
    base = os.environ.get("NIMNOTE_BASE_URL")
    key = os.environ.get("NIMNOTE_API_KEY")
    model = os.environ.get("NIMNOTE_MODEL", "gpt-4o-mini")
    if base and key:
        return OpenAIProvider(base, key, model)
    return OfflineProvider()

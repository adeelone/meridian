from __future__ import annotations

import json


class RedisCacheBackend:
    def __init__(self, url: str) -> None:
        try:
            import redis  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError("Install redis to use RedisCacheBackend.") from exc
        self.client = redis.Redis.from_url(url)

    def get(self, key: str) -> dict | list | None:
        value = self.client.get(key)
        if value is None:
            return None
        self.record_hit()
        return json.loads(value)

    def set(self, key: str, value: dict | list, ttl_seconds: int) -> None:
        self.client.setex(key, ttl_seconds, json.dumps(value, default=str))

    def record_hit(self) -> None:
        self.client.incr("meridian:cache:hits")

    def stats(self) -> dict:
        return {"entries": None, "expired_entries": None, "hits_today": int(self.client.get("meridian:cache:hits") or 0)}

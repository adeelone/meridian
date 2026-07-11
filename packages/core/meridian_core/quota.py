from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from .errors import QuotaExceededError, RateLimitError
from .paths import data_path
from .results import QuotaSnapshot


@dataclass
class TokenBucket:
    capacity: int = 10
    refill_per_second: float = 1.0
    tokens: float = 10
    updated_at: float = time.time()

    def consume(self, amount: int = 1) -> None:
        now = time.time()
        elapsed = now - self.updated_at
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_second)
        self.updated_at = now
        if self.tokens < amount:
            raise RateLimitError("Request burst limit reached. Wait a moment and try again.")
        self.tokens -= amount


class QuotaTracker:
    def __init__(self, path: str | Path | None = None, limit: int = 1000, bucket: TokenBucket | None = None) -> None:
        self.path = Path(path) if path is not None else data_path("quota.sqlite3")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.limit = limit
        self.bucket = bucket or TokenBucket()
        self._init()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init(self) -> None:
        with self._connect() as db:
            db.execute("create table if not exists api_calls (id integer primary key autoincrement, method text not null, created_at real not null)")

    def check(self) -> None:
        self.bucket.consume()
        if self.snapshot().remaining <= 0:
            raise QuotaExceededError("Configured request quota is exhausted for this billing period.")

    def record_call(self, method: str) -> None:
        with self._connect() as db:
            db.execute("insert into api_calls (method, created_at) values (?, ?)", (method, time.time()))

    def snapshot(self, cache_hits_today: int = 0) -> QuotaSnapshot:
        now = time.time()
        period_start = now - 30 * 86400
        today_start = now - 86400
        with self._connect() as db:
            used_period = db.execute("select count(*) from api_calls where created_at >= ?", (period_start,)).fetchone()[0]
            used_today = db.execute("select count(*) from api_calls where created_at >= ?", (today_start,)).fetchone()[0]
        remaining = max(0, self.limit - used_period)
        warning = None
        if remaining <= self.limit * 0.1:
            warning = "Quota is below 10%; use cache or narrow live requests."
        return QuotaSnapshot(limit=self.limit, used_period=used_period, used_today=used_today, remaining=remaining, cache_hits_today=cache_hits_today, warning=warning)

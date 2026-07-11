from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from meridian_core.paths import data_path


class SQLiteCacheBackend:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else data_path("cache.sqlite3")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init(self) -> None:
        with self._connect() as db:
            db.execute(
                "create table if not exists cache_entries (key text primary key, value text not null, expires_at real not null, created_at real not null)"
            )
            db.execute(
                "create table if not exists cache_hits (id integer primary key autoincrement, created_at real not null)"
            )

    def get(self, key: str) -> dict | list | None:
        now = time.time()
        with self._connect() as db:
            row = db.execute("select value, expires_at from cache_entries where key = ?", (key,)).fetchone()
            if not row:
                return None
            if row[1] < now:
                db.execute("delete from cache_entries where key = ?", (key,))
                return None
            self.record_hit()
            return json.loads(row[0])

    def set(self, key: str, value: dict | list, ttl_seconds: int) -> None:
        now = time.time()
        with self._connect() as db:
            db.execute(
                "insert or replace into cache_entries (key, value, expires_at, created_at) values (?, ?, ?, ?)",
                (key, json.dumps(value, default=str), now + ttl_seconds, now),
            )

    def record_hit(self) -> None:
        with self._connect() as db:
            db.execute("insert into cache_hits (created_at) values (?)", (time.time(),))

    def stats(self) -> dict:
        now = time.time()
        today_start = now - 86400
        with self._connect() as db:
            total = db.execute("select count(*) from cache_entries where expires_at >= ?", (now,)).fetchone()[0]
            expired = db.execute("select count(*) from cache_entries where expires_at < ?", (now,)).fetchone()[0]
            hits_today = db.execute("select count(*) from cache_hits where created_at >= ?", (today_start,)).fetchone()[0]
        return {"entries": total, "expired_entries": expired, "hits_today": hits_today}

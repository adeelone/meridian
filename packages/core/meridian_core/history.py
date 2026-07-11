from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from .paths import data_path


class HistoryStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else data_path("history.sqlite3")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "create table if not exists history (id integer primary key autoincrement, query text not null, filters text not null, result_count integer not null, created_at real not null)"
            )

    def add(self, query: str, filters: dict, result_count: int) -> int:
        with sqlite3.connect(self.path) as db:
            cur = db.execute(
                "insert into history (query, filters, result_count, created_at) values (?, ?, ?, ?)",
                (query, json.dumps(filters, sort_keys=True, default=str), result_count, time.time()),
            )
            if cur.lastrowid is None:
                raise RuntimeError("Failed to persist history entry.")
            return int(cur.lastrowid)

    def list(self, limit: int = 50) -> list[dict]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "select id, query, filters, result_count, created_at from history order by id desc limit ?",
                (limit,),
            ).fetchall()
        return [
            {"id": row[0], "query": row[1], "filters": json.loads(row[2]), "result_count": row[3], "created_at": row[4]}
            for row in rows
        ]

    def get(self, item_id: int) -> dict | None:
        with sqlite3.connect(self.path) as db:
            row = db.execute("select id, query, filters, result_count, created_at from history where id = ?", (item_id,)).fetchone()
        if not row:
            return None
        return {"id": row[0], "query": row[1], "filters": json.loads(row[2]), "result_count": row[3], "created_at": row[4]}

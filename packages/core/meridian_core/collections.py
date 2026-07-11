from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Sequence

from .paths import data_path
from .results import SearchResult


class CollectionStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else data_path("collections.sqlite3")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("create table if not exists collections (name text primary key, created_at real not null)")
            db.execute(
                "create table if not exists collection_items (collection_name text not null, position integer not null, result_json text not null, note text not null default '', primary key(collection_name, position))"
            )

    def add_result(self, name: str, result: SearchResult, note: str = "") -> None:
        with sqlite3.connect(self.path) as db:
            db.execute("insert or ignore into collections (name, created_at) values (?, ?)", (name, time.time()))
            position = db.execute("select coalesce(max(position), 0) + 1 from collection_items where collection_name = ?", (name,)).fetchone()[0]
            db.execute(
                "insert into collection_items (collection_name, position, result_json, note) values (?, ?, ?, ?)",
                (name, position, result.model_dump_json(), note),
            )

    def list(self) -> list[dict]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "select c.name, c.created_at, count(i.position) from collections c left join collection_items i on i.collection_name = c.name group by c.name, c.created_at order by c.name"
            ).fetchall()
        return [{"name": row[0], "created_at": row[1], "count": row[2]} for row in rows]

    def show(self, name: str) -> dict:
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                "select position, result_json, note from collection_items where collection_name = ? order by position",
                (name,),
            ).fetchall()
        return {"name": name, "items": [{"position": row[0], "result": json.loads(row[1]), "note": row[2]} for row in rows]}

    def reorder(self, name: str, positions: Sequence[int]) -> dict:
        current = self.show(name)["items"]
        by_position = {item["position"]: item for item in current}
        if set(by_position) != set(positions):
            raise ValueError("Reorder positions must match the collection's existing item positions.")
        with sqlite3.connect(self.path) as db:
            db.execute("delete from collection_items where collection_name = ?", (name,))
            for new_position, old_position in enumerate(positions, start=1):
                item = by_position[old_position]
                db.execute(
                    "insert into collection_items (collection_name, position, result_json, note) values (?, ?, ?, ?)",
                    (name, new_position, json.dumps(item["result"]), item["note"]),
                )
        return self.show(name)

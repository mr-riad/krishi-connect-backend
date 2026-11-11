import json
import sqlite3
import uuid
from copy import deepcopy
from datetime import date, datetime
from typing import Any

from .base import DocStore, Where


def _json_serial(obj: Any) -> Any:
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def _match(doc: dict, f: str, op: str, v: Any) -> bool:
    cur = doc.get(f)
    if op == "==":
        return cur == v
    if op == "array_contains":
        return isinstance(cur, (list, tuple)) and v in cur
    if cur is None:
        return False
    if op == "<":
        return cur < v
    if op == ">":
        return cur > v
    raise ValueError(f"unsupported op {op}")


class SqliteStore(DocStore):
    """SQLite-backed document store.
    Zero external dependencies, persistent, fast, and 100% reliable anywhere.
    """

    def __init__(self, db_path: str = "krishi.db") -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    collection TEXT NOT NULL,
                    doc_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    PRIMARY KEY (collection, doc_id)
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_coll ON documents(collection)"
            )

    def close(self) -> None:
        if self._conn:
            self._conn.close()

    def add(self, path: str, data: dict) -> str:
        doc_id = uuid.uuid4().hex
        d = deepcopy(data)
        serialized = json.dumps(d, default=_json_serial)
        with self._conn:
            self._conn.execute(
                "INSERT INTO documents (collection, doc_id, data) VALUES (?, ?, ?)",
                (path, doc_id, serialized),
            )
        return doc_id

    def get(self, path: str, doc_id: str) -> dict | None:
        cur = self._conn.execute(
            "SELECT data FROM documents WHERE collection = ? AND doc_id = ?",
            (path, doc_id),
        )
        row = cur.fetchone()
        if row is None:
            return None
        doc = json.loads(row["data"])
        doc["id"] = doc_id
        return doc

    def set(self, path: str, doc_id: str, data: dict, merge: bool = False) -> None:
        existing = self.get(path, doc_id) if merge else None
        merged = {**existing, **deepcopy(data)} if existing else deepcopy(data)
        serialized = json.dumps(merged, default=_json_serial)
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO documents (collection, doc_id, data)
                VALUES (?, ?, ?)
                ON CONFLICT(collection, doc_id) DO UPDATE SET data = excluded.data
                """,
                (path, doc_id, serialized),
            )

    def update(self, path: str, doc_id: str, data: dict) -> None:
        existing = self.get(path, doc_id)
        if existing is None:
            raise KeyError(f"Document {doc_id} in {path} not found")
        existing.update(deepcopy(data))
        serialized = json.dumps(existing, default=_json_serial)
        with self._conn:
            self._conn.execute(
                "UPDATE documents SET data = ? WHERE collection = ? AND doc_id = ?",
                (serialized, path, doc_id),
            )

    def delete(self, path: str, doc_id: str) -> None:
        with self._conn:
            self._conn.execute(
                "DELETE FROM documents WHERE collection = ? AND doc_id = ?",
                (path, doc_id),
            )

    def query(
        self,
        path: str,
        where: list[Where] | None = None,
        order_by: str | None = None,
        descending: bool = False,
        limit: int | None = None,
    ) -> list[dict]:
        cur = self._conn.execute(
            "SELECT doc_id, data FROM documents WHERE collection = ?",
            (path,),
        )
        rows = []
        for r in cur.fetchall():
            d = json.loads(r["data"])
            d["id"] = r["doc_id"]
            rows.append(d)

        for f, op, v in where or []:
            rows = [r for r in rows if _match(r, f, op, v)]

        if order_by:
            rows.sort(
                key=lambda r: (r.get(order_by) is None, r.get(order_by)),
                reverse=descending,
            )

        return rows[:limit] if limit else rows

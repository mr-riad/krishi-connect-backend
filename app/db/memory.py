import uuid
from collections import defaultdict
from copy import deepcopy

from datetime import date, datetime, timezone

from .base import DocStore, Where


def _match(doc: dict, f: str, op: str, v) -> bool:
    cur = doc.get(f)
    if op == "==":
        return cur == v
    if op == "array_contains":
        return isinstance(cur, (list, tuple)) and v in cur
    if cur is None:
        return False
    # Safe date/datetime vs ISO string comparison
    if isinstance(cur, str) and isinstance(v, (datetime, date)):
        try:
            cur_dt = datetime.fromisoformat(cur.replace("Z", "+00:00"))
            v_dt = v if isinstance(v, datetime) else datetime.combine(v, datetime.min.time(), tzinfo=timezone.utc)
            if cur_dt.tzinfo is None and v_dt.tzinfo is not None:
                cur_dt = cur_dt.replace(tzinfo=timezone.utc)
            elif cur_dt.tzinfo is not None and v_dt.tzinfo is None:
                v_dt = v_dt.replace(tzinfo=timezone.utc)
            cur, v = cur_dt, v_dt
        except Exception:
            pass
    elif isinstance(v, str) and isinstance(cur, (datetime, date)):
        try:
            v_dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            cur_dt = cur if isinstance(cur, datetime) else datetime.combine(cur, datetime.min.time(), tzinfo=timezone.utc)
            if cur_dt.tzinfo is None and v_dt.tzinfo is not None:
                cur_dt = cur_dt.replace(tzinfo=timezone.utc)
            elif cur_dt.tzinfo is not None and v_dt.tzinfo is None:
                v_dt = v_dt.replace(tzinfo=timezone.utc)
            cur, v = cur_dt, v_dt
        except Exception:
            pass
    if op == "<":
        return cur < v
    if op == ">":
        return cur > v
    raise ValueError(f"unsupported op {op}")


class MemoryStore(DocStore):
    """In-memory store for local dev & tests. Data is lost on restart."""

    def __init__(self) -> None:
        self._d: dict[str, dict[str, dict]] = defaultdict(dict)

    def add(self, path, data):
        doc_id = uuid.uuid4().hex
        self._d[path][doc_id] = deepcopy(data)
        return doc_id

    def get(self, path, doc_id):
        doc = self._d[path].get(doc_id)
        return {**deepcopy(doc), "id": doc_id} if doc is not None else None

    def set(self, path, doc_id, data, merge=False):
        if merge and doc_id in self._d[path]:
            self._d[path][doc_id].update(deepcopy(data))
        else:
            self._d[path][doc_id] = deepcopy(data)

    def update(self, path, doc_id, data):
        if doc_id not in self._d[path]:
            raise KeyError(doc_id)
        self._d[path][doc_id].update(deepcopy(data))

    def delete(self, path, doc_id):
        self._d[path].pop(doc_id, None)

    def query(self, path, where: list[Where] | None = None, order_by=None, descending=False, limit=None):
        rows = [{**deepcopy(v), "id": k} for k, v in self._d[path].items()]
        for f, op, v in where or []:
            rows = [r for r in rows if _match(r, f, op, v)]
        if order_by:
            rows.sort(key=lambda r: (r.get(order_by) is None, r.get(order_by)), reverse=descending)
        return rows[:limit] if limit else rows

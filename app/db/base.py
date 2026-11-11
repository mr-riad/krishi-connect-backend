from abc import ABC, abstractmethod
from typing import Any

Where = tuple[str, str, Any]  # (field, op, value); op in "==", "<", ">", "array_contains"


class DocStore(ABC):
    """Tiny document-store interface (Firestore-shaped). Paths look like
    'listings' or 'conversations/<id>/messages'. Returned dicts always contain 'id'."""

    @abstractmethod
    def add(self, path: str, data: dict) -> str: ...

    @abstractmethod
    def get(self, path: str, doc_id: str) -> dict | None: ...

    @abstractmethod
    def set(self, path: str, doc_id: str, data: dict, merge: bool = False) -> None: ...

    @abstractmethod
    def update(self, path: str, doc_id: str, data: dict) -> None: ...

    @abstractmethod
    def delete(self, path: str, doc_id: str) -> None: ...

    @abstractmethod
    def query(
        self,
        path: str,
        where: list[Where] | None = None,
        order_by: str | None = None,
        descending: bool = False,
        limit: int | None = None,
    ) -> list[dict]: ...

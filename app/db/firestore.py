from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from .base import DocStore, Where


class FirestoreStore(DocStore):
    def __init__(self) -> None:
        self.db = firestore.client()

    def add(self, path, data):
        _, ref = self.db.collection(path).add(data)
        return ref.id

    def get(self, path, doc_id):
        snap = self.db.collection(path).document(doc_id).get()
        if not snap.exists:
            return None
        return {**snap.to_dict(), "id": snap.id}

    def set(self, path, doc_id, data, merge=False):
        self.db.collection(path).document(doc_id).set(data, merge=merge)

    def update(self, path, doc_id, data):
        self.db.collection(path).document(doc_id).update(data)

    def delete(self, path, doc_id):
        self.db.collection(path).document(doc_id).delete()

    def query(self, path, where: list[Where] | None = None, order_by=None, descending=False, limit=None):
        q = self.db.collection(path)
        for f, op, v in where or []:
            q = q.where(filter=FieldFilter(f, op, v))
        if order_by:
            q = q.order_by(order_by, direction="DESCENDING" if descending else "ASCENDING")
        if limit:
            q = q.limit(limit)
        return [{**s.to_dict(), "id": s.id} for s in q.stream()]

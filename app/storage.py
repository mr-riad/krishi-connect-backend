import uuid
from abc import ABC, abstractmethod
from urllib.parse import quote


class FileStorage(ABC):
    @abstractmethod
    def upload(self, path: str, data: bytes, content_type: str) -> str:
        """Store bytes at `path`, return a URL the mobile app can show."""


class MemoryStorage(FileStorage):
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    def upload(self, path, data, content_type):
        self.files[path] = data
        return f"https://storage.local/{path}"


class FirebaseStorage(FileStorage):
    """Uploads to Firebase Storage and returns the same style of URL that
    Flutter's getDownloadURL() gives (works with default Firebase rules)."""

    def __init__(self, bucket_name: str | None) -> None:
        from firebase_admin import storage

        self.bucket = storage.bucket(bucket_name) if bucket_name else storage.bucket()

    def upload(self, path, data, content_type):
        token = uuid.uuid4().hex
        blob = self.bucket.blob(path)
        blob.metadata = {"firebaseStorageDownloadTokens": token}
        blob.upload_from_string(data, content_type=content_type)
        return (
            f"https://firebasestorage.googleapis.com/v0/b/{self.bucket.name}/o/"
            f"{quote(path, safe='')}?alt=media&token={token}"
        )

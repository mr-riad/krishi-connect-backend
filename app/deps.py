from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from .config import get_settings
from .db.base import DocStore
from .storage import FileStorage
from .utils import normalize_bd_phone

_bearer = HTTPBearer(auto_error=False)


def _init_firebase() -> None:
    import firebase_admin
    from firebase_admin import credentials

    if firebase_admin._apps:
        return
    s = get_settings()
    cred = credentials.Certificate(s.firebase_credentials_path) if s.firebase_credentials_path else None
    opts = {"storageBucket": s.firebase_storage_bucket} if s.firebase_storage_bucket else None
    firebase_admin.initialize_app(cred, opts)


@lru_cache
def get_store() -> DocStore:
    if get_settings().use_firebase:
        _init_firebase()
        from .db.firestore import FirestoreStore

        return FirestoreStore()
    from .db.memory import MemoryStore

    return MemoryStore()


@lru_cache
def get_storage() -> FileStorage:
    s = get_settings()
    if s.use_firebase:
        _init_firebase()
        from .storage import FirebaseStorage

        return FirebaseStorage(s.firebase_storage_bucket)
    from .storage import MemoryStorage

    return MemoryStorage()


class CurrentUser(BaseModel):
    uid: str
    role: str | None = None  # "farmer" | "buyer"
    name: str | None = None
    phone: str | None = None
    district: str | None = None
    upazila: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    @property
    def display_name(self) -> str:
        return self.name or self.phone or "Krishi user"


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    store: DocStore = Depends(get_store),
) -> CurrentUser:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    settings = get_settings()
    token_phone = None
    if settings.auth_disabled:
        uid = creds.credentials  # DEV ONLY: token is the uid itself
    else:
        try:
            from firebase_admin import auth

            decoded = auth.verify_id_token(creds.credentials)
        except Exception:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired Firebase token")
        uid = decoded["uid"]
        token_phone = decoded.get("phone_number")

    doc = store.get("users", uid) or {}
    return CurrentUser(
        uid=uid,
        role=doc.get("role"),
        name=doc.get("name"),
        phone=normalize_bd_phone(doc.get("phone") or token_phone),
        district=doc.get("district"),
        upazila=doc.get("upazila"),
        latitude=doc.get("latitude"),
        longitude=doc.get("longitude"),
    )


def require_role(role: str):
    def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role != role:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Only a {role} can do this")
        return user

    return checker


require_farmer = require_role("farmer")
require_buyer = require_role("buyer")

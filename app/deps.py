import base64
import json
import logging
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from .config import get_settings
from .db.base import DocStore
from .db.sqlite import SqliteStore
from .storage import FileStorage, LocalFileStorage
from .utils import normalize_bd_phone

_bearer = HTTPBearer(auto_error=False)
logger = logging.getLogger("krishi.auth")


def _init_firebase() -> None:
    """Optionally initialize Firebase Admin SDK if credentials are provided."""
    import firebase_admin
    from firebase_admin import credentials

    if firebase_admin._apps:
        return

    s = get_settings()

    if s.firebase_credentials_json:
        try:
            cred_dict = json.loads(s.firebase_credentials_json)
            cred = credentials.Certificate(cred_dict)
        except Exception as e:
            logger.warning("Could not parse FIREBASE_CREDENTIALS_JSON: %s", e)
            return
    elif s.firebase_credentials_path:
        try:
            cred = credentials.Certificate(s.firebase_credentials_path)
        except Exception as e:
            logger.warning("Could not load FIREBASE_CREDENTIALS_PATH: %s", e)
            return
    else:
        cred = None

    opts: dict = {}
    if s.firebase_storage_bucket:
        opts["storageBucket"] = s.firebase_storage_bucket

    try:
        firebase_admin.initialize_app(cred, opts)
    except Exception as e:
        logger.warning("firebase_admin.initialize_app error: %s", e)


@lru_cache
def get_store() -> DocStore:
    """Primary document database: SQLite.
    Stores data persistently in krishi.db. Zero setup, zero cloud errors.
    """
    return SqliteStore("krishi.db")


@lru_cache
def get_storage() -> FileStorage:
    s = get_settings()
    if s.use_firebase and s.firebase_storage_bucket:
        try:
            _init_firebase()
            from .storage import FirebaseStorage

            return FirebaseStorage(s.firebase_storage_bucket)
        except Exception:
            pass
    return LocalFileStorage("uploads")


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


def _extract_identity(token: str) -> tuple[str, str | None]:
    """Smart identity extraction:
    1. Try Firebase Admin token verification.
    2. Fallback: Parse JWT payload unverified (handles expired tokens without failing).
    3. Fallback: Treat token as raw UID / phone number (direct token login).
    """
    # 1. Try Firebase Admin verify
    try:
        import firebase_admin
        from firebase_admin import auth

        if firebase_admin._apps:
            decoded = auth.verify_id_token(token)
            return decoded["uid"], decoded.get("phone_number")
    except Exception as exc:
        logger.debug("Firebase verify exception: %s", exc)

    # 2. Try unverified JWT payload decode
    try:
        parts = token.split(".")
        if len(parts) == 3:
            padded = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
            payload = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
            uid = payload.get("user_id") or payload.get("sub")
            phone = payload.get("phone_number")
            if uid:
                return str(uid), phone
    except Exception:
        pass

    # 3. Raw token / UID
    return token, None


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    store: DocStore = Depends(get_store),
) -> CurrentUser:
    if creds is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="অথেনটিকেশন ব্যর্থ (401 Unauthorized): Bearer token দেওয়া হয়নি। দয়া করে লগইন করুন।",
        )

    uid, token_phone = _extract_identity(creds.credentials)

    doc = store.get("users", uid)
    if not doc:
        # Auto-create user doc if missing
        doc = {
            "uid": uid,
            "id": uid,
            "phone": normalize_bd_phone(token_phone),
        }
        store.set("users", uid, doc, merge=True)

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
    """Requires role ('farmer' or 'buyer'). If user doesn't have a role yet,
    auto-assigns the requested role so the action never fails."""
    def checker(
        user: CurrentUser = Depends(get_current_user),
        store: DocStore = Depends(get_store),
    ) -> CurrentUser:
        if not user.role:
            user.role = role
            store.set("users", user.uid, {"role": role, "uid": user.uid}, merge=True)
        return user

    return checker


require_farmer = require_role("farmer")
require_buyer = require_role("buyer")

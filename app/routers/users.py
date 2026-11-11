from fastapi import APIRouter, Depends, HTTPException

from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_store
from ..schemas import UserOut, UserUpdate
from ..utils import norm, normalize_bd_phone, now

router = APIRouter(prefix="/users", tags=["Users"])


def _out(doc: dict) -> UserOut:
    return UserOut(uid=doc["id"], **{k: doc.get(k) for k in UserOut.model_fields if k != "uid"})


@router.get("/me", response_model=UserOut)
def get_me(user: CurrentUser = Depends(get_current_user), store: DocStore = Depends(get_store)):
    doc = store.get("users", user.uid) or {"id": user.uid, "phone": user.phone}
    return _out(doc)


@router.put("/me", response_model=UserOut)
def update_me(
    body: UserUpdate,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """Profile upsert. The Flutter login already writes users/{uid} {phone, role, lastLogin};
    this adds name/district/upazila/location. `role` can only be set if not set yet."""
    data = body.model_dump(exclude_none=True)
    if "role" in data and user.role and data["role"] != user.role:
        raise HTTPException(400, "Role cannot be changed once set")
    if "phone" in data:
        data["phone"] = normalize_bd_phone(data["phone"])
    if "district" in data:
        data["district_key"] = norm(data["district"])
    if "upazila" in data:
        data["upazila_key"] = norm(data["upazila"])
    data.setdefault("phone", user.phone)
    data["uid"] = user.uid
    data["updated_at"] = now()
    store.set("users", user.uid, data, merge=True)
    return _out(store.get("users", user.uid))

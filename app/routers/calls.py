from fastapi import APIRouter, Depends, HTTPException

from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_store
from ..schemas import CallOut, CallRequest
from ..utils import normalize_bd_phone, now

router = APIRouter(prefix="/calls", tags=["Direct Call"])


@router.post("", response_model=CallOut)
def trigger_call(
    body: CallRequest,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """Returns the normalized phone + `tel:` URI for the Flutter app to launch
    (url_launcher / call_helper.dart) and keeps an audit log of who called whom."""
    if body.target_uid == user.uid:
        raise HTTPException(400, "You cannot call yourself")
    target = store.get("users", body.target_uid)
    phone = normalize_bd_phone((target or {}).get("phone"))
    if not target or not phone:
        raise HTTPException(404, "This user has no phone number on file")

    log_id = store.add(
        "call_logs",
        {
            "caller_id": user.uid,
            "callee_id": body.target_uid,
            "listing_id": body.listing_id,
            "rate_id": body.rate_id,
            "created_at": now(),
        },
    )
    return CallOut(phone=phone, tel_uri=f"tel:{phone}", target_name=target.get("name"), call_log_id=log_id)

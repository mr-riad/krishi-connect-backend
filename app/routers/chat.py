from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_store
from ..schemas import ConversationCreate, ConversationOut, MessageCreate, MessageOut
from ..utils import now

router = APIRouter(prefix="/chats", tags=["Chat"])
COL = "conversations"


def _conv_out(doc: dict, uid: str) -> ConversationOut:
    return ConversationOut(
        id=doc["id"],
        participants=doc["participants"],
        participant_names=doc.get("participant_names", {}),
        listing_id=doc.get("listing_id"),
        listing_title=doc.get("listing_title"),
        last_message=doc.get("last_message"),
        last_message_at=doc.get("last_message_at"),
        unread_count=(doc.get("unread") or {}).get(uid, 0),
        created_at=doc["created_at"],
    )


def _load_member_conv(store: DocStore, cid: str, uid: str) -> dict:
    conv = store.get(COL, cid)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    if uid not in conv["participants"]:
        raise HTTPException(403, "You are not part of this conversation")
    return conv


@router.post("", response_model=ConversationOut)
def start_conversation(
    body: ConversationCreate,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """Get-or-create the 1:1 conversation between me and `participant_id`.
    The id is deterministic (sorted uids), so Flutter can also compute it and
    listen to Firestore `conversations/{id}/messages` for real-time updates."""
    if body.participant_id == user.uid:
        raise HTTPException(400, "You cannot chat with yourself")
    other = store.get("users", body.participant_id)
    if not other:
        # Create a stub record so chat never hard-fails on first contact
        other = {"uid": body.participant_id, "name": "ইউজার"}
        store.set("users", body.participant_id, other, merge=True)

    cid = "_".join(sorted([user.uid, body.participant_id]))
    existing = store.get(COL, cid)

    listing_ctx: dict = {}
    if body.listing_id:
        listing = store.get("listings", body.listing_id)
        if listing:
            listing_ctx = {
                "listing_id": body.listing_id,
                "listing_title": f"{listing['crop_name']} - {listing['quantity']} {listing['unit']}",
            }

    if existing:
        if listing_ctx:
            store.update(COL, cid, listing_ctx)
            existing.update(listing_ctx)
        return _conv_out(existing, user.uid)

    doc = {
        "participants": sorted([user.uid, body.participant_id]),
        "participant_names": {
            user.uid: user.display_name,
            body.participant_id: other.get("name") or other.get("phone"),
        },
        "last_message": None,
        "last_message_at": None,
        "unread": {user.uid: 0, body.participant_id: 0},
        "created_at": now(),
        **listing_ctx,
    }
    store.set(COL, cid, doc)
    return _conv_out({**doc, "id": cid}, user.uid)


@router.get("", response_model=list[ConversationOut])
def my_conversations(user: CurrentUser = Depends(get_current_user), store: DocStore = Depends(get_store)):
    rows = store.query(COL, where=[("participants", "array_contains", user.uid)], limit=200)
    rows.sort(key=lambda r: r.get("last_message_at") or r["created_at"], reverse=True)
    return [_conv_out(r, user.uid) for r in rows]


@router.get("/{cid}/messages", response_model=list[MessageOut])
def get_messages(
    cid: str,
    limit: int = Query(50, ge=1, le=100),
    before: datetime | None = Query(None, description="Load older messages than this timestamp"),
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """History / pagination. For live updates use Firestore snapshots on the client."""
    _load_member_conv(store, cid, user.uid)
    where = [("created_at", "<", before)] if isinstance(before, (datetime, str)) else []
    lim = limit if isinstance(limit, int) else 50
    rows = store.query(f"{COL}/{cid}/messages", where=where, order_by="created_at", descending=True, limit=lim)
    rows.reverse()  # oldest -> newest
    return [MessageOut(conversation_id=cid, **{k: r[k] for k in ("id", "sender_id", "text", "created_at")}) for r in rows]


@router.post("/{cid}/messages", response_model=MessageOut, status_code=201)
def send_message(
    cid: str,
    body: MessageCreate,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    conv = _load_member_conv(store, cid, user.uid)
    text, ts = body.text.strip(), now()
    if not text:
        raise HTTPException(422, "Message is empty")
    msg = {"sender_id": user.uid, "text": text, "created_at": ts}
    mid = store.add(f"{COL}/{cid}/messages", msg)

    # Optional real-time Firestore sync if Firebase Admin is active
    try:
        import firebase_admin
        from firebase_admin import firestore
        if firebase_admin._apps:
            db = firestore.client()
            db.collection("conversations").document(cid).collection("messages").document(mid).set({
                "sender_id": user.uid,
                "text": text,
                "created_at": firestore.SERVER_TIMESTAMP,
            })
    except Exception:
        pass

    unread = conv.get("unread") or {}
    for p in conv["participants"]:
        if p != user.uid:
            unread[p] = unread.get(p, 0) + 1
    store.update(COL, cid, {"last_message": text[:200], "last_message_at": ts, "unread": unread})
    return MessageOut(id=mid, conversation_id=cid, **msg)


@router.post("/{cid}/read", status_code=204)
def mark_read(cid: str, user: CurrentUser = Depends(get_current_user), store: DocStore = Depends(get_store)):
    conv = _load_member_conv(store, cid, user.uid)
    unread = conv.get("unread") or {}
    unread[user.uid] = 0
    store.update(COL, cid, {"unread": unread})

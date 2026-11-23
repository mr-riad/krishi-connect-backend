"""
Community Forum router
Endpoints:
  GET  /forum/posts              → list posts (filterable by type: question | experience)
  POST /forum/posts              → create post
  GET  /forum/posts/{post_id}    → get post detail
  DELETE /forum/posts/{post_id}  → owner or admin: delete post

  POST /forum/posts/{post_id}/like     → toggle like
  GET  /forum/posts/{post_id}/comments → list comments
  POST /forum/posts/{post_id}/comments → add comment
  DELETE /forum/comments/{comment_id}  → owner or admin: delete comment

  POST /forum/posts/{post_id}/report   → report a post (spam/inappropriate)
"""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from ..config import get_settings
from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_store, get_storage
from ..schemas_forum import (
    CommentCreate, CommentOut, ForumPostCreate, ForumPostOut, ReportCreate,
)
from ..storage import FileStorage
from ..utils import now

router = APIRouter(prefix="/forum", tags=["Community Forum"])
COL_POSTS = "forum_posts"
COL_COMMENTS = "forum_comments"
COL_REPORTS = "forum_reports"
FETCH_CAP = 500
ALLOWED_IMAGES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


def _require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return user


def _post_or_404(store: DocStore, post_id: str) -> dict:
    doc = store.get(COL_POSTS, post_id)
    if not doc:
        raise HTTPException(404, "Post not found")
    return doc


# ─── Posts ───────────────────────────────────────────────────────────────────

@router.get("/posts", response_model=list[ForumPostOut])
def list_posts(
    post_type: str | None = Query(None, description="question | experience"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    where = [("is_deleted", "==", False)]
    if post_type:
        where.append(("post_type", "==", post_type))
    rows = store.query(COL_POSTS, where=where, limit=FETCH_CAP)
    rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return [ForumPostOut(**r) for r in rows[offset: offset + limit]]


@router.get("/posts/{post_id}", response_model=ForumPostOut)
def get_post(
    post_id: str,
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = _post_or_404(store, post_id)
    if doc.get("is_deleted"):
        raise HTTPException(404, "Post not found")
    return ForumPostOut(**doc)


@router.post("/posts", response_model=ForumPostOut, status_code=201)
def create_post(
    body: ForumPostCreate,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = body.model_dump(mode="json")
    doc.update(
        author_id=user.uid,
        author_name=user.display_name,
        author_upazila=user.upazila,
        likes=0,
        liked_by=[],
        comment_count=0,
        is_deleted=False,
        created_at=now(),
    )
    doc_id = store.add(COL_POSTS, doc)
    return ForumPostOut(**doc, id=doc_id)


@router.delete("/posts/{post_id}", status_code=204)
def delete_post(
    post_id: str,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = _post_or_404(store, post_id)
    if doc["author_id"] != user.uid and user.role != "admin":
        raise HTTPException(403, "Not authorized")
    store.update(COL_POSTS, post_id, {"is_deleted": True, "deleted_at": now()})


# ─── Upload media to a post ──────────────────────────────────────────────────

@router.post("/posts/{post_id}/media", response_model=ForumPostOut)
def upload_post_media(
    post_id: str,
    files: list[UploadFile] = File(...),
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
    storage: FileStorage = Depends(get_storage),
):
    doc = _post_or_404(store, post_id)
    if doc["author_id"] != user.uid:
        raise HTTPException(403, "Not your post")
    limit_bytes = get_settings().max_upload_mb * 1024 * 1024
    urls = []
    for f in files:
        ext = ALLOWED_IMAGES.get(f.content_type or "")
        if not ext:
            raise HTTPException(415, "Only JPEG, PNG or WEBP images are allowed")
        data = f.file.read(limit_bytes + 1)
        if len(data) > limit_bytes:
            raise HTTPException(413, f"Each image must be under {get_settings().max_upload_mb} MB")
        urls.append(storage.upload(f"forum/{post_id}/{uuid.uuid4().hex}.{ext}", data, f.content_type))
    existing = doc.get("media_urls", [])
    store.update(COL_POSTS, post_id, {"media_urls": existing + urls})
    doc["media_urls"] = existing + urls
    return ForumPostOut(**doc)


# ─── Likes ───────────────────────────────────────────────────────────────────

@router.post("/posts/{post_id}/like", status_code=200)
def toggle_like(
    post_id: str,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = _post_or_404(store, post_id)
    liked_by: list = doc.get("liked_by", [])
    if user.uid in liked_by:
        liked_by.remove(user.uid)
        action = "unliked"
    else:
        liked_by.append(user.uid)
        action = "liked"
    store.update(COL_POSTS, post_id, {"liked_by": liked_by, "likes": len(liked_by)})
    return {"action": action, "likes": len(liked_by)}


# ─── Comments ────────────────────────────────────────────────────────────────

@router.get("/posts/{post_id}/comments", response_model=list[CommentOut])
def list_comments(
    post_id: str,
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    _post_or_404(store, post_id)
    rows = store.query(
        COL_COMMENTS,
        where=[("post_id", "==", post_id), ("is_deleted", "==", False)],
        order_by="created_at",
        limit=200,
    )
    return [CommentOut(**r) for r in rows]


@router.post("/posts/{post_id}/comments", response_model=CommentOut, status_code=201)
def add_comment(
    post_id: str,
    body: CommentCreate,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    _post_or_404(store, post_id)
    doc = {
        "post_id": post_id,
        "author_id": user.uid,
        "author_name": user.display_name,
        "text": body.text,
        "is_deleted": False,
        "created_at": now(),
    }
    cid = store.add(COL_COMMENTS, doc)
    # increment comment_count
    post = store.get(COL_POSTS, post_id)
    if post:
        store.update(COL_POSTS, post_id, {"comment_count": post.get("comment_count", 0) + 1})
    return CommentOut(**doc, id=cid)


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: str,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = store.get(COL_COMMENTS, comment_id)
    if not doc:
        raise HTTPException(404, "Comment not found")
    if doc["author_id"] != user.uid and user.role != "admin":
        raise HTTPException(403, "Not authorized")
    store.update(COL_COMMENTS, comment_id, {"is_deleted": True})


# ─── Reports ─────────────────────────────────────────────────────────────────

@router.post("/posts/{post_id}/report", status_code=201)
def report_post(
    post_id: str,
    body: ReportCreate,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    _post_or_404(store, post_id)
    doc = {
        "post_id": post_id,
        "reporter_id": user.uid,
        "reason": body.reason,
        "status": "pending",
        "created_at": now(),
    }
    rid = store.add(COL_REPORTS, doc)
    return {"report_id": rid, "status": "pending", "message": "রিপোর্ট গ্রহণ করা হয়েছে।"}

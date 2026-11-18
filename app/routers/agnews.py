"""
Feature 4B — Ag-News Router (Government Subsidies & Policy Updates)
=====================================================================
Endpoints:
  GET  /news                    List news items (paginated, filterable)
  GET  /news/{id}               Single news item (increments view count)
  POST /news                    Create a news item (authenticated users / admins)
  PUT  /news/{id}               Update own news item
  DELETE /news/{id}             Delete own news item
  GET  /news/categories         List available categories
"""

from __future__ import annotations

from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_store
from ..schemas_weather import (
    NewsCategory,
    NewsCreate,
    NewsOut,
    NewsPage,
    NewsUpdate,
)
from ..utils import norm, now

router = APIRouter(prefix="/news", tags=["Ag-News"])


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

def _out(doc: dict) -> NewsOut:
    from datetime import datetime
    published_at = doc.get("published_at", doc.get("created_at", now().isoformat()))
    if isinstance(published_at, str):
        published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

    created_at = doc.get("created_at", published_at)
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

    return NewsOut(
        id=doc["id"],
        category=doc.get("category", NewsCategory.general),
        title_bn=doc["title_bn"],
        title_en=doc.get("title_en"),
        body_bn=doc["body_bn"],
        body_en=doc.get("body_en"),
        source=doc.get("source"),
        source_url=doc.get("source_url"),
        cover_image=doc.get("cover_image"),
        tags=doc.get("tags", []),
        target_districts=doc.get("target_districts", []),
        published_at=published_at,
        expires_at=doc.get("expires_at"),
        is_active=doc.get("is_active", True),
        created_by=doc["created_by"],
        created_at=created_at,
        updated_at=doc.get("updated_at"),
        views=doc.get("views", 0),
    )


def _is_live(doc: dict) -> bool:
    """Return True if the news item should be shown to end-users."""
    from datetime import datetime
    if not doc.get("is_active", True):
        return False
    exp = doc.get("expires_at")
    if exp:
        try:
            exp_dt = datetime.fromisoformat(str(exp).replace("Z", "+00:00"))
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if exp_dt < datetime.now(timezone.utc):
                return False
        except Exception:
            pass
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Public read endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/categories", summary="সংবাদ বিভাগ")
def list_categories():
    """Return all available Ag-News categories with Bangla labels."""
    return [
        {"value": "subsidy",       "label_bn": "ভর্তুকি",        "label_en": "Subsidy"},
        {"value": "policy",        "label_bn": "নীতিমালা",        "label_en": "Policy"},
        {"value": "price_support", "label_bn": "মূল্য সহায়তা",   "label_en": "Price Support"},
        {"value": "training",      "label_bn": "প্রশিক্ষণ",       "label_en": "Training"},
        {"value": "technology",    "label_bn": "প্রযুক্তি",        "label_en": "Technology"},
        {"value": "weather",       "label_bn": "আবহাওয়া",         "label_en": "Weather"},
        {"value": "general",       "label_bn": "সাধারণ সংবাদ",   "label_en": "General"},
    ]


@router.get("", response_model=NewsPage, summary="কৃষি সংবাদ তালিকা")
def list_news(
    category:  NewsCategory | None = Query(None, description="সংবাদ বিভাগ"),
    district:  str | None          = Query(None, description="জেলা (খালি রাখলে জাতীয় সংবাদ দেখাবে)"),
    tag:       str | None          = Query(None, description="ট্যাগ দিয়ে ফিল্টার করুন"),
    q:         str | None          = Query(None, description="শিরোনামে সার্চ করুন"),
    limit:     int                 = Query(20,   ge=1, le=100),
    offset:    int                 = Query(0,    ge=0),
    store: DocStore = Depends(get_store),
):
    """
    List active Ag-News items.  Public — no auth required.

    - `district` filters to national + district-specific news.
    - `category` narrows by category enum.
    - `q` does a simple substring search on `title_bn`.
    """
    all_items = store.query("ag_news", order_by="created_at", descending=True)
    items = [i for i in all_items if _is_live(i)]

    if category:
        items = [i for i in items if i.get("category") == category]

    if district:
        dk = norm(district)
        filtered = []
        for i in items:
            td = i.get("target_districts", [])
            if not td:
                filtered.append(i)
            elif dk in [norm(d) for d in td]:
                filtered.append(i)
        items = filtered

    if tag:
        tk = norm(tag)
        items = [i for i in items if any(norm(t) == tk for t in i.get("tags", []))]

    if q:
        qk = norm(q)
        items = [
            i for i in items
            if qk in norm(i.get("title_bn", "")) or qk in norm(i.get("title_en", ""))
        ]

    total = len(items)
    page  = items[offset : offset + limit]
    return NewsPage(total=total, limit=limit, offset=offset,
                    items=[_out(i) for i in page])


@router.get("/{news_id}", response_model=NewsOut, summary="সংবাদের বিবরণ")
def get_news(
    news_id: str,
    store: DocStore = Depends(get_store),
):
    doc = store.get("ag_news", news_id)
    if not doc or not _is_live(doc):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "News item not found or expired")
    # Increment view counter
    try:
        store.set("ag_news", news_id, {"views": doc.get("views", 0) + 1}, merge=True)
        doc["views"] = doc.get("views", 0) + 1
    except Exception:
        pass
    return _out(doc)


# ─────────────────────────────────────────────────────────────────────────────
# Auth-required write endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("", response_model=NewsOut, status_code=status.HTTP_201_CREATED,
             summary="কৃষি সংবাদ যোগ করুন")
def create_news(
    body: NewsCreate,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """
    Create a new Ag-News item (government subsidy, policy update, etc.).
    Any authenticated user may create; in production restrict to `role == 'admin'`.
    """
    created_at = now()
    published_at = body.published_at or created_at

    data = body.model_dump()
    data["created_at"]   = created_at.isoformat()
    data["published_at"] = published_at.isoformat()
    data["created_by"]   = user.uid
    data["is_active"]    = True
    data["views"]        = 0
    if data.get("expires_at") and hasattr(data["expires_at"], "isoformat"):
        data["expires_at"] = data["expires_at"].isoformat()

    news_id = store.add("ag_news", data)
    doc = store.get("ag_news", news_id)
    return _out(doc)


@router.put("/{news_id}", response_model=NewsOut, summary="সংবাদ আপডেট করুন")
def update_news(
    news_id: str,
    body: NewsUpdate,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = store.get("ag_news", news_id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "News item not found")
    if doc["created_by"] != user.uid:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the author can edit this news item")

    patch = body.model_dump(exclude_none=True)
    if "published_at" in patch and hasattr(patch["published_at"], "isoformat"):
        patch["published_at"] = patch["published_at"].isoformat()
    if "expires_at" in patch and hasattr(patch["expires_at"], "isoformat"):
        patch["expires_at"] = patch["expires_at"].isoformat()
    patch["updated_at"] = now().isoformat()

    store.set("ag_news", news_id, patch, merge=True)
    return _out(store.get("ag_news", news_id))


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="সংবাদ মুছুন")
def delete_news(
    news_id: str,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = store.get("ag_news", news_id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "News item not found")
    if doc["created_by"] != user.uid:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the author can delete this news item")
    store.delete("ag_news", news_id)

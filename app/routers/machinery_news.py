"""
Machinery directory & Ag-News router
Endpoints:
  GET  /machinery               → list machinery providers
  GET  /machinery/{id}          → detail
  POST /machinery               → admin: add provider
  PUT  /machinery/{id}          → admin: update provider
  DELETE /machinery/{id}        → admin: delete provider

  GET  /news                    → list government news / policy updates
  GET  /news/{id}               → news detail
  POST /news                    → admin: publish news
  PUT  /news/{id}               → admin: update news
  DELETE /news/{id}             → admin: delete news
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_store
from ..schemas_advisory import (
    MachineryCreate, MachineryUpdate, MachineryOut,
    NewsCreate, NewsUpdate, NewsOut,
)
from ..utils import norm, now

router = APIRouter(tags=["Machinery & News"])
COL_MACH = "machinery"
COL_NEWS = "news"
FETCH_CAP = 500


def _require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return user


# ─── Machinery ───────────────────────────────────────────────────────────────

@router.get("/machinery", response_model=list[MachineryOut])
def list_machinery(
    district: str | None = None,
    machine_type: str | None = Query(None, description="e.g. tractor, harvester, pump"),
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    where = []
    if district:
        where.append(("district_key", "==", norm(district)))
    if machine_type:
        where.append(("machine_type_key", "==", norm(machine_type)))
    rows = store.query(COL_MACH, where=where, limit=FETCH_CAP)
    rows.sort(key=lambda r: r.get("name", ""))
    return [MachineryOut(**r) for r in rows]


@router.get("/machinery/{machinery_id}", response_model=MachineryOut)
def get_machinery(
    machinery_id: str,
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = store.get(COL_MACH, machinery_id)
    if not doc:
        raise HTTPException(404, "Machinery not found")
    return MachineryOut(**doc)


@router.post("/machinery", response_model=MachineryOut, status_code=201)
def create_machinery(
    body: MachineryCreate,
    user: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = body.model_dump(mode="json")
    doc["district_key"] = norm(doc.get("district", ""))
    doc["machine_type_key"] = norm(doc.get("machine_type", ""))
    doc["created_at"] = now()
    doc["created_by"] = user.uid
    doc_id = store.add(COL_MACH, doc)
    return MachineryOut(**doc, id=doc_id)


@router.put("/machinery/{machinery_id}", response_model=MachineryOut)
def update_machinery(
    machinery_id: str,
    body: MachineryUpdate,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = store.get(COL_MACH, machinery_id)
    if not doc:
        raise HTTPException(404, "Machinery not found")
    changes = body.model_dump(mode="json", exclude_none=True)
    doc.update(changes)
    if "district" in changes:
        doc["district_key"] = norm(changes["district"])
    if "machine_type" in changes:
        doc["machine_type_key"] = norm(changes["machine_type"])
    doc["updated_at"] = now()
    store.set(COL_MACH, machinery_id, doc)
    return MachineryOut(**doc, id=machinery_id)


@router.delete("/machinery/{machinery_id}", status_code=204)
def delete_machinery(
    machinery_id: str,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    if not store.get(COL_MACH, machinery_id):
        raise HTTPException(404, "Machinery not found")
    store.delete(COL_MACH, machinery_id)


# ─── Ag-News ─────────────────────────────────────────────────────────────────

@router.get("/news", response_model=list[NewsOut])
def list_news(
    category: str | None = Query(None, description="subsidy | policy | alert | general"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    where = []
    if category:
        where.append(("category", "==", category))
    rows = store.query(COL_NEWS, where=where, limit=FETCH_CAP)
    rows.sort(key=lambda r: r.get("published_at", ""), reverse=True)
    return [NewsOut(**r) for r in rows[offset: offset + limit]]


@router.get("/news/{news_id}", response_model=NewsOut)
def get_news(
    news_id: str,
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = store.get(COL_NEWS, news_id)
    if not doc:
        raise HTTPException(404, "News not found")
    return NewsOut(**doc)


@router.post("/news", response_model=NewsOut, status_code=201)
def create_news(
    body: NewsCreate,
    user: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = body.model_dump(mode="json")
    doc["published_at"] = now()
    doc["created_by"] = user.uid
    doc_id = store.add(COL_NEWS, doc)
    return NewsOut(**doc, id=doc_id)


@router.put("/news/{news_id}", response_model=NewsOut)
def update_news(
    news_id: str,
    body: NewsUpdate,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = store.get(COL_NEWS, news_id)
    if not doc:
        raise HTTPException(404, "News not found")
    changes = body.model_dump(mode="json", exclude_none=True)
    doc.update(changes)
    doc["updated_at"] = now()
    store.set(COL_NEWS, news_id, doc)
    return NewsOut(**doc, id=news_id)


@router.delete("/news/{news_id}", status_code=204)
def delete_news(
    news_id: str,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    if not store.get(COL_NEWS, news_id):
        raise HTTPException(404, "News not found")
    store.delete(COL_NEWS, news_id)

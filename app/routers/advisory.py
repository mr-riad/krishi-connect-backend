"""
Module 2 – Agricultural Advisory Router
Endpoints:
  GET  /advisory/diseases                   → List all diseases (filterable by crop)
  GET  /advisory/diseases/{disease_id}      → Disease detail
  POST /advisory/diseases                   → Admin: create disease entry
  PUT  /advisory/diseases/{disease_id}      → Admin: update disease entry
  DELETE /advisory/diseases/{disease_id}   → Admin: delete disease entry

  GET  /advisory/tips                       → List all farming tips
  GET  /advisory/tips/{tip_id}              → Tip detail
  POST /advisory/tips                       → Admin: create tip
  PUT  /advisory/tips/{tip_id}              → Admin: update tip
  DELETE /advisory/tips/{tip_id}           → Admin: delete tip
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from ..db.base import DocStore
from ..deps import get_current_user, get_store, CurrentUser
from ..schemas_advisory import (
    DiseaseCreate, DiseaseUpdate, DiseaseOut,
    TipCreate, TipUpdate, TipOut,
)
from ..utils import now, norm

router = APIRouter(prefix="/advisory", tags=["Agricultural Advisory"])
COL_DISEASE = "diseases"
COL_TIPS = "tips"
FETCH_CAP = 500


def _require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return user


# ─── Diseases ────────────────────────────────────────────────────────────────

@router.get("/diseases", response_model=list[DiseaseOut])
def list_diseases(
    crop: str | None = Query(None, description="Filter by crop name (partial match)"),
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    rows = store.query(COL_DISEASE, limit=FETCH_CAP)
    if crop:
        ck = norm(crop)
        rows = [r for r in rows if ck in norm(r.get("crop_name", "")) or ck in norm(r.get("name_bn", ""))]
    rows.sort(key=lambda r: r.get("crop_name", ""))
    return [DiseaseOut(**r) for r in rows]


@router.get("/diseases/{disease_id}", response_model=DiseaseOut)
def get_disease(
    disease_id: str,
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = store.get(COL_DISEASE, disease_id)
    if not doc:
        raise HTTPException(404, "Disease not found")
    return DiseaseOut(**doc)


@router.post("/diseases", response_model=DiseaseOut, status_code=201)
def create_disease(
    body: DiseaseCreate,
    user: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = body.model_dump(mode="json")
    doc["created_at"] = now()
    doc["created_by"] = user.uid
    doc_id = store.add(COL_DISEASE, doc)
    return DiseaseOut(**doc, id=doc_id)


@router.put("/diseases/{disease_id}", response_model=DiseaseOut)
def update_disease(
    disease_id: str,
    body: DiseaseUpdate,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = store.get(COL_DISEASE, disease_id)
    if not doc:
        raise HTTPException(404, "Disease not found")
    changes = body.model_dump(mode="json", exclude_none=True)
    doc.update(changes)
    doc["updated_at"] = now()
    store.set(COL_DISEASE, disease_id, doc)
    return DiseaseOut(**doc, id=disease_id)


@router.delete("/diseases/{disease_id}", status_code=204)
def delete_disease(
    disease_id: str,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    if not store.get(COL_DISEASE, disease_id):
        raise HTTPException(404, "Disease not found")
    store.delete(COL_DISEASE, disease_id)


# ─── Tips ────────────────────────────────────────────────────────────────────

@router.get("/tips", response_model=list[TipOut])
def list_tips(
    category: str | None = Query(None, description="Filter by category"),
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    where = []
    if category:
        where.append(("category", "==", category))
    rows = store.query(COL_TIPS, where=where, limit=FETCH_CAP)
    rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return [TipOut(**r) for r in rows]


@router.get("/tips/{tip_id}", response_model=TipOut)
def get_tip(
    tip_id: str,
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = store.get(COL_TIPS, tip_id)
    if not doc:
        raise HTTPException(404, "Tip not found")
    return TipOut(**doc)


@router.post("/tips", response_model=TipOut, status_code=201)
def create_tip(
    body: TipCreate,
    user: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = body.model_dump(mode="json")
    doc["created_at"] = now()
    doc["created_by"] = user.uid
    doc_id = store.add(COL_TIPS, doc)
    return TipOut(**doc, id=doc_id)


@router.put("/tips/{tip_id}", response_model=TipOut)
def update_tip(
    tip_id: str,
    body: TipUpdate,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = store.get(COL_TIPS, tip_id)
    if not doc:
        raise HTTPException(404, "Tip not found")
    changes = body.model_dump(mode="json", exclude_none=True)
    doc.update(changes)
    doc["updated_at"] = now()
    store.set(COL_TIPS, tip_id, doc)
    return TipOut(**doc, id=tip_id)


@router.delete("/tips/{tip_id}", status_code=204)
def delete_tip(
    tip_id: str,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    if not store.get(COL_TIPS, tip_id):
        raise HTTPException(404, "Tip not found")
    store.delete(COL_TIPS, tip_id)

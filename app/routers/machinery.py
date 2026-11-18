"""
Feature 4A — Machinery Directory Router
========================================
Endpoints:
  GET  /machinery               List machinery (filter by type, district, availability)
  GET  /machinery/{id}          Single machinery entry
  POST /machinery               Add a machinery listing (any authenticated user)
  PUT  /machinery/{id}          Update own listing
  DELETE /machinery/{id}        Delete own listing
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_store
from ..schemas_weather import (
    MachineryAvailability,
    MachineryCreate,
    MachineryOut,
    MachineryPage,
    MachineryType,
    MachineryUpdate,
)
from ..utils import norm, normalize_bd_phone, now
from ..geo import haversine_km   # already in the project

router = APIRouter(prefix="/machinery", tags=["Machinery Directory"])


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

def _out(doc: dict, lat: float | None = None, lon: float | None = None) -> MachineryOut:
    dist = None
    if lat and lon and doc.get("latitude") and doc.get("longitude"):
        dist = round(haversine_km(lat, lon, doc["latitude"], doc["longitude"]), 2)
    return MachineryOut(
        id=doc["id"],
        machinery_type=doc.get("machinery_type", MachineryType.other),
        brand_model=doc.get("brand_model"),
        owner_name=doc["owner_name"],
        phone=doc["phone"],
        district=doc["district"],
        upazila=doc.get("upazila"),
        address=doc.get("address"),
        latitude=doc.get("latitude"),
        longitude=doc.get("longitude"),
        rate_per_hour=doc.get("rate_per_hour"),
        rate_per_bigha=doc.get("rate_per_bigha"),
        rate_per_acre=doc.get("rate_per_acre"),
        availability=doc.get("availability", MachineryAvailability.available),
        description=doc.get("description"),
        photo_urls=doc.get("photo_urls", []),
        posted_by=doc["posted_by"],
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at"),
        distance_km=dist,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Public read endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("", response_model=MachineryPage, summary="যন্ত্রপাতি তালিকা")
def list_machinery(
    machinery_type:  MachineryType | None         = Query(None, description="যন্ত্রের ধরন"),
    district:        str | None                   = Query(None, description="জেলা"),
    upazila:         str | None                   = Query(None),
    availability:    MachineryAvailability | None = Query(None),
    lat:             float | None                 = Query(None, ge=-90,  le=90,  description="আপনার অবস্থানের latitude"),
    lon:             float | None                 = Query(None, ge=-180, le=180, description="আপনার অবস্থানের longitude"),
    limit:           int                          = Query(20,   ge=1,   le=100),
    offset:          int                          = Query(0,    ge=0),
    store: DocStore = Depends(get_store),
):
    """List machinery available for hire. No auth required."""
    items = store.query("machinery", order_by="created_at", descending=True)

    if machinery_type:
        items = [i for i in items if i.get("machinery_type") == machinery_type]
    if district:
        dk = norm(district)
        items = [i for i in items if norm(i.get("district", "")) == dk]
    if upazila:
        uk = norm(upazila)
        items = [i for i in items if norm(i.get("upazila", "")) == uk]
    if availability:
        items = [i for i in items if i.get("availability") == availability]

    # Sort by distance if coordinates provided
    if lat and lon:
        def _dist(item: dict) -> float:
            if item.get("latitude") and item.get("longitude"):
                return haversine_km(lat, lon, item["latitude"], item["longitude"])
            return 9999.0
        items.sort(key=_dist)

    total = len(items)
    page  = items[offset : offset + limit]
    return MachineryPage(
        total=total, limit=limit, offset=offset,
        items=[_out(i, lat, lon) for i in page],
    )


@router.get("/{machinery_id}", response_model=MachineryOut, summary="যন্ত্রপাতির বিবরণ")
def get_machinery(
    machinery_id: str,
    lat: float | None = Query(None, ge=-90,  le=90),
    lon: float | None = Query(None, ge=-180, le=180),
    store: DocStore = Depends(get_store),
):
    doc = store.get("machinery", machinery_id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Machinery entry not found")
    return _out(doc, lat, lon)


# ─────────────────────────────────────────────────────────────────────────────
# Auth-required write endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("", response_model=MachineryOut, status_code=status.HTTP_201_CREATED,
             summary="যন্ত্রপাতি যোগ করুন")
def add_machinery(
    body: MachineryCreate,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """Add a machinery-for-hire entry. Any authenticated user can list their machine."""
    created_at = now()
    data = body.model_dump()
    data["phone"]        = normalize_bd_phone(data["phone"]) or data["phone"]
    data["district_key"] = norm(data["district"])
    data["upazila_key"]  = norm(data.get("upazila", ""))
    data["posted_by"]    = user.uid
    data["created_at"]   = created_at.isoformat()
    doc_id = store.add("machinery", data)
    doc = store.get("machinery", doc_id)
    return _out(doc)


@router.put("/{machinery_id}", response_model=MachineryOut, summary="যন্ত্রপাতি আপডেট করুন")
def update_machinery(
    machinery_id: str,
    body: MachineryUpdate,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = store.get("machinery", machinery_id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Machinery entry not found")
    if doc["posted_by"] != user.uid:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can edit this entry")

    patch = body.model_dump(exclude_none=True)
    if "phone" in patch:
        patch["phone"] = normalize_bd_phone(patch["phone"]) or patch["phone"]
    if "district" in patch:
        patch["district_key"] = norm(patch["district"])
    if "upazila" in patch:
        patch["upazila_key"] = norm(patch["upazila"])
    patch["updated_at"] = now().isoformat()

    store.set("machinery", machinery_id, patch, merge=True)
    return _out(store.get("machinery", machinery_id))


@router.delete("/{machinery_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="যন্ত্রপাতি মুছুন")
def delete_machinery(
    machinery_id: str,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = store.get("machinery", machinery_id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Machinery entry not found")
    if doc["posted_by"] != user.uid:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can delete this entry")
    store.delete("machinery", machinery_id)

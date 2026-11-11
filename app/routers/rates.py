from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query

from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_store, require_buyer
from ..geo import distance_between
from ..matching import crop_matches, location_matches
from ..schemas import (
    UNIT_TO_KG, Category, ListingOut, ListingStatus, RateCreate, RateOut, RatePage,
    RateSort, RateUpdate, Unit,
)
from ..utils import norm, now

router = APIRouter(prefix="/rates", tags=["Buyer Rate Board"])
COL = "rates"
FETCH_CAP = 1000


def _derive(doc: dict) -> None:
    doc["rate_per_kg"] = round(doc["rate_per_unit"] / UNIT_TO_KG[Unit(doc["unit"])], 4)
    doc["crop_key"] = norm(doc["crop_name"])
    doc["district_key"] = norm(doc.get("district"))
    doc["upazila_key"] = norm(doc.get("upazila"))


def _get_or_404(store: DocStore, rate_id: str) -> dict:
    doc = store.get(COL, rate_id)
    if not doc:
        raise HTTPException(404, "Rate not found")
    return doc


@router.post("", response_model=RateOut, status_code=201)
def publish_rate(
    body: RateCreate,
    user: CurrentUser = Depends(require_buyer),
    store: DocStore = Depends(get_store),
):
    doc = body.model_dump(mode="json")
    created = now()
    doc.update(
        active=True,
        buyer_id=user.uid,
        buyer_name=user.display_name,
        buyer_phone=user.phone,
        created_at=created,
        expires_at=created + timedelta(days=body.valid_days),
    )
    doc["latitude"] = doc["latitude"] if doc["latitude"] is not None else user.latitude
    doc["longitude"] = doc["longitude"] if doc["longitude"] is not None else user.longitude
    _derive(doc)
    return RateOut(**doc, id=store.add(COL, doc))


@router.get("", response_model=RatePage)
def rate_board(
    q: str | None = None,
    category: Category | None = None,
    district: str | None = None,
    upazila: str | None = None,
    min_rate: float | None = Query(None, ge=0, description="BDT per kg"),
    max_rate: float | None = Query(None, ge=0, description="BDT per kg"),
    lat: float | None = Query(None, ge=-90, le=90),
    lng: float | None = Query(None, ge=-180, le=180),
    radius_km: float | None = Query(None, gt=0),
    sort: RateSort = RateSort.newest,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """Farmer view of the rate board. With lat/lng + sort=nearest this also powers 'nearby buyers'."""
    if (sort == RateSort.nearest or radius_km) and (lat is None or lng is None):
        raise HTTPException(400, "lat and lng are required for nearest sort / radius filter")

    where = [("active", "==", True)]
    if category:
        where.append(("category", "==", category.value))
    if district:
        where.append(("district_key", "==", norm(district)))
    if upazila:
        where.append(("upazila_key", "==", norm(upazila)))
    rows = store.query(COL, where=where, limit=FETCH_CAP)

    t, qk, out = now(), norm(q), []
    for r in rows:
        if r["expires_at"] <= t:
            continue
        if qk and qk not in r["crop_key"]:
            continue
        if min_rate is not None and r["rate_per_kg"] < min_rate:
            continue
        if max_rate is not None and r["rate_per_kg"] > max_rate:
            continue
        r["distance_km"] = distance_between(r, lat, lng)
        if radius_km and (r["distance_km"] is None or r["distance_km"] > radius_km):
            continue
        out.append(r)

    far = float("inf")
    if sort == RateSort.rate_desc:
        out.sort(key=lambda r: -r["rate_per_kg"])
    elif sort == RateSort.nearest:
        out.sort(key=lambda r: r["distance_km"] if r["distance_km"] is not None else far)
    else:
        out.sort(key=lambda r: r["created_at"], reverse=True)

    return RatePage(total=len(out), limit=limit, offset=offset, items=[RateOut(**r) for r in out[offset: offset + limit]])


@router.get("/mine", response_model=list[RateOut])
def my_rates(user: CurrentUser = Depends(require_buyer), store: DocStore = Depends(get_store)):
    rows = store.query(COL, where=[("buyer_id", "==", user.uid)], limit=FETCH_CAP)
    rows.sort(key=lambda r: r["created_at"], reverse=True)
    return [RateOut(**r) for r in rows]


@router.get("/{rate_id}", response_model=RateOut)
def get_rate(rate_id: str, _: CurrentUser = Depends(get_current_user), store: DocStore = Depends(get_store)):
    return RateOut(**_get_or_404(store, rate_id))


@router.patch("/{rate_id}", response_model=RateOut)
def update_rate(
    rate_id: str,
    body: RateUpdate,
    user: CurrentUser = Depends(require_buyer),
    store: DocStore = Depends(get_store),
):
    doc = _get_or_404(store, rate_id)
    if doc["buyer_id"] != user.uid:
        raise HTTPException(403, "Not your rate")
    changes = body.model_dump(mode="json", exclude_none=True)
    doc.update(changes)
    if "valid_days" in changes:
        doc["expires_at"] = now() + timedelta(days=changes["valid_days"])
    _derive(doc)
    doc.pop("id")
    store.set(COL, rate_id, doc)
    return RateOut(**doc, id=rate_id)


@router.delete("/{rate_id}", status_code=204)
def delete_rate(rate_id: str, user: CurrentUser = Depends(require_buyer), store: DocStore = Depends(get_store)):
    doc = _get_or_404(store, rate_id)
    if doc["buyer_id"] != user.uid:
        raise HTTPException(403, "Not your rate")
    store.delete(COL, rate_id)


@router.get("/{rate_id}/matching-listings", response_model=list[ListingOut], tags=["Matching"])
def matching_listings(
    rate_id: str,
    radius_km: float = Query(50, gt=0),
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """Buyer view: farmers' listings that match this rate's crop and are in the same district / within radius."""
    rate = _get_or_404(store, rate_id)
    rows = store.query("listings", where=[("status", "==", ListingStatus.active.value)], limit=FETCH_CAP)
    result = []
    for r in rows:
        if not crop_matches(rate, r):
            continue
        ok, dist = location_matches(rate, r, radius_km)
        if ok:
            r["distance_km"] = dist
            result.append(r)
    result.sort(key=lambda r: (r["distance_km"] is None, r["distance_km"] or 0, r["price_per_kg"]))
    return [ListingOut(**r) for r in result]

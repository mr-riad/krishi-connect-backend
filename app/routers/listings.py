import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from ..config import get_settings
from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_storage, get_store, require_farmer
from ..geo import distance_between
from ..schemas import (
    UNIT_TO_KG, Category, ListingCreate, ListingOut, ListingPage, ListingSort,
    ListingStatus, ListingUpdate, RateOut, Unit,
)
from ..storage import FileStorage
from ..utils import norm, now

router = APIRouter(prefix="/listings", tags=["Farmer Listings"])
COL = "listings"
FETCH_CAP = 1000
ALLOWED_IMAGES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


def _derive(doc: dict) -> None:
    unit = Unit(doc["unit"])
    doc["quantity_kg"] = round(doc["quantity"] * UNIT_TO_KG[unit], 3)
    doc["price_per_kg"] = round(doc["price_per_unit"] / UNIT_TO_KG[unit], 4)
    doc["crop_key"] = norm(doc["crop_name"])
    doc["district_key"] = norm(doc.get("district"))
    doc["upazila_key"] = norm(doc.get("upazila"))


def _get_or_404(store: DocStore, listing_id: str) -> dict:
    doc = store.get(COL, listing_id)
    if not doc:
        raise HTTPException(404, "Listing not found")
    return doc


@router.post("", response_model=ListingOut, status_code=201)
def create_listing(
    body: ListingCreate,
    user: CurrentUser = Depends(require_farmer),
    store: DocStore = Depends(get_store),
):
    try:
        doc = body.model_dump(mode="json")
        doc.update(
            status=ListingStatus.active.value,
            farmer_id=user.uid,
            farmer_name=user.display_name,
            farmer_phone=user.phone,
            created_at=now(),
        )
        # fall back to the farmer's saved profile location
        doc["latitude"] = doc["latitude"] if doc["latitude"] is not None else user.latitude
        doc["longitude"] = doc["longitude"] if doc["longitude"] is not None else user.longitude
        _derive(doc)
        doc_id = store.add(COL, doc)
        return ListingOut(**doc, id=doc_id)
    except Exception as e:
        import logging
        logging.getLogger("krishi.listings").exception("create_listing error: %s", e)
        raise HTTPException(500, detail=f"পোস্ট প্রকাশে ত্রুটি: {str(e)}")


@router.get("", response_model=ListingPage)
def search_listings(
    q: str | None = Query(None, description="Crop name (partial match)"),
    category: Category | None = None,
    district: str | None = None,
    upazila: str | None = None,
    min_price: float | None = Query(None, ge=0, description="BDT per kg"),
    max_price: float | None = Query(None, ge=0, description="BDT per kg"),
    min_quantity: float | None = Query(None, ge=0, description="in kg"),
    max_quantity: float | None = Query(None, ge=0, description="in kg"),
    harvest_from: str | None = Query(None, description="YYYY-MM-DD"),
    harvest_to: str | None = Query(None, description="YYYY-MM-DD"),
    lat: float | None = Query(None, ge=-90, le=90),
    lng: float | None = Query(None, ge=-180, le=180),
    radius_km: float | None = Query(None, gt=0, description="Needs lat & lng"),
    sort: ListingSort = ListingSort.newest,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    if (sort == ListingSort.nearest or radius_km) and (lat is None or lng is None):
        raise HTTPException(400, "lat and lng are required for nearest sort / radius filter")

    where = [("status", "==", ListingStatus.active.value)]
    if category:
        where.append(("category", "==", category.value))
    if district:
        where.append(("district_key", "==", norm(district)))
    if upazila:
        where.append(("upazila_key", "==", norm(upazila)))
    rows = store.query(COL, where=where, limit=FETCH_CAP)

    qk = norm(q)
    out = []
    for r in rows:
        if qk and qk not in r.get("crop_key", ""):
            continue
        if min_price is not None and r["price_per_kg"] < min_price:
            continue
        if max_price is not None and r["price_per_kg"] > max_price:
            continue
        if min_quantity is not None and r["quantity_kg"] < min_quantity:
            continue
        if max_quantity is not None and r["quantity_kg"] > max_quantity:
            continue
        hd = r.get("harvest_date")
        if harvest_from and (not hd or hd < harvest_from):
            continue
        if harvest_to and (not hd or hd > harvest_to):
            continue
        r["distance_km"] = distance_between(r, lat, lng)
        if radius_km and (r["distance_km"] is None or r["distance_km"] > radius_km):
            continue
        out.append(r)

    far = float("inf")
    if sort == ListingSort.price_asc:
        out.sort(key=lambda r: r["price_per_kg"])
    elif sort == ListingSort.nearest:
        out.sort(key=lambda r: r["distance_km"] if r["distance_km"] is not None else far)
    else:
        out.sort(key=lambda r: r["created_at"], reverse=True)

    page = out[offset: offset + limit]
    return ListingPage(total=len(out), limit=limit, offset=offset, items=[ListingOut(**r) for r in page])


@router.get("/mine", response_model=list[ListingOut])
def my_listings(user: CurrentUser = Depends(require_farmer), store: DocStore = Depends(get_store)):
    rows = store.query(COL, where=[("farmer_id", "==", user.uid)], limit=FETCH_CAP)
    rows.sort(key=lambda r: r["created_at"], reverse=True)
    return [ListingOut(**r) for r in rows]


@router.get("/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: str, _: CurrentUser = Depends(get_current_user), store: DocStore = Depends(get_store)):
    return ListingOut(**_get_or_404(store, listing_id))


@router.patch("/{listing_id}", response_model=ListingOut)
def update_listing(
    listing_id: str,
    body: ListingUpdate,
    user: CurrentUser = Depends(require_farmer),
    store: DocStore = Depends(get_store),
):
    doc = _get_or_404(store, listing_id)
    if doc["farmer_id"] != user.uid:
        raise HTTPException(403, "Not your listing")
    changes = body.model_dump(mode="json", exclude_none=True)
    doc.update(changes)
    _derive(doc)
    doc.pop("id")
    store.set(COL, listing_id, doc)
    return ListingOut(**doc, id=listing_id)


@router.delete("/{listing_id}", status_code=204)
def delete_listing(listing_id: str, user: CurrentUser = Depends(require_farmer), store: DocStore = Depends(get_store)):
    doc = _get_or_404(store, listing_id)
    if doc["farmer_id"] != user.uid:
        raise HTTPException(403, "Not your listing")
    store.delete(COL, listing_id)


@router.post("/{listing_id}/photos", response_model=ListingOut)
def upload_photos(
    listing_id: str,
    files: list[UploadFile] = File(...),
    user: CurrentUser = Depends(require_farmer),
    store: DocStore = Depends(get_store),
    storage: FileStorage = Depends(get_storage),
):
    """Upload up to 5 photos (jpg/png/webp) to Firebase Storage and attach the URLs.
    (Alternative: upload from Flutter directly and send the URLs in `photo_urls`.)"""
    doc = _get_or_404(store, listing_id)
    if doc["farmer_id"] != user.uid:
        raise HTTPException(403, "Not your listing")
    if len(doc.get("photo_urls", [])) + len(files) > 5:
        raise HTTPException(400, "A listing can have at most 5 photos")

    limit_bytes = get_settings().max_upload_mb * 1024 * 1024
    urls = []
    for f in files:
        ext = ALLOWED_IMAGES.get(f.content_type or "")
        if not ext:
            raise HTTPException(415, "Only JPEG, PNG or WEBP images are allowed")
        data = f.file.read(limit_bytes + 1)
        if len(data) > limit_bytes:
            raise HTTPException(413, f"Each image must be under {get_settings().max_upload_mb} MB")
        urls.append(storage.upload(f"listings/{listing_id}/{uuid.uuid4().hex}.{ext}", data, f.content_type))

    doc["photo_urls"] = doc.get("photo_urls", []) + urls
    store.update(COL, listing_id, {"photo_urls": doc["photo_urls"]})
    return ListingOut(**doc)


@router.get("/{listing_id}/matching-rates", response_model=list[RateOut], tags=["Matching"])
def matching_rates(
    listing_id: str,
    radius_km: float = Query(50, gt=0),
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """Farmer view: which buyers are buying this crop near me, best rate first."""
    from ..matching import crop_matches, location_matches

    listing = _get_or_404(store, listing_id)
    rates = store.query("rates", where=[("active", "==", True)], limit=FETCH_CAP)
    result = []
    for r in rates:
        if r["expires_at"] <= now() or not crop_matches(listing, r):
            continue
        ok, dist = location_matches(listing, r, radius_km)
        if ok:
            r["distance_km"] = dist
            result.append(r)
    result.sort(key=lambda r: -r["rate_per_kg"])
    return [RateOut(**r) for r in result]

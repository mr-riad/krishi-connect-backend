"""
Admin dashboard router
Endpoints:
  GET  /admin/stats                 → platform analytics summary
  GET  /admin/users                 → list all users (paginated)
  GET  /admin/users/{uid}           → get user detail
  PATCH /admin/users/{uid}          → update/ban/verify user
  DELETE /admin/users/{uid}         → delete user

  GET  /admin/listings              → list all listings (any status)
  PATCH /admin/listings/{id}        → moderate listing (approve/suspend/delete)
  DELETE /admin/listings/{id}       → hard-delete listing

  GET  /admin/reports               → list moderation reports
  PATCH /admin/reports/{id}         → resolve/dismiss report

  GET  /admin/forum/posts           → list all forum posts including deleted
  DELETE /admin/forum/posts/{id}    → hard-delete forum post
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_store
from ..schemas_admin import (
    AdminUserUpdate, AdminUserOut,
    AdminListingModerate,
    AdminReportResolve, AdminReportOut,
    AdminStatsOut,
)
from ..schemas import ListingOut, ListingStatus
from ..utils import now, norm

router = APIRouter(prefix="/admin", tags=["Admin"])
FETCH_CAP = 2000


def _require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return user


# ─── Stats ───────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=AdminStatsOut)
def get_stats(
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    users = store.query("users", limit=FETCH_CAP)
    listings = store.query("listings", limit=FETCH_CAP)
    rates = store.query("rates", limit=FETCH_CAP)
    posts = store.query("forum_posts", limit=FETCH_CAP)
    reports = store.query("forum_reports", where=[("status", "==", "pending")], limit=FETCH_CAP)
    alerts = store.query("weather_alerts", where=[("active", "==", True)], limit=100)
    calls = store.query("call_logs", limit=FETCH_CAP)

    farmers = sum(1 for u in users if u.get("role") == "farmer")
    buyers = sum(1 for u in users if u.get("role") == "buyer")
    active_listings = sum(1 for l in listings if l.get("status") == "active")

    # District breakdown
    district_counts: dict[str, int] = {}
    for u in users:
        d = u.get("district", "Unknown") or "Unknown"
        district_counts[d] = district_counts.get(d, 0) + 1

    return AdminStatsOut(
        total_users=len(users),
        total_farmers=farmers,
        total_buyers=buyers,
        total_listings=len(listings),
        active_listings=active_listings,
        total_rates=len(rates),
        total_forum_posts=len(posts),
        pending_reports=len(reports),
        active_weather_alerts=len(alerts),
        total_calls=len(calls),
        users_by_district=district_counts,
    )


# ─── Users ───────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    role: str | None = Query(None, description="farmer | buyer | admin"),
    district: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    where = []
    if role:
        where.append(("role", "==", role))
    if district:
        where.append(("district_key", "==", norm(district)))
    rows = store.query("users", where=where, limit=FETCH_CAP)
    rows.sort(key=lambda r: r.get("created_at", r.get("updated_at", "")), reverse=True)
    return [AdminUserOut(**r) for r in rows[offset: offset + limit]]


@router.get("/users/{uid}", response_model=AdminUserOut)
def get_user(
    uid: str,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = store.get("users", uid)
    if not doc:
        raise HTTPException(404, "User not found")
    return AdminUserOut(**doc)


@router.patch("/users/{uid}", response_model=AdminUserOut)
def update_user(
    uid: str,
    body: AdminUserUpdate,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = store.get("users", uid)
    if not doc:
        raise HTTPException(404, "User not found")
    changes = body.model_dump(mode="json", exclude_none=True)
    changes["updated_at"] = now()
    store.set("users", uid, {**doc, **changes})
    return AdminUserOut(**{**doc, **changes})


@router.delete("/users/{uid}", status_code=204)
def delete_user(
    uid: str,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    if not store.get("users", uid):
        raise HTTPException(404, "User not found")
    store.delete("users", uid)


# ─── Listings Moderation ──────────────────────────────────────────────────────

@router.get("/listings", response_model=list[ListingOut])
def admin_list_listings(
    status: str | None = Query(None, description="active | sold | closed | suspended"),
    district: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    where = []
    if status:
        where.append(("status", "==", status))
    if district:
        where.append(("district_key", "==", norm(district)))
    rows = store.query("listings", where=where, limit=FETCH_CAP)
    rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return [ListingOut(**r) for r in rows[offset: offset + limit]]


@router.patch("/listings/{listing_id}")
def moderate_listing(
    listing_id: str,
    body: AdminListingModerate,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = store.get("listings", listing_id)
    if not doc:
        raise HTTPException(404, "Listing not found")
    changes = {"status": body.status, "admin_note": body.note, "moderated_at": now()}
    store.update("listings", listing_id, changes)
    return {"listing_id": listing_id, "status": body.status}


@router.delete("/listings/{listing_id}", status_code=204)
def admin_delete_listing(
    listing_id: str,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    if not store.get("listings", listing_id):
        raise HTTPException(404, "Listing not found")
    store.delete("listings", listing_id)


# ─── Reports ─────────────────────────────────────────────────────────────────

@router.get("/reports", response_model=list[AdminReportOut])
def list_reports(
    status: str | None = Query(None, description="pending | resolved | dismissed"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    where = []
    if status:
        where.append(("status", "==", status))
    else:
        where.append(("status", "==", "pending"))
    rows = store.query("forum_reports", where=where, limit=FETCH_CAP)
    rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return [AdminReportOut(**r) for r in rows[offset: offset + limit]]


@router.patch("/reports/{report_id}", response_model=AdminReportOut)
def resolve_report(
    report_id: str,
    body: AdminReportResolve,
    admin: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = store.get("forum_reports", report_id)
    if not doc:
        raise HTTPException(404, "Report not found")
    changes = {
        "status": body.action,  # "resolved" | "dismissed"
        "admin_note": body.note,
        "resolved_by": admin.uid,
        "resolved_at": now(),
    }
    doc.update(changes)
    store.set("forum_reports", report_id, doc)

    # If resolved → soft-delete the offending post
    if body.action == "resolved" and doc.get("post_id"):
        post = store.get("forum_posts", doc["post_id"])
        if post:
            store.update("forum_posts", doc["post_id"], {"is_deleted": True, "deleted_at": now()})

    return AdminReportOut(**doc)


# ─── Forum Moderation ─────────────────────────────────────────────────────────

@router.get("/forum/posts", response_model=list[dict])
def admin_list_forum_posts(
    include_deleted: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    rows = store.query("forum_posts", limit=FETCH_CAP)
    if not include_deleted:
        rows = [r for r in rows if not r.get("is_deleted")]
    rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return rows[offset: offset + limit]


@router.delete("/forum/posts/{post_id}", status_code=204)
def admin_delete_forum_post(
    post_id: str,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    if not store.get("forum_posts", post_id):
        raise HTTPException(404, "Post not found")
    store.delete("forum_posts", post_id)

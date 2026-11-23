"""
Feature 3 — Weather Alerts Router
==================================
Endpoints:
  POST /weather/fcm-token          Register / update user's FCM device token
  DELETE /weather/fcm-token        Unregister (logout / permission revoked)
  GET  /weather/alerts             List recent active weather alerts (public)
  GET  /weather/alerts/{id}        Single alert detail (public)
  POST /weather/alerts             Create & broadcast alert (admin only)
  GET  /weather/alerts/my          Alerts targeted to current user's district
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_store
from ..fcm import send_fcm_to_tokens
from ..schemas_weather import (
    AlertSeverity,
    FCMTokenOut,
    FCMTokenRegister,
    WeatherAlertCreate,
    WeatherAlertOut,
    WeatherAlertPage,
)
from ..utils import norm, now

router = APIRouter(prefix="/weather", tags=["Weather Alerts"])


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

def _alert_out(doc: dict) -> WeatherAlertOut:
    return WeatherAlertOut(
        id=doc["id"],
        alert_type=doc["alert_type"],
        severity=doc.get("severity", AlertSeverity.warning),
        title_bn=doc["title_bn"],
        title_en=doc.get("title_en"),
        body_bn=doc["body_bn"],
        body_en=doc.get("body_en"),
        target_districts=doc.get("target_districts", []),
        source=doc.get("source"),
        valid_until=doc.get("valid_until"),
        extra_data=doc.get("extra_data", {}),
        sent_count=doc.get("sent_count", 0),
        created_at=doc["created_at"],
        created_by=doc["created_by"],
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# FCM Device Token Registration
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/fcm-token", response_model=FCMTokenOut, summary="FCM টোকেন রেজিস্টার করুন")
def register_fcm_token(
    body: FCMTokenRegister,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """
    Register or update the current user's FCM device token.
    Call this after login and whenever the FCM token refreshes.
    - Saves the token in collection `fcm_tokens` keyed by uid.
    - Also persists district/location for geo-targeted alerts.
    """
    registered_at = now()
    data = {
        "uid":           user.uid,
        "fcm_token":     body.fcm_token,
        "district":      body.district,
        "district_key":  norm(body.district) if body.district else None,
        "upazila":       body.upazila,
        "latitude":      body.latitude,
        "longitude":     body.longitude,
        "registered_at": registered_at.isoformat(),
    }
    store.set("fcm_tokens", user.uid, data, merge=False)

    # Also update user's location if provided
    if body.district or body.latitude:
        patch: dict = {}
        if body.district:
            patch["district"] = body.district
            patch["district_key"] = norm(body.district)
        if body.upazila:
            patch["upazila"] = body.upazila
        if body.latitude is not None:
            patch["latitude"] = body.latitude
        if body.longitude is not None:
            patch["longitude"] = body.longitude
        if patch:
            store.set("users", user.uid, patch, merge=True)

    return FCMTokenOut(
        uid=user.uid,
        fcm_token=body.fcm_token,
        district=body.district,
        upazila=body.upazila,
        latitude=body.latitude,
        longitude=body.longitude,
        registered_at=registered_at,
    )


@router.delete("/fcm-token", status_code=status.HTTP_204_NO_CONTENT, summary="FCM টোকেন মুছুন")
def unregister_fcm_token(
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """Remove the user's FCM token (called on logout or permission denial)."""
    store.delete("fcm_tokens", user.uid)


# ─────────────────────────────────────────────────────────────────────────────
# Alert CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/alerts", response_model=WeatherAlertPage, summary="আবহাওয়া সতর্কতা তালিকা")
def list_alerts(
    district: str | None = Query(None, description="Filter by district (Bangla or English)"),
    severity: AlertSeverity | None = Query(None),
    limit:  int = Query(20, ge=1, le=100),
    offset: int = Query(0,  ge=0),
    store: DocStore = Depends(get_store),
):
    """
    List active weather alerts.
    - Public endpoint — no auth required.
    - Pass `district` to get alerts for a specific area (includes national alerts too).
    """
    all_alerts = store.query("weather_alerts", order_by="created_at", descending=True)
    now_dt = datetime.now(timezone.utc)

    # Filter expired
    active = []
    for a in all_alerts:
        vu = a.get("valid_until")
        if vu:
            try:
                vu_dt = datetime.fromisoformat(str(vu).replace("Z", "+00:00"))
                if vu_dt.tzinfo is None:
                    vu_dt = vu_dt.replace(tzinfo=timezone.utc)
                if vu_dt < now_dt:
                    continue
            except Exception:
                pass
        active.append(a)

    # Filter by district
    if district:
        dk = norm(district)
        filtered = []
        for a in active:
            td = a.get("target_districts", [])
            if not td:  # broadcast to all
                filtered.append(a)
            elif dk in [norm(d) for d in td]:
                filtered.append(a)
        active = filtered

    # Filter by severity
    if severity:
        active = [a for a in active if a.get("severity") == severity]

    total = len(active)
    page  = active[offset : offset + limit]
    return WeatherAlertPage(total=total, limit=limit, offset=offset,
                            items=[_alert_out(a) for a in page])


@router.get("/alerts/my", response_model=WeatherAlertPage, summary="আমার এলাকার সতর্কতা")
def my_alerts(
    limit:  int = Query(20, ge=1, le=100),
    offset: int = Query(0,  ge=0),
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """
    Return alerts targeted to the authenticated user's district.
    Includes national (broadcast) alerts as well.
    """
    district = user.district
    all_alerts = store.query("weather_alerts", order_by="created_at", descending=True)
    now_dt = datetime.now(timezone.utc)
    result = []
    dk = norm(district) if district else None

    for a in all_alerts:
        # Expiry check
        vu = a.get("valid_until")
        if vu:
            try:
                vu_dt = datetime.fromisoformat(str(vu).replace("Z", "+00:00"))
                if vu_dt.tzinfo is None:
                    vu_dt = vu_dt.replace(tzinfo=timezone.utc)
                if vu_dt < now_dt:
                    continue
            except Exception:
                pass

        td = a.get("target_districts", [])
        if not td:
            result.append(a)
        elif dk and dk in [norm(d) for d in td]:
            result.append(a)

    total = len(result)
    page  = result[offset : offset + limit]
    return WeatherAlertPage(total=total, limit=limit, offset=offset,
                            items=[_alert_out(a) for a in page])


@router.get("/alerts/{alert_id}", response_model=WeatherAlertOut, summary="সতর্কতার বিবরণ")
def get_alert(
    alert_id: str,
    store: DocStore = Depends(get_store),
):
    doc = store.get("weather_alerts", alert_id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alert not found")
    return _alert_out(doc)


@router.post("/alerts", response_model=WeatherAlertOut, status_code=status.HTTP_201_CREATED,
             summary="আবহাওয়া সতর্কতা তৈরি ও পাঠান")
def create_and_broadcast_alert(
    body: WeatherAlertCreate,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """
    Create a weather alert AND push FCM notifications to targeted users.

    **Who can call this?**
    Currently any authenticated user (admin gate can be added via role check).
    In production, restrict to `role == "admin"` or a separate admin token.

    **FCM behaviour:**
    - If `target_districts` is empty → all registered devices receive a push.
    - Otherwise only devices whose registered district matches receive it.
    - Falls back to MOCK logging when Firebase is not configured.
    """
    created_at = now()

    # ── Persist alert ──
    alert_data = body.model_dump()
    alert_data["created_at"]  = created_at.isoformat()
    alert_data["created_by"]  = user.uid
    alert_data["sent_count"]  = 0
    if alert_data.get("valid_until") and hasattr(alert_data["valid_until"], "isoformat"):
        alert_data["valid_until"] = alert_data["valid_until"].isoformat()

    alert_id = store.add("weather_alerts", alert_data)

    # ── Collect FCM tokens ──
    all_tokens = store.query("fcm_tokens")
    target_districts_keys = [norm(d) for d in (body.target_districts or [])]

    if target_districts_keys:
        tokens = [
            t["fcm_token"]
            for t in all_tokens
            if t.get("fcm_token") and norm(t.get("district", "")) in target_districts_keys
        ]
    else:
        tokens = [t["fcm_token"] for t in all_tokens if t.get("fcm_token")]

    # ── Send FCM ──
    sent_count = 0
    if tokens:
        severity_emoji = {"info": "ℹ️", "warning": "⚠️", "danger": "🔴"}.get(body.severity, "⚠️")
        fcm_data = {
            "alert_id":   alert_id,
            "alert_type": body.alert_type,
            "severity":   body.severity,
        }
        result = send_fcm_to_tokens(
            tokens=tokens,
            title=f"{severity_emoji} {body.title_bn}",
            body=body.body_bn,
            data={k: str(v) for k, v in fcm_data.items()},
        )
        sent_count = result.success

    # Update sent_count in DB
    store.set("weather_alerts", alert_id, {"sent_count": sent_count}, merge=True)

    doc = store.get("weather_alerts", alert_id)
    return _alert_out(doc)

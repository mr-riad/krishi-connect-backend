"""
Push Notification / Weather Alert router
Endpoints:
  GET  /alerts/weather                   → list active weather alerts
  POST /alerts/weather                   → admin: create & broadcast alert
  DELETE /alerts/weather/{alert_id}      → admin: deactivate alert

  POST /notifications/fcm/register       → register / refresh device FCM token
  POST /notifications/fcm/send           → admin: manual push to topic/token
  POST /notifications/fcm/send-topic     → admin: send to a topic (district)
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_store
from ..schemas_advisory import (
    WeatherAlertCreate, WeatherAlertOut,
    FCMTokenRegister, FCMSendRequest,
)
from ..utils import now

router = APIRouter(tags=["Alerts & Notifications"])
COL_ALERTS = "weather_alerts"
COL_TOKENS = "fcm_tokens"
logger = logging.getLogger("krishi.notifications")


def _require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return user


def _send_fcm(title: str, body: str, data: dict[str, Any] | None = None,
              token: str | None = None, topic: str | None = None) -> dict:
    """Send FCM push notification via Firebase Admin SDK."""
    try:
        import firebase_admin
        from firebase_admin import messaging

        if not firebase_admin._apps:
            return {"status": "skipped", "reason": "Firebase not initialized"}

        notification = messaging.Notification(title=title, body=body)
        android = messaging.AndroidConfig(priority="high")
        apns = messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(sound="default", badge=1)
            )
        )

        if token:
            msg = messaging.Message(
                notification=notification,
                data=data or {},
                android=android,
                apns=apns,
                token=token,
            )
        elif topic:
            msg = messaging.Message(
                notification=notification,
                data=data or {},
                android=android,
                apns=apns,
                topic=topic,
            )
        else:
            return {"status": "error", "reason": "Either token or topic required"}

        resp = messaging.send(msg)
        return {"status": "sent", "message_id": resp}
    except Exception as exc:
        logger.warning("FCM send failed: %s", exc)
        return {"status": "error", "reason": str(exc)}


# ─── Weather Alerts ──────────────────────────────────────────────────────────

@router.get("/alerts/weather", response_model=list[WeatherAlertOut])
def list_weather_alerts(
    district: str | None = None,
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    where = [("active", "==", True)]
    if district:
        where.append(("district", "==", district))
    rows = store.query(COL_ALERTS, where=where, limit=100)
    rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return [WeatherAlertOut(**r) for r in rows]


@router.post("/alerts/weather", response_model=WeatherAlertOut, status_code=201)
def create_weather_alert(
    body: WeatherAlertCreate,
    user: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    doc = body.model_dump(mode="json")
    doc.update(active=True, created_at=now(), created_by=user.uid)
    alert_id = store.add(COL_ALERTS, doc)

    # Broadcast to district topic (or "all_farmers")
    topic = f"district_{doc.get('district', 'all').replace(' ', '_').lower()}" if doc.get("district") else "all_farmers"
    fcm_result = _send_fcm(
        title=f"⚠️ আবহাওয়া সতর্কতা – {doc.get('district', 'সকল এলাকা')}",
        body=doc.get("message_bn", "আবহাওয়া সংক্রান্ত জরুরি বার্তা।"),
        data={"type": "weather_alert", "alert_id": alert_id},
        topic=topic,
    )
    logger.info("Weather alert %s sent via FCM: %s", alert_id, fcm_result)

    return WeatherAlertOut(**doc, id=alert_id)


@router.delete("/alerts/weather/{alert_id}", status_code=204)
def deactivate_alert(
    alert_id: str,
    _: CurrentUser = Depends(_require_admin),
    store: DocStore = Depends(get_store),
):
    if not store.get(COL_ALERTS, alert_id):
        raise HTTPException(404, "Alert not found")
    store.update(COL_ALERTS, alert_id, {"active": False, "deactivated_at": now()})


# ─── FCM Token Registration ───────────────────────────────────────────────────

@router.post("/notifications/fcm/register", status_code=200)
def register_fcm_token(
    body: FCMTokenRegister,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """Flutter calls this after app launch to register/update the device FCM token.
    Also subscribes the device to the user's district topic."""
    doc = {
        "uid": user.uid,
        "token": body.token,
        "district": body.district or user.district,
        "platform": body.platform,
        "updated_at": now(),
    }
    store.set(COL_TOKENS, f"{user.uid}_{body.token[:20]}", doc, merge=True)

    # Subscribe to district topic
    if body.district or user.district:
        district = (body.district or user.district or "").replace(" ", "_").lower()
        try:
            import firebase_admin
            from firebase_admin import messaging
            if firebase_admin._apps:
                messaging.subscribe_to_topic([body.token], f"district_{district}")
        except Exception as exc:
            logger.debug("FCM subscribe error: %s", exc)

    # Also subscribe to all_farmers topic
    try:
        import firebase_admin
        from firebase_admin import messaging
        if firebase_admin._apps:
            messaging.subscribe_to_topic([body.token], "all_farmers")
    except Exception as exc:
        logger.debug("FCM all_farmers subscribe error: %s", exc)

    return {"status": "registered", "uid": user.uid}


@router.post("/notifications/fcm/send")
def send_notification(
    body: FCMSendRequest,
    _: CurrentUser = Depends(_require_admin),
):
    """Admin: send a push notification to a specific device token."""
    result = _send_fcm(
        title=body.title,
        body=body.body,
        data=body.data,
        token=body.token,
    )
    return result


@router.post("/notifications/fcm/send-topic")
def send_notification_topic(
    body: FCMSendRequest,
    _: CurrentUser = Depends(_require_admin),
):
    """Admin: broadcast to a topic (e.g. district_rajshahi, all_farmers)."""
    result = _send_fcm(
        title=body.title,
        body=body.body,
        data=body.data,
        topic=body.topic or "all_farmers",
    )
    return result

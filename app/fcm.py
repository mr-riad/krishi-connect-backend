"""
FCM (Firebase Cloud Messaging) helper utilities for Krishi Connect.

Supports two push modes:
  1. REAL mode  — firebase-admin SDK sends actual FCM notifications
                  (requires FIREBASE_CREDENTIALS_* env var)
  2. MOCK mode  — logs the notification to console / structured logs
                  (used in development when Firebase is not configured)

The router calls send_fcm_notification() and never needs to know which
mode is active.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .config import get_settings

logger = logging.getLogger("krishi.fcm")


@dataclass
class FCMResult:
    success: int = 0
    failure: int = 0
    details: list[dict[str, Any]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.success + self.failure


def _is_firebase_ready() -> bool:
    """Check whether firebase-admin is initialised WITH valid credentials (not anonymous)."""
    try:
        import firebase_admin
        if not firebase_admin._apps:
            return False
        # Check the default app has real credentials (not anonymous / empty)
        app = firebase_admin.get_app()
        cred = app._credential
        # Anonymous / default credentials won't have a service_account_email
        sa_email = getattr(cred, "service_account_email", None)
        return bool(sa_email)
    except Exception:
        return False


def _init_firebase_if_needed() -> None:
    """Lazy-initialise Firebase Admin SDK once."""
    import json
    try:
        import firebase_admin
        from firebase_admin import credentials

        if firebase_admin._apps:
            return

        s = get_settings()
        cred = None

        if s.firebase_credentials_json:
            cred_dict = json.loads(s.firebase_credentials_json)
            cred = credentials.Certificate(cred_dict)
        elif s.firebase_credentials_path:
            cred = credentials.Certificate(s.firebase_credentials_path)

        opts: dict = {}
        if s.firebase_storage_bucket:
            opts["storageBucket"] = s.firebase_storage_bucket

        firebase_admin.initialize_app(cred, opts)
        logger.info("Firebase Admin SDK initialised (FCM ready).")
    except Exception as exc:
        logger.warning("FCM: Firebase initialisation failed: %s", exc)


def send_fcm_to_tokens(
    tokens: list[str],
    title: str,
    body: str,
    data: dict[str, str] | None = None,
    image_url: str | None = None,
) -> FCMResult:
    """
    Send a push notification to a list of FCM device tokens.

    Args:
        tokens     — FCM registration tokens (max 500 per batch per FCM spec)
        title      — Notification title (should be in Bangla for KrishiConnect)
        body       — Notification body text
        data       — Optional key-value data payload (all values must be str)
        image_url  — Optional image URL shown in notification

    Returns:
        FCMResult with success/failure counts.
    """
    if not tokens:
        return FCMResult()

    _init_firebase_if_needed()

    if not _is_firebase_ready():
        # ── MOCK MODE ──────────────────────────────────────────────────────
        logger.info(
            "FCM MOCK: would send to %d token(s) | title=%r | body=%r | data=%s",
            len(tokens), title, body, data,
        )
        return FCMResult(success=len(tokens), failure=0)

    # ── REAL MODE (firebase-admin) ─────────────────────────────────────────
    try:
        from firebase_admin import messaging

        result = FCMResult()
        # FCM batch limit is 500 tokens per MulticastMessage
        BATCH = 500
        for i in range(0, len(tokens), BATCH):
            batch_tokens = tokens[i : i + BATCH]
            notification = messaging.Notification(title=title, body=body, image=image_url)
            android_config = messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    title=title,
                    body=body,
                    image=image_url,
                    sound="default",
                    channel_id="weather_alerts",
                ),
            )
            apns_config = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(sound="default", badge=1)
                )
            )
            message = messaging.MulticastMessage(
                tokens=batch_tokens,
                notification=notification,
                android=android_config,
                apns=apns_config,
                data=data or {},
            )
            batch_response = messaging.send_each_for_multicast(message)
            result.success += batch_response.success_count
            result.failure += batch_response.failure_count
            for idx, resp in enumerate(batch_response.responses):
                if not resp.success:
                    result.details.append({
                        "token": batch_tokens[idx][:20] + "...",
                        "error": str(resp.exception),
                    })

        logger.info(
            "FCM sent: %d success, %d failure (total tokens: %d)",
            result.success, result.failure, len(tokens),
        )
        return result

    except Exception as exc:
        logger.error("FCM send_each_for_multicast failed: %s", exc)
        return FCMResult(success=0, failure=len(tokens))


def send_fcm_to_topic(
    topic: str,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> FCMResult:
    """
    Send a push notification to an FCM topic (e.g. 'district_dhaka').
    Topics are cheaper than token-lists for broadcast scenarios.
    """
    _init_firebase_if_needed()

    if not _is_firebase_ready():
        logger.info("FCM MOCK topic=%r | title=%r | body=%r", topic, title, body)
        return FCMResult(success=1, failure=0)

    try:
        from firebase_admin import messaging

        message = messaging.Message(
            topic=topic,
            notification=messaging.Notification(title=title, body=body),
            android=messaging.AndroidConfig(priority="high"),
            data=data or {},
        )
        messaging.send(message)
        return FCMResult(success=1, failure=0)
    except Exception as exc:
        logger.error("FCM topic send failed: %s", exc)
        return FCMResult(success=0, failure=1)

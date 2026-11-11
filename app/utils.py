import re
from datetime import datetime, timezone

_BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def now() -> datetime:
    return datetime.now(timezone.utc)


def is_expired(expires_at) -> bool:
    """Safe expiry check that works with both datetime objects and ISO strings from SQLite."""
    if not expires_at:
        return False
    if isinstance(expires_at, str):
        try:
            exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        except Exception:
            return False
    elif isinstance(expires_at, datetime):
        exp = expires_at
    else:
        return False
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return exp <= datetime.now(timezone.utc)


def norm(text: str | None) -> str:
    """Case/space-insensitive key for district, upazila, crop name comparison."""
    return (text or "").strip().casefold()


def normalize_bd_phone(raw: str | None) -> str | None:
    """'০১৭১১-১২৩৪৫৬' / '01711 123456' / '+8801711123456' -> '+8801711123456'."""
    if not raw:
        return None
    s = raw.translate(_BN_DIGITS)
    s = re.sub(r"[^\d+]", "", s)
    if s.startswith("+880"):
        s = s[4:]
    elif s.startswith("880"):
        s = s[3:]
    s = s.lstrip("0")
    if len(s) == 10 and s.startswith("1"):
        return "+880" + s
    return raw.strip()  # unknown format (e.g. foreign number): return as given

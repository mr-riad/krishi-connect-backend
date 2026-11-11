from .geo import haversine_km
from .utils import norm


def crop_matches(a: dict, b: dict) -> bool:
    """Same category AND crop names overlap (e.g. 'বোরো ধান' ~ 'ধান', 'potato' ~ 'potato (diamond)')."""
    if a.get("category") != b.get("category"):
        return False
    na, nb = norm(a.get("crop_name")), norm(b.get("crop_name"))
    return bool(na and nb and (na in nb or nb in na))


def location_matches(a: dict, b: dict, radius_km: float) -> tuple[bool, float | None]:
    """Same district counts as a match; otherwise use GPS distance when both have it."""
    dist = None
    if None not in (a.get("latitude"), a.get("longitude"), b.get("latitude"), b.get("longitude")):
        dist = round(haversine_km(a["latitude"], a["longitude"], b["latitude"], b["longitude"]), 2)
    if dist is not None and dist <= radius_km:
        return True, dist
    if a.get("district_key") and a.get("district_key") == b.get("district_key"):
        return True, dist
    return False, dist

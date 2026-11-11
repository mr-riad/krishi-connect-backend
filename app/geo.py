import math


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def distance_between(doc: dict, lat: float | None, lng: float | None) -> float | None:
    if lat is None or lng is None:
        return None
    if doc.get("latitude") is None or doc.get("longitude") is None:
        return None
    return round(haversine_km(lat, lng, doc["latitude"], doc["longitude"]), 2)

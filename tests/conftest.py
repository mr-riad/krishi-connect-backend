import os

os.environ["USE_FIREBASE"] = "false"
os.environ["AUTH_DISABLED"] = "true"

import pytest
from fastapi.testclient import TestClient

from app.deps import get_storage, get_store
from app.main import app


@pytest.fixture()
def client():
    get_store.cache_clear()
    get_storage.cache_clear()
    return TestClient(app)


def h(uid: str) -> dict:
    return {"Authorization": f"Bearer {uid}"}


@pytest.fixture()
def users(client):
    def mk(uid, role, name, phone, district="Khulna", **extra):
        r = client.put("/users/me", headers=h(uid), json={"role": role, "name": name, "phone": phone, "district": district, **extra})
        assert r.status_code == 200, r.text

    mk("farmer1", "farmer", "Nurul", "01735-678901", "Khulna", upazila="Dumuria", latitude=22.80, longitude=89.42)
    mk("farmer2", "farmer", "Karim", "01711123456", "Rajshahi", latitude=24.37, longitude=88.60)
    mk("buyer1", "buyer", "Rahim Traders", "০১৮২২-৯৮৭৬৫৪", "Khulna", latitude=22.82, longitude=89.55)

"""
Tests for Feature 3 (Weather Alerts / FCM) and Feature 4 (Machinery + Ag-News).
Run with:  pytest tests/test_weather_machinery_news.py -v
"""

import os

# Must be set before importing app
os.environ.setdefault("USE_FIREBASE", "false")
os.environ.setdefault("AUTH_DISABLED", "true")

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer test_farmer_uid"}
AUTH2 = {"Authorization": "Bearer test_buyer_uid"}


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 3 — Weather Alerts & FCM
# ─────────────────────────────────────────────────────────────────────────────

class TestFCMToken:
    def test_register_token(self):
        r = client.post(
            "/weather/fcm-token",
            json={
                "fcm_token": "fake_device_token_abc123",
                "district": "Dhaka",
                "latitude": 23.8103,
                "longitude": 90.4125,
            },
            headers=AUTH,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["fcm_token"] == "fake_device_token_abc123"
        assert data["district"] == "Dhaka"
        assert data["uid"] == "test_farmer_uid"

    def test_unregister_token(self):
        # Register first
        client.post(
            "/weather/fcm-token",
            json={"fcm_token": "token_to_delete"},
            headers=AUTH,
        )
        r = client.delete("/weather/fcm-token", headers=AUTH)
        assert r.status_code == 204

    def test_token_requires_auth(self):
        r = client.post("/weather/fcm-token", json={"fcm_token": "x"})
        assert r.status_code == 401


class TestWeatherAlerts:
    def test_list_alerts_empty(self):
        r = client.get("/weather/alerts")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert isinstance(body["items"], list)

    def test_create_broadcast_alert(self):
        r = client.post(
            "/weather/alerts",
            json={
                "alert_type": "storm",
                "severity": "danger",
                "title_bn": "ঘূর্ণিঝড় সতর্কতা",
                "body_bn": "আগামী ২৪ ঘন্টায় ঘূর্ণিঝড়ের আশঙ্কা আছে। সতর্ক থাকুন।",
                "target_districts": [],
            },
            headers=AUTH,
        )
        assert r.status_code == 201
        data = r.json()
        assert data["alert_type"] == "storm"
        assert data["severity"] == "danger"
        assert "id" in data

    def test_create_targeted_alert(self):
        r = client.post(
            "/weather/alerts",
            json={
                "alert_type": "heavy_rain",
                "severity": "warning",
                "title_bn": "ভারী বৃষ্টির সতর্কতা",
                "body_bn": "ঢাকা ও ময়মনসিংহে ভারী বৃষ্টি হতে পারে।",
                "target_districts": ["Dhaka", "Mymensingh"],
                "source": "BMD",
            },
            headers=AUTH,
        )
        assert r.status_code == 201
        data = r.json()
        assert "Dhaka" in data["target_districts"]

    def test_get_alert_by_id(self):
        # Create alert first
        cr = client.post(
            "/weather/alerts",
            json={
                "alert_type": "flood",
                "severity": "danger",
                "title_bn": "বন্যা সতর্কতা",
                "body_bn": "নিচু এলাকায় বন্যার আশঙ্কা।",
            },
            headers=AUTH,
        )
        alert_id = cr.json()["id"]
        r = client.get(f"/weather/alerts/{alert_id}")
        assert r.status_code == 200
        assert r.json()["id"] == alert_id

    def test_get_nonexistent_alert(self):
        r = client.get("/weather/alerts/nonexistent_id_xyz")
        assert r.status_code == 404

    def test_list_alerts_filter_severity(self):
        client.post(
            "/weather/alerts",
            json={"alert_type": "general", "severity": "info",
                  "title_bn": "তথ্য", "body_bn": "আবহাওয়া স্বাভাবিক।"},
            headers=AUTH,
        )
        r = client.get("/weather/alerts?severity=info")
        assert r.status_code == 200
        for item in r.json()["items"]:
            assert item["severity"] == "info"

    def test_my_alerts_requires_auth(self):
        r = client.get("/weather/alerts/my")
        assert r.status_code == 401

    def test_my_alerts_authenticated(self):
        # Register token with district first
        client.post(
            "/weather/fcm-token",
            json={"fcm_token": "my_token", "district": "Dhaka"},
            headers=AUTH,
        )
        r = client.get("/weather/alerts/my", headers=AUTH)
        assert r.status_code == 200
        assert "items" in r.json()


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 4A — Machinery Directory
# ─────────────────────────────────────────────────────────────────────────────

MACHINERY_PAYLOAD = {
    "machinery_type": "tractor",
    "brand_model": "Kubota L4508",
    "owner_name": "রহিম উদ্দিন",
    "phone": "01711123456",
    "district": "Rajshahi",
    "upazila": "Godagari",
    "rate_per_bigha": 800.0,
    "rate_per_acre": 2000.0,
    "availability": "available",
    "description": "৫০ HP ট্র্যাক্টর, দিনে ৮ বিঘা চাষ করা সম্ভব।",
}


class TestMachineryDirectory:
    def test_list_machinery_public(self):
        r = client.get("/machinery")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert "total" in body

    def test_add_machinery(self):
        r = client.post("/machinery", json=MACHINERY_PAYLOAD, headers=AUTH)
        assert r.status_code == 201
        data = r.json()
        assert data["machinery_type"] == "tractor"
        assert data["owner_name"] == "রহিম উদ্দিন"
        assert data["posted_by"] == "test_farmer_uid"

    def test_get_machinery_by_id(self):
        cr = client.post("/machinery", json=MACHINERY_PAYLOAD, headers=AUTH)
        mid = cr.json()["id"]
        r = client.get(f"/machinery/{mid}")
        assert r.status_code == 200
        assert r.json()["id"] == mid

    def test_machinery_filter_by_type(self):
        r = client.get("/machinery?machinery_type=tractor")
        assert r.status_code == 200
        for item in r.json()["items"]:
            assert item["machinery_type"] == "tractor"

    def test_machinery_filter_by_district(self):
        r = client.get("/machinery?district=Rajshahi")
        assert r.status_code == 200
        for item in r.json()["items"]:
            assert item["district"].lower() == "rajshahi"

    def test_update_own_machinery(self):
        cr = client.post("/machinery", json=MACHINERY_PAYLOAD, headers=AUTH)
        mid = cr.json()["id"]
        r = client.put(
            f"/machinery/{mid}",
            json={"availability": "booked", "rate_per_bigha": 900.0},
            headers=AUTH,
        )
        assert r.status_code == 200
        assert r.json()["availability"] == "booked"
        assert r.json()["rate_per_bigha"] == 900.0

    def test_cannot_update_others_machinery(self):
        cr = client.post("/machinery", json=MACHINERY_PAYLOAD, headers=AUTH)
        mid = cr.json()["id"]
        r = client.put(
            f"/machinery/{mid}",
            json={"availability": "unavailable"},
            headers=AUTH2,
        )
        assert r.status_code == 403

    def test_delete_own_machinery(self):
        cr = client.post("/machinery", json=MACHINERY_PAYLOAD, headers=AUTH)
        mid = cr.json()["id"]
        r = client.delete(f"/machinery/{mid}", headers=AUTH)
        assert r.status_code == 204
        # Verify deleted
        r2 = client.get(f"/machinery/{mid}")
        assert r2.status_code == 404

    def test_cannot_delete_others_machinery(self):
        cr = client.post("/machinery", json=MACHINERY_PAYLOAD, headers=AUTH)
        mid = cr.json()["id"]
        r = client.delete(f"/machinery/{mid}", headers=AUTH2)
        assert r.status_code == 403

    def test_add_machinery_requires_auth(self):
        r = client.post("/machinery", json=MACHINERY_PAYLOAD)
        assert r.status_code == 401

    def test_machinery_distance_sort(self):
        # With location, should not error
        r = client.get("/machinery?lat=24.3745&lon=88.6042")
        assert r.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE 4B — Ag-News
# ─────────────────────────────────────────────────────────────────────────────

NEWS_PAYLOAD = {
    "category": "subsidy",
    "title_bn": "সার ক্রয়ে ৫০% ভর্তুকি ঘোষণা",
    "body_bn": "কৃষি মন্ত্রণালয় জানিয়েছে যে এই মৌসুমে সার ক্রয়ে ৫০% ভর্তুকি দেওয়া হবে। কৃষকরা নিকটস্থ বিএডিসি কেন্দ্র থেকে সার সংগ্রহ করতে পারবেন।",
    "source": "Ministry of Agriculture, Bangladesh",
    "tags": ["ভর্তুকি", "সার", "কৃষি"],
}


class TestAgNews:
    def test_list_news_public(self):
        r = client.get("/news")
        assert r.status_code == 200
        assert "items" in r.json()

    def test_list_categories(self):
        r = client.get("/news/categories")
        assert r.status_code == 200
        cats = r.json()
        assert len(cats) >= 7
        values = [c["value"] for c in cats]
        assert "subsidy" in values
        assert "policy" in values

    def test_create_news(self):
        r = client.post("/news", json=NEWS_PAYLOAD, headers=AUTH)
        assert r.status_code == 201
        data = r.json()
        assert data["category"] == "subsidy"
        assert "সার" in data["title_bn"]
        assert data["views"] == 0
        assert data["created_by"] == "test_farmer_uid"

    def test_get_news_by_id_increments_views(self):
        cr = client.post("/news", json=NEWS_PAYLOAD, headers=AUTH)
        nid = cr.json()["id"]
        r = client.get(f"/news/{nid}")
        assert r.status_code == 200
        assert r.json()["views"] >= 1

    def test_get_nonexistent_news(self):
        r = client.get("/news/does_not_exist_xyz")
        assert r.status_code == 404

    def test_filter_by_category(self):
        client.post("/news", json={**NEWS_PAYLOAD, "category": "policy",
                                   "title_bn": "নতুন কৃষি নীতি ২০২৬",
                                   "body_bn": "নতুন কৃষি নীতি ঘোষণা করা হয়েছে।"},
                    headers=AUTH)
        r = client.get("/news?category=policy")
        assert r.status_code == 200
        for item in r.json()["items"]:
            assert item["category"] == "policy"

    def test_search_news_by_title(self):
        r = client.get("/news?q=সার")
        assert r.status_code == 200
        # Should find the subsidy news created above

    def test_filter_by_district(self):
        client.post("/news",
                    json={**NEWS_PAYLOAD,
                          "title_bn": "সিলেটে বন্যা ক্ষতিপূরণ",
                          "body_bn": "সিলেট জেলার কৃষকদের ক্ষতিপূরণ দেওয়া হবে।",
                          "target_districts": ["Sylhet"]},
                    headers=AUTH)
        r = client.get("/news?district=Sylhet")
        assert r.status_code == 200
        # Should include national + Sylhet-targeted news

    def test_update_own_news(self):
        cr = client.post("/news", json=NEWS_PAYLOAD, headers=AUTH)
        nid = cr.json()["id"]
        r = client.put(
            f"/news/{nid}",
            json={"title_bn": "আপডেট: সার ক্রয়ে ৬০% ভর্তুকি"},
            headers=AUTH,
        )
        assert r.status_code == 200
        assert "৬০%" in r.json()["title_bn"]

    def test_cannot_update_others_news(self):
        cr = client.post("/news", json=NEWS_PAYLOAD, headers=AUTH)
        nid = cr.json()["id"]
        r = client.put(
            f"/news/{nid}",
            json={"title_bn": "হ্যাক করা শিরোনাম"},
            headers=AUTH2,
        )
        assert r.status_code == 403

    def test_delete_own_news(self):
        cr = client.post("/news", json=NEWS_PAYLOAD, headers=AUTH)
        nid = cr.json()["id"]
        r = client.delete(f"/news/{nid}", headers=AUTH)
        assert r.status_code == 204
        r2 = client.get(f"/news/{nid}")
        assert r2.status_code == 404

    def test_cannot_delete_others_news(self):
        cr = client.post("/news", json=NEWS_PAYLOAD, headers=AUTH)
        nid = cr.json()["id"]
        r = client.delete(f"/news/{nid}", headers=AUTH2)
        assert r.status_code == 403

    def test_create_news_requires_auth(self):
        r = client.post("/news", json=NEWS_PAYLOAD)
        assert r.status_code == 401

    def test_news_with_all_fields(self):
        r = client.post(
            "/news",
            json={
                "category": "training",
                "title_bn": "বিনামূল্যে কৃষি প্রশিক্ষণ",
                "title_en": "Free Agricultural Training",
                "body_bn": "কৃষি সম্প্রসারণ অধিদপ্তর বিনামূল্যে প্রশিক্ষণ দিচ্ছে।",
                "body_en": "Department of Agricultural Extension offers free training.",
                "source": "DAE Bangladesh",
                "source_url": "https://dae.gov.bd",
                "tags": ["প্রশিক্ষণ", "DAE"],
                "target_districts": ["Dhaka", "Chittagong"],
            },
            headers=AUTH,
        )
        assert r.status_code == 201
        data = r.json()
        assert data["category"] == "training"
        assert len(data["target_districts"]) == 2

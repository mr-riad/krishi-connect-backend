"""
Tests for Disease Diagnosis & Agricultural Tips endpoints.
Run: pytest tests/test_disease_api.py -v
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

# ─────────────────────────── Fixtures ───────────────────────────

FARMER_TOKEN = "test-farmer-uid-001"
AUTH_HEADER = {"Authorization": f"Bearer {FARMER_TOKEN}"}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ═══════════════════════════════════════════════════════════
#  DISEASE DATABASE TESTS
# ═══════════════════════════════════════════════════════════

class TestDiseaseList:
    def test_list_all_diseases(self, client):
        resp = client.get("/diseases", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        assert "items" in data
        assert len(data["items"]) > 0

    def test_filter_by_crop_paddy(self, client):
        resp = client.get("/diseases?crop=paddy", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 3  # We have 4 paddy diseases + general
        for item in data["items"]:
            assert item["crop"] in ("paddy", "general")

    def test_filter_by_category_fungal(self, client):
        resp = client.get("/diseases?category=fungal", headers=AUTH_HEADER)
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["category"] == "fungal"

    def test_filter_by_severity_high(self, client):
        resp = client.get("/diseases?severity=high", headers=AUTH_HEADER)
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["severity"] == "high"

    def test_filter_by_season_rabi(self, client):
        resp = client.get("/diseases?season=rabi", headers=AUTH_HEADER)
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert "rabi" in item["season"]

    def test_keyword_search_blast(self, client):
        resp = client.get("/diseases?q=blast", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        ids = [item["id"] for item in data["items"]]
        assert "paddy_blast" in ids

    def test_keyword_search_bangla(self, client):
        resp = client.get("/diseases?q=মরিচা", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_pagination(self, client):
        resp = client.get("/diseases?limit=3&offset=0", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 3
        assert data["limit"] == 3
        assert data["offset"] == 0

    def test_requires_auth(self, client):
        resp = client.get("/diseases")
        assert resp.status_code == 401


class TestDiseaseDetail:
    def test_get_paddy_blast(self, client):
        resp = client.get("/diseases/paddy_blast", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "paddy_blast"
        assert data["crop"] == "paddy"
        assert len(data["remedies_bn"]) > 0
        assert len(data["prevention_bn"]) > 0

    def test_get_nonexistent_disease(self, client):
        resp = client.get("/diseases/fake_disease_xyz", headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_all_diseases_have_required_fields(self, client):
        resp = client.get("/diseases?limit=100", headers=AUTH_HEADER)
        assert resp.status_code == 200
        required = ["id", "crop", "name", "name_bn", "category", "symptoms_bn", "remedies_bn", "prevention_bn", "severity"]
        for item in resp.json()["items"]:
            for field in required:
                assert field in item, f"Missing field '{field}' in disease {item.get('id')}"


class TestSupportedCrops:
    def test_list_crops(self, client):
        resp = client.get("/diseases/crops", headers=AUTH_HEADER)
        assert resp.status_code == 200
        crops = resp.json()
        assert isinstance(crops, list)
        assert "paddy" in crops
        assert "potato" in crops
        assert len(crops) >= 5


# ═══════════════════════════════════════════════════════════
#  DIAGNOSIS TESTS
# ═══════════════════════════════════════════════════════════

class TestDiagnosis:
    def test_diagnose_paddy_blast(self, client):
        resp = client.post(
            "/diseases/diagnose",
            json={
                "crop": "paddy",
                "symptoms": "পাতায় ডায়মন্ড আকারের বাদামি দাগ, কেন্দ্র ধূসর",
                "affected_part": "leaf",
                "season": "kharif",
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "matches" in data
        assert len(data["matches"]) > 0
        assert data["matches"][0]["disease_id"] == "paddy_blast"
        assert data["matches"][0]["match_score"] > 0.3
        assert len(data["matches"][0]["top_remedies"]) > 0

    def test_diagnose_potato_late_blight(self, client):
        resp = client.post(
            "/diseases/diagnose",
            json={
                "crop": "potato",
                "symptoms": "পাতায় পানিতে ভেজা বাদামি দাগ, পাতার নিচে সাদা ছাঁচ",
                "season": "rabi",
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["matches"]) > 0
        top_ids = [m["disease_id"] for m in data["matches"]]
        assert "potato_late_blight" in top_ids

    def test_diagnose_english_symptoms(self, client):
        resp = client.post(
            "/diseases/diagnose",
            json={
                "crop": "wheat",
                "symptoms": "orange rust pustules on leaves, yellow powder on stems",
                "season": "rabi",
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "matches" in data

    def test_diagnose_unknown_crop_returns_general_advice(self, client):
        resp = client.post(
            "/diseases/diagnose",
            json={
                "crop": "alien_plant",
                "symptoms": "পাতা হলুদ হয়ে যাচ্ছে",
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "general_advice_bn" in data

    def test_diagnose_requires_auth(self, client):
        resp = client.post(
            "/diseases/diagnose",
            json={"crop": "paddy", "symptoms": "some symptoms here"},
        )
        assert resp.status_code == 401

    def test_diagnose_validation_too_short(self, client):
        resp = client.post(
            "/diseases/diagnose",
            json={"crop": "paddy", "symptoms": "bad"},
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════
#  FARMING TIPS TESTS
# ═══════════════════════════════════════════════════════════

class TestFarmingTips:
    def test_list_all_tips(self, client):
        resp = client.get("/tips", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 5
        assert len(data["items"]) > 0

    def test_filter_tips_by_crop(self, client):
        resp = client.get("/tips?crop=paddy", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert "paddy" in item["crops"] or "all" in item["crops"]

    def test_filter_tips_by_category(self, client):
        resp = client.get("/tips?category=soil", headers=AUTH_HEADER)
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["category"] == "soil"

    def test_filter_tips_by_season(self, client):
        resp = client.get("/tips?season=kharif", headers=AUTH_HEADER)
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert "kharif" in item["season"]

    def test_tip_keyword_search(self, client):
        resp = client.get("/tips?q=সেচ", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_get_tip_by_id(self, client):
        resp = client.get("/tips/tip_soil_test", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "tip_soil_test"
        assert "title_bn" in data
        assert "body_bn" in data

    def test_get_tip_not_found(self, client):
        resp = client.get("/tips/nonexistent_tip", headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_tip_requires_auth(self, client):
        resp = client.get("/tips")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════
#  DISEASE REPORTS TESTS
# ═══════════════════════════════════════════════════════════

class TestDiseaseReports:
    report_id = None

    def test_create_report(self, client):
        resp = client.post(
            "/disease-reports",
            json={
                "crop": "paddy",
                "disease_name": "Blast suspected",
                "symptoms_description": "পাতায় ডায়মন্ড আকারের বাদামি দাগ দেখা যাচ্ছে। অনেক গাছ আক্রান্ত।",
                "severity": "high",
                "district": "Comilla",
                "upazila": "Laksam",
                "latitude": 23.23,
                "longitude": 91.12,
            },
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["crop"] == "paddy"
        assert data["severity"] == "high"
        assert data["status"] == "pending"
        assert data["reported_by"] == FARMER_TOKEN
        TestDiseaseReports.report_id = data["id"]

    def test_list_reports(self, client):
        resp = client.get("/disease-reports", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_list_my_reports(self, client):
        resp = client.get("/disease-reports?my_reports=true", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["reported_by"] == FARMER_TOKEN

    def test_filter_reports_by_district(self, client):
        resp = client.get("/disease-reports?district=Comilla", headers=AUTH_HEADER)
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["district"] == "Comilla"

    def test_get_report_by_id(self, client):
        assert TestDiseaseReports.report_id is not None
        resp = client.get(f"/disease-reports/{TestDiseaseReports.report_id}", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == TestDiseaseReports.report_id

    def test_update_report_status(self, client):
        assert TestDiseaseReports.report_id is not None
        resp = client.patch(
            f"/disease-reports/{TestDiseaseReports.report_id}?status=reviewed",
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "reviewed"

    def test_update_report_invalid_status(self, client):
        assert TestDiseaseReports.report_id is not None
        resp = client.patch(
            f"/disease-reports/{TestDiseaseReports.report_id}?status=invalid_status",
            headers=AUTH_HEADER,
        )
        assert resp.status_code == 400

    def test_get_nonexistent_report(self, client):
        resp = client.get("/disease-reports/nonexistent_report_id", headers=AUTH_HEADER)
        assert resp.status_code == 404

    def test_create_report_requires_auth(self, client):
        resp = client.post(
            "/disease-reports",
            json={
                "crop": "tomato",
                "symptoms_description": "পাতায় দাগ পড়েছে।",
                "severity": "low",
                "district": "Dhaka",
            },
        )
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════
#  STATS ENDPOINT TESTS
# ═══════════════════════════════════════════════════════════

class TestStats:
    def test_global_stats(self, client):
        resp = client.get("/disease-reports/stats/summary", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_reports" in data
        assert "by_crop" in data
        assert "by_severity" in data
        assert "by_status" in data
        assert data["total_reports"] >= 0

    def test_district_stats(self, client):
        resp = client.get("/disease-reports/stats/summary?district=Comilla", headers=AUTH_HEADER)
        assert resp.status_code == 200
        data = resp.json()
        assert data["district_filter"] == "Comilla"


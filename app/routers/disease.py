"""
Router: Disease Diagnosis & Agricultural Tips
Endpoints:
  GET  /diseases                – browse / search disease database
  GET  /diseases/{disease_id}   – single disease detail
  POST /diseases/diagnose       – keyword-based diagnosis from symptoms
  GET  /tips                    – browse farming management tips
  GET  /tips/{tip_id}           – single tip detail
  POST /disease-reports         – farmer submits a field disease report (with photos)
  GET  /disease-reports         – admin/farmer views own reports
  GET  /disease-reports/{id}    – single report
  PATCH /disease-reports/{id}   – update report status (admin)
  GET  /diseases/crops          – list of supported crops
"""

import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from ..db.base import DocStore
from ..deps import CurrentUser, get_current_user, get_storage, get_store
from ..storage import FileStorage
from ..config import get_settings
from ..utils import norm, now

from ..disease_data import DISEASE_DB, FARMING_TIPS
from ..disease_schemas import (
    DiagnosisRequest,
    DiagnosisResponse,
    DiagnosisMatch,
    DiseaseOut,
    DiseasePage,
    DiseaseReportCreate,
    DiseaseReportOut,
    DiseaseReportPage,
    SeasonType,
    TipOut,
    TipPage,
)

router = APIRouter(tags=["Disease & Agri Tips"])
logger = logging.getLogger("krishi.disease")

REPORT_COL = "disease_reports"
FETCH_CAP = 500
ALLOWED_IMAGES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════

def _disease_to_out(d: dict) -> DiseaseOut:
    return DiseaseOut(**d)


def _tip_to_out(t: dict) -> TipOut:
    return TipOut(**t)


def _score_disease(disease: dict, crop_key: str, symptom_tokens: list[str], affected_part: str | None, season: str | None) -> float:
    """
    Simple keyword-overlap scoring:
    - Crop match        → +0.4
    - Symptom keywords  → up to +0.4 (proportional to match fraction)
    - Affected part     → +0.1
    - Season match      → +0.1
    """
    score = 0.0

    # Crop match
    d_crop = norm(disease.get("crop", ""))
    if d_crop == "general":
        score += 0.15
    elif d_crop == crop_key:
        score += 0.40

    # Symptom keyword overlap
    symptoms_text = norm(disease.get("symptoms_bn", "") + " " + disease.get("name_bn", "") + " " + disease.get("name", ""))
    causes_text = norm(disease.get("causes_bn", ""))
    combined = symptoms_text + " " + causes_text

    if symptom_tokens:
        matches = sum(1 for tok in symptom_tokens if tok and tok in combined)
        score += 0.40 * (matches / len(symptom_tokens))

    # Affected part bonus
    if affected_part:
        parts = [norm(p) for p in disease.get("affected_parts", [])]
        if norm(affected_part) in parts or "general" in parts:
            score += 0.10

    # Season bonus
    if season and season in disease.get("season", []):
        score += 0.10

    return round(min(score, 1.0), 3)


# ═══════════════════════════════════════════════════════════
#  DISEASE DATABASE ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/diseases/crops", response_model=list[str], summary="List supported crops")
def list_supported_crops(_: CurrentUser = Depends(get_current_user)):
    """Return the unique list of crop keys present in the disease database."""
    crops = sorted({d["crop"] for d in DISEASE_DB})
    return crops


@router.get("/diseases", response_model=DiseasePage, summary="Browse disease database")
def list_diseases(
    crop: str | None = Query(None, description="Filter by crop (e.g. paddy, potato, tomato)"),
    category: str | None = Query(None, description="Filter by category: fungal, bacterial, viral, pest"),
    severity: str | None = Query(None, description="Filter by severity: low, medium, high"),
    season: SeasonType | None = Query(None, description="kharif or rabi"),
    q: str | None = Query(None, description="Keyword search in disease name / symptoms (Bangla or English)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: CurrentUser = Depends(get_current_user),
):
    """
    Browse all crop diseases with optional filters.
    All text is in Bangla. Useful for building a searchable encyclopedia in the Flutter app.
    """
    results = list(DISEASE_DB)  # copy

    if crop:
        ck = norm(crop)
        results = [d for d in results if norm(d["crop"]) == ck or d["crop"] == "general"]

    if category:
        catk = norm(category)
        results = [d for d in results if norm(d["category"]) == catk]

    if severity:
        sevk = norm(severity)
        results = [d for d in results if norm(d["severity"]) == sevk]

    if season:
        results = [d for d in results if season.value in d.get("season", [])]

    if q:
        qk = norm(q)
        results = [
            d for d in results
            if qk in norm(d.get("name", ""))
            or qk in norm(d.get("name_bn", ""))
            or qk in norm(d.get("symptoms_bn", ""))
            or qk in norm(d.get("crop_bn", ""))
            or qk in norm(d.get("crop", ""))
        ]

    total = len(results)
    page = results[offset: offset + limit]
    return DiseasePage(total=total, limit=limit, offset=offset, items=[DiseaseOut(**d) for d in page])


@router.get("/diseases/{disease_id}", response_model=DiseaseOut, summary="Get disease detail")
def get_disease(disease_id: str, _: CurrentUser = Depends(get_current_user)):
    """Get complete information about a specific disease by its ID."""
    for d in DISEASE_DB:
        if d["id"] == disease_id:
            return DiseaseOut(**d)
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Disease '{disease_id}' not found")


# ═══════════════════════════════════════════════════════════
#  DIAGNOSIS ENGINE
# ═══════════════════════════════════════════════════════════

@router.post("/diseases/diagnose", response_model=DiagnosisResponse, summary="Diagnose disease from symptoms")
def diagnose_disease(
    body: DiagnosisRequest,
    _: CurrentUser = Depends(get_current_user),
):
    """
    Keyword-based diagnosis engine.
    Pass the crop name and symptom description; returns ranked disease matches with remedies.

    - **crop**: e.g. `paddy`, `potato`, `tomato`
    - **symptoms**: Describe what you see on the plant (Bangla or English)
    - **affected_part**: leaf, stem, fruit, root, flower, panicle (optional)
    - **season**: kharif or rabi (optional, improves ranking)
    """
    crop_key = norm(body.crop)
    # Tokenize symptoms (remove very short tokens)
    symptom_tokens = [t for t in norm(body.symptoms).split() if len(t) >= 3]
    season_val = body.season.value if body.season else None

    # Score every disease
    scored = []
    for disease in DISEASE_DB:
        s = _score_disease(disease, crop_key, symptom_tokens, body.affected_part, season_val)
        if s > 0.1:  # ignore very low relevance
            scored.append((s, disease))

    scored.sort(key=lambda x: -x[0])
    top = scored[:5]  # return top 5 matches

    matches = [
        DiagnosisMatch(
            disease_id=d["id"],
            name=d["name"],
            name_bn=d["name_bn"],
            crop_bn=d["crop_bn"],
            match_score=s,
            severity=d["severity"],
            top_remedies=d["remedies_bn"][:3],
            top_prevention=d["prevention_bn"][:3],
        )
        for s, d in top
    ]

    if not matches:
        general_advice = (
            "আপনার বর্ণনার সাথে মিলে এমন কোনো রোগ পাওয়া যায়নি। "
            "দয়া করে স্থানীয় কৃষি অফিসে যোগাযোগ করুন অথবা উপজেলা কৃষি কর্মকর্তার পরামর্শ নিন।"
        )
    elif matches[0].match_score < 0.3:
        general_advice = (
            "আপনার লক্ষণের সাথে মিলতে পারে এমন কিছু রোগ নিচে দেখানো হয়েছে, "
            "তবে নিশ্চিত হতে স্থানীয় কৃষি বিশেষজ্ঞের পরামর্শ নিন।"
        )
    else:
        top_disease = top[0][1]
        general_advice = (
            f"আপনার ফসলে সম্ভবত **{top_disease['name_bn']}** হয়েছে। "
            f"এটি একটি {top_disease['category']} জনিত রোগ। "
            "নিচের প্রতিকার ও প্রতিরোধ ব্যবস্থা দ্রুত অনুসরণ করুন। "
            "প্রয়োজনে উপজেলা কৃষি অফিসে যোগাযোগ করুন।"
        )

    return DiagnosisResponse(
        query_crop=body.crop,
        query_symptoms=body.symptoms,
        matches=matches,
        general_advice_bn=general_advice,
    )


# ═══════════════════════════════════════════════════════════
#  FARMING TIPS ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/tips", response_model=TipPage, summary="Browse farming management tips")
def list_tips(
    crop: str | None = Query(None, description="Filter by crop (use 'all' for universal tips)"),
    category: str | None = Query(None, description="Tip category: soil, irrigation, fertilizer, pest_management, seed, post_harvest, organic, management, weather, integrated_farming"),
    season: SeasonType | None = Query(None),
    q: str | None = Query(None, description="Keyword search in tip title / body"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: CurrentUser = Depends(get_current_user),
):
    """
    Browse agricultural best practices and farming tips.
    Tips are in Bangla and cover: soil management, irrigation, IPM, seeds, post-harvest, organic farming, etc.
    """
    results = list(FARMING_TIPS)

    if crop:
        ck = norm(crop)
        results = [t for t in results if "all" in t.get("crops", []) or ck in [norm(c) for c in t.get("crops", [])]]

    if category:
        catk = norm(category)
        results = [t for t in results if norm(t.get("category", "")) == catk]

    if season:
        results = [t for t in results if season.value in t.get("season", [])]

    if q:
        qk = norm(q)
        results = [
            t for t in results
            if qk in norm(t.get("title_bn", ""))
            or qk in norm(t.get("body_bn", ""))
            or qk in norm(t.get("category_bn", ""))
        ]

    total = len(results)
    page = results[offset: offset + limit]
    return TipPage(total=total, limit=limit, offset=offset, items=[TipOut(**t) for t in page])


@router.get("/tips/{tip_id}", response_model=TipOut, summary="Get farming tip detail")
def get_tip(tip_id: str, _: CurrentUser = Depends(get_current_user)):
    """Get a single farming tip by ID."""
    for t in FARMING_TIPS:
        if t["id"] == tip_id:
            return TipOut(**t)
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Tip '{tip_id}' not found")


# ═══════════════════════════════════════════════════════════
#  DISEASE FIELD REPORTS (farmer-submitted)
# ═══════════════════════════════════════════════════════════

@router.post("/disease-reports", response_model=DiseaseReportOut, status_code=201, summary="Submit a field disease report")
def create_disease_report(
    body: DiseaseReportCreate,
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """
    Farmer submits a report about a disease observed in the field.
    This creates a community record that helps track disease spread across districts.
    Photo URLs can be added separately via `POST /disease-reports/{id}/photos`.
    """
    doc = body.model_dump(mode="json")
    doc.update(
        reported_by=user.uid,
        reporter_name=user.display_name,
        created_at=now().isoformat(),
        status="pending",
    )
    report_id = store.add(REPORT_COL, doc)
    return DiseaseReportOut(**doc, id=report_id)


@router.get("/disease-reports", response_model=DiseaseReportPage, summary="List disease reports")
def list_disease_reports(
    district: str | None = Query(None),
    crop: str | None = Query(None),
    severity: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status", description="pending | reviewed | resolved"),
    my_reports: bool = Query(False, description="If true, return only my own reports"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """
    List field disease reports. Useful for community disease surveillance.
    - Farmers see all reports in their district or just their own (`my_reports=true`).
    - Reports include GPS coordinates for map visualization.
    """
    where = []
    if my_reports:
        where.append(("reported_by", "==", user.uid))
    if district:
        where.append(("district", "==", district))
    if crop:
        where.append(("crop", "==", norm(crop)))
    if severity:
        where.append(("severity", "==", severity))
    if status_filter:
        where.append(("status", "==", status_filter))

    rows = store.query(REPORT_COL, where=where or None, limit=FETCH_CAP)
    rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)

    total = len(rows)
    page = rows[offset: offset + limit]
    return DiseaseReportPage(
        total=total, limit=limit, offset=offset,
        items=[DiseaseReportOut(**r) for r in page],
    )


@router.get("/disease-reports/{report_id}", response_model=DiseaseReportOut, summary="Get report detail")
def get_disease_report(
    report_id: str,
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    doc = store.get(REPORT_COL, report_id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Report not found")
    return DiseaseReportOut(**doc)


@router.patch("/disease-reports/{report_id}", response_model=DiseaseReportOut, summary="Update report status")
def update_disease_report(
    report_id: str,
    new_status: str = Query(..., description="New status: reviewed | resolved"),
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """Update the status of a disease report (reported_by or any authenticated user)."""
    doc = store.get(REPORT_COL, report_id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Report not found")

    allowed_statuses = {"pending", "reviewed", "resolved"}
    if new_status not in allowed_statuses:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Status must be one of: {allowed_statuses}")

    store.update(REPORT_COL, report_id, {"status": new_status})
    doc["status"] = new_status
    return DiseaseReportOut(**doc)


@router.post("/disease-reports/{report_id}/photos", response_model=DiseaseReportOut, summary="Upload photos for a disease report")
def upload_report_photos(
    report_id: str,
    files: list[UploadFile] = File(...),
    user: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
    storage: FileStorage = Depends(get_storage),
):
    """Upload up to 5 field photos (JPEG/PNG/WEBP) for a disease report."""
    doc = store.get(REPORT_COL, report_id)
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Report not found")
    if doc["reported_by"] != user.uid:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not your report")

    existing_photos = doc.get("photo_urls", [])
    if len(existing_photos) + len(files) > 5:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="A report can have at most 5 photos")

    limit_bytes = get_settings().max_upload_mb * 1024 * 1024
    urls = []
    for f in files:
        ext = ALLOWED_IMAGES.get(f.content_type or "")
        if not ext:
            raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only JPEG, PNG or WEBP images allowed")
        data = f.file.read(limit_bytes + 1)
        if len(data) > limit_bytes:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"Each image must be under {get_settings().max_upload_mb} MB")
        url = storage.upload(f"disease-reports/{report_id}/{uuid.uuid4().hex}.{ext}", data, f.content_type)
        urls.append(url)

    updated_urls = existing_photos + urls
    store.update(REPORT_COL, report_id, {"photo_urls": updated_urls})
    doc["photo_urls"] = updated_urls
    return DiseaseReportOut(**doc)


# ═══════════════════════════════════════════════════════════
#  QUICK STATS (community dashboard)
# ═══════════════════════════════════════════════════════════

@router.get("/disease-reports/stats/summary", summary="Disease report statistics", tags=["Disease & Agri Tips"])
def disease_report_stats(
    district: str | None = Query(None),
    _: CurrentUser = Depends(get_current_user),
    store: DocStore = Depends(get_store),
):
    """
    Quick summary: how many reports by crop, severity, and status.
    Useful for displaying a community disease map or dashboard.
    """
    where = []
    if district:
        where.append(("district", "==", district))

    rows = store.query(REPORT_COL, where=where or None, limit=FETCH_CAP)

    by_crop: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    by_status: dict[str, int] = {}

    for r in rows:
        crop = r.get("crop", "unknown")
        sev = r.get("severity", "unknown")
        st = r.get("status", "unknown")
        by_crop[crop] = by_crop.get(crop, 0) + 1
        by_severity[sev] = by_severity.get(sev, 0) + 1
        by_status[st] = by_status.get(st, 0) + 1

    return {
        "total_reports": len(rows),
        "by_crop": by_crop,
        "by_severity": by_severity,
        "by_status": by_status,
        "district_filter": district,
    }


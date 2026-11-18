"""
Pydantic schemas for Disease Diagnosis & Agricultural Tips module.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ─────────────────────────── Enums ───────────────────────────

class DiseaseCategory(str, Enum):
    fungal = "fungal"
    bacterial = "bacterial"
    viral = "viral"
    pest = "pest"
    nutritional = "nutritional"
    other = "other"


class CropType(str, Enum):
    paddy = "paddy"
    potato = "potato"
    tomato = "tomato"
    jute = "jute"
    wheat = "wheat"
    mustard = "mustard"
    onion = "onion"
    brinjal = "brinjal"
    chili = "chili"
    sugarcane = "sugarcane"
    general = "general"
    other = "other"


class SeasonType(str, Enum):
    kharif = "kharif"   # খরিফ (বর্ষা)
    rabi = "rabi"       # রবি (শীতকাল)
    zaid = "zaid"       # জায়িদ (গ্রীষ্মকাল)


class SeverityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TipCategory(str, Enum):
    soil = "soil"
    irrigation = "irrigation"
    fertilizer = "fertilizer"
    pest_management = "pest_management"
    seed = "seed"
    post_harvest = "post_harvest"
    organic = "organic"
    management = "management"
    weather = "weather"
    integrated_farming = "integrated_farming"


# ─────────────────────────── Disease Schemas ───────────────────────────

class DiseaseOut(BaseModel):
    id: str
    crop: str
    crop_bn: str
    name: str
    name_bn: str
    category: str
    affected_parts: list[str]
    symptoms_bn: str
    causes_bn: str
    remedies_bn: list[str]
    prevention_bn: list[str]
    severity: str
    season: list[str]
    image_hint: str | None = None


class DiseasePage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[DiseaseOut]


# ─────────────────────────── Custom Diagnosis ───────────────────────────

class DiagnosisRequest(BaseModel):
    crop: str = Field(..., min_length=1, max_length=100, description="Crop name or type (e.g. 'paddy', 'potato')")
    symptoms: str = Field(..., min_length=5, max_length=2000, description="Describe the symptoms you observe (Bangla or English)")
    affected_part: str | None = Field(None, max_length=100, description="Which part of the plant is affected (e.g. leaf, stem, fruit)")
    season: SeasonType | None = None
    district: str | None = Field(None, max_length=100)


class DiagnosisMatch(BaseModel):
    disease_id: str
    name: str
    name_bn: str
    crop_bn: str
    match_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0–1")
    severity: str
    top_remedies: list[str]
    top_prevention: list[str]


class DiagnosisResponse(BaseModel):
    query_crop: str
    query_symptoms: str
    matches: list[DiagnosisMatch]
    general_advice_bn: str


# ─────────────────────────── Farming Tips Schemas ───────────────────────────

class TipOut(BaseModel):
    id: str
    category: str
    category_bn: str
    title_bn: str
    body_bn: str
    crops: list[str]
    season: list[str]


class TipPage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[TipOut]


# ─────────────────────────── Report / Feedback ───────────────────────────

class DiseaseReportCreate(BaseModel):
    crop: str = Field(..., min_length=1, max_length=100)
    disease_name: str | None = Field(None, max_length=200)
    symptoms_description: str = Field(..., min_length=10, max_length=2000)
    severity: SeverityLevel = SeverityLevel.medium
    district: str = Field(..., min_length=1, max_length=100)
    upazila: str | None = Field(None, max_length=100)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    photo_urls: list[str] = Field(default_factory=list, max_length=5)
    notes: str | None = Field(None, max_length=1000)


class DiseaseReportOut(DiseaseReportCreate):
    id: str
    reported_by: str
    reporter_name: str | None = None
    created_at: str
    status: str = "pending"   # pending | reviewed | resolved


class DiseaseReportPage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[DiseaseReportOut]


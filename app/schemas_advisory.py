"""
Pydantic schemas for Advisory, Machinery, News, Notifications
"""
from datetime import datetime
from pydantic import BaseModel, Field


# ─── Disease ─────────────────────────────────────────────────────────────────

class DiseaseCreate(BaseModel):
    name_bn: str = Field(..., description="Disease name in Bengali")
    name_en: str | None = None
    crop_name: str = Field(..., description="Affected crop")
    symptoms_bn: str = Field(..., description="Symptoms in Bengali")
    remedy_bn: str = Field(..., description="Remedy / treatment in Bengali")
    prevention_bn: str | None = None
    image_url: str | None = None
    severity: str | None = Field(None, description="low | medium | high")


class DiseaseUpdate(BaseModel):
    name_bn: str | None = None
    name_en: str | None = None
    crop_name: str | None = None
    symptoms_bn: str | None = None
    remedy_bn: str | None = None
    prevention_bn: str | None = None
    image_url: str | None = None
    severity: str | None = None


class DiseaseOut(DiseaseCreate):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ─── Farming Tips ────────────────────────────────────────────────────────────

class TipCreate(BaseModel):
    title_bn: str
    body_bn: str
    category: str = Field("general", description="general | soil | irrigation | pesticide | harvest")
    image_url: str | None = None


class TipUpdate(BaseModel):
    title_bn: str | None = None
    body_bn: str | None = None
    category: str | None = None
    image_url: str | None = None


class TipOut(TipCreate):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ─── Machinery ───────────────────────────────────────────────────────────────

class MachineryCreate(BaseModel):
    name: str = Field(..., description="Owner / provider name")
    machine_type: str = Field(..., description="tractor | harvester | pump | thresher | other")
    description_bn: str | None = None
    phone: str
    district: str
    upazila: str | None = None
    address: str | None = None
    daily_rate_bdt: float | None = Field(None, gt=0)
    availability: str | None = Field("available", description="available | busy | unavailable")


class MachineryUpdate(BaseModel):
    name: str | None = None
    machine_type: str | None = None
    description_bn: str | None = None
    phone: str | None = None
    district: str | None = None
    upazila: str | None = None
    address: str | None = None
    daily_rate_bdt: float | None = Field(None, gt=0)
    availability: str | None = None


class MachineryOut(MachineryCreate):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ─── News ────────────────────────────────────────────────────────────────────

class NewsCreate(BaseModel):
    title_bn: str
    body_bn: str
    category: str = Field("general", description="subsidy | policy | alert | general")
    source: str | None = None
    image_url: str | None = None
    external_url: str | None = None


class NewsUpdate(BaseModel):
    title_bn: str | None = None
    body_bn: str | None = None
    category: str | None = None
    source: str | None = None
    image_url: str | None = None
    external_url: str | None = None


class NewsOut(NewsCreate):
    id: str
    published_at: datetime | None = None
    updated_at: datetime | None = None


# ─── Weather Alerts ──────────────────────────────────────────────────────────

class WeatherAlertCreate(BaseModel):
    title_bn: str
    message_bn: str
    district: str | None = Field(None, description="Specific district or None for all")
    alert_type: str = Field("rain", description="rain | storm | flood | drought | cold | heat")
    severity: str = Field("medium", description="low | medium | high | critical")


class WeatherAlertOut(WeatherAlertCreate):
    id: str
    active: bool = True
    created_at: datetime | None = None
    deactivated_at: datetime | None = None


# ─── FCM ─────────────────────────────────────────────────────────────────────

class FCMTokenRegister(BaseModel):
    token: str = Field(..., min_length=10)
    district: str | None = None
    platform: str = Field("android", description="android | ios | web")


class FCMSendRequest(BaseModel):
    title: str
    body: str
    token: str | None = None   # for direct send
    topic: str | None = None   # for topic send
    data: dict | None = None

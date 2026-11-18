"""
Schemas for Feature 3: Push Weather Alerts (FCM-based)
and Feature 4: Machinery Directory & Ag-News
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


# ============================================================
# FEATURE 3 — Weather Alerts & FCM Device Registration
# ============================================================

class WeatherAlertType(str, Enum):
    storm          = "storm"           # ঝড়
    heavy_rain     = "heavy_rain"      # ভারী বৃষ্টি
    flood          = "flood"           # বন্যা
    drought        = "drought"         # খরা
    cyclone        = "cyclone"         # সাইক্লোন
    frost          = "frost"           # শীতল আবহাওয়া
    heatwave       = "heatwave"        # তাপপ্রবাহ
    general        = "general"         # সাধারণ সতর্কতা


class AlertSeverity(str, Enum):
    info     = "info"      # তথ্য
    warning  = "warning"   # সতর্কতা
    danger   = "danger"    # বিপদ


# --- FCM Device Token ---
class FCMTokenRegister(BaseModel):
    fcm_token: str = Field(..., min_length=10, description="Firebase Cloud Messaging device token")
    district:  str | None = Field(None, description="User's district for location-based alerts")
    upazila:   str | None = Field(None, description="User's upazila")
    latitude:  float | None = Field(None, ge=-90,  le=90)
    longitude: float | None = Field(None, ge=-180, le=180)


class FCMTokenOut(BaseModel):
    uid:       str
    fcm_token: str
    district:  str | None = None
    upazila:   str | None = None
    latitude:  float | None = None
    longitude: float | None = None
    registered_at: datetime


# --- Weather Alert (admin sends, users receive) ---
class WeatherAlertCreate(BaseModel):
    alert_type:  WeatherAlertType = WeatherAlertType.general
    severity:    AlertSeverity    = AlertSeverity.warning
    title_bn:    str = Field(..., min_length=2, max_length=200, description="Alert title in Bangla")
    title_en:    str | None = Field(None, max_length=200)
    body_bn:     str = Field(..., min_length=5, max_length=2000, description="Alert body in Bangla")
    body_en:     str | None = Field(None, max_length=2000)
    # Targeting: empty = broadcast to ALL; set districts to narrow scope
    target_districts: list[str] = Field(
        default_factory=list,
        description="Leave empty to broadcast to all. Set district names to target specific areas."
    )
    source:      str | None = Field(None, max_length=100, description="e.g. 'BMD' (Bangladesh Meteorological Dept)")
    valid_until: datetime | None = None
    extra_data:  dict[str, Any] = Field(default_factory=dict, description="Extra key-value payload")


class WeatherAlertOut(BaseModel):
    id:               str
    alert_type:       WeatherAlertType
    severity:         AlertSeverity
    title_bn:         str
    title_en:         str | None = None
    body_bn:          str
    body_en:          str | None = None
    target_districts: list[str] = []
    source:           str | None = None
    valid_until:      datetime | None = None
    extra_data:       dict[str, Any] = {}
    sent_count:       int = 0           # how many FCM pushes were dispatched
    created_at:       datetime
    created_by:       str               # admin uid


class WeatherAlertPage(BaseModel):
    total:  int
    limit:  int
    offset: int
    items:  list[WeatherAlertOut]


# ============================================================
# FEATURE 4A — Machinery Directory
# ============================================================

class MachineryType(str, Enum):
    tractor         = "tractor"          # ট্র্যাক্টর
    harvester       = "harvester"        # হার্ভেস্টার / কম্বাইন
    power_tiller    = "power_tiller"     # পাওয়ার টিলার
    rice_transplanter = "rice_transplanter"  # রাইস ট্রান্সপ্লান্টার
    thresher        = "thresher"         # থ্রেশার
    irrigation_pump = "irrigation_pump"  # সেচ পাম্প
    sprayer         = "sprayer"          # স্প্রেয়ার
    other           = "other"


class MachineryAvailability(str, Enum):
    available   = "available"    # পাওয়া যাচ্ছে
    booked      = "booked"       # বুকড
    unavailable = "unavailable"  # অনুপলব্ধ


class MachineryCreate(BaseModel):
    machinery_type: MachineryType = MachineryType.other
    brand_model:    str | None = Field(None, max_length=100, description="e.g. 'Kubota L4508'")
    owner_name:     str = Field(..., min_length=2, max_length=100)
    phone:          str = Field(..., min_length=7, max_length=20)
    district:       str = Field(..., min_length=1)
    upazila:        str | None = None
    address:        str | None = Field(None, max_length=300)
    latitude:       float | None = Field(None, ge=-90,  le=90)
    longitude:      float | None = Field(None, ge=-180, le=180)
    rate_per_hour:  float | None = Field(None, gt=0, description="Rate per hour in BDT")
    rate_per_bigha: float | None = Field(None, gt=0, description="Rate per bigha in BDT")
    rate_per_acre:  float | None = Field(None, gt=0, description="Rate per acre in BDT")
    availability:   MachineryAvailability = MachineryAvailability.available
    description:    str | None = Field(None, max_length=1000)
    photo_urls:     list[str] = Field(default_factory=list, max_length=5)


class MachineryUpdate(BaseModel):
    brand_model:    str | None = Field(None, max_length=100)
    owner_name:     str | None = Field(None, min_length=2, max_length=100)
    phone:          str | None = Field(None, min_length=7, max_length=20)
    district:       str | None = None
    upazila:        str | None = None
    address:        str | None = Field(None, max_length=300)
    latitude:       float | None = Field(None, ge=-90,  le=90)
    longitude:      float | None = Field(None, ge=-180, le=180)
    rate_per_hour:  float | None = Field(None, gt=0)
    rate_per_bigha: float | None = Field(None, gt=0)
    rate_per_acre:  float | None = Field(None, gt=0)
    availability:   MachineryAvailability | None = None
    description:    str | None = Field(None, max_length=1000)
    photo_urls:     list[str] | None = Field(None, max_length=5)


class MachineryOut(MachineryCreate):
    id:           str
    posted_by:    str               # uid of the user who added the entry
    created_at:   datetime
    updated_at:   datetime | None = None
    distance_km:  float | None = None


class MachineryPage(BaseModel):
    total:  int
    limit:  int
    offset: int
    items:  list[MachineryOut]


# ============================================================
# FEATURE 4B — Ag-News (Government Subsidies & Policy Updates)
# ============================================================

class NewsCategory(str, Enum):
    subsidy      = "subsidy"       # ভর্তুকি
    policy       = "policy"        # নীতিমালা
    price_support = "price_support" # মূল্য সহায়তা
    training     = "training"      # প্রশিক্ষণ
    technology   = "technology"    # প্রযুক্তি
    weather      = "weather"       # আবহাওয়া সংক্রান্ত
    general      = "general"       # সাধারণ সংবাদ


class NewsCreate(BaseModel):
    category:    NewsCategory = NewsCategory.general
    title_bn:    str = Field(..., min_length=3, max_length=300)
    title_en:    str | None = Field(None, max_length=300)
    body_bn:     str = Field(..., min_length=10, max_length=10000)
    body_en:     str | None = Field(None, max_length=10000)
    source:      str | None = Field(None, max_length=200, description="e.g. 'Ministry of Agriculture'")
    source_url:  str | None = Field(None, max_length=500)
    cover_image: str | None = Field(None, max_length=500)
    tags:        list[str] = Field(default_factory=list, max_length=10)
    # Optionally target specific districts (empty = national / all)
    target_districts: list[str] = Field(default_factory=list)
    published_at: datetime | None = None   # None = publish immediately
    expires_at:   datetime | None = None


class NewsUpdate(BaseModel):
    category:    NewsCategory | None = None
    title_bn:    str | None = Field(None, min_length=3, max_length=300)
    title_en:    str | None = Field(None, max_length=300)
    body_bn:     str | None = Field(None, min_length=10, max_length=10000)
    body_en:     str | None = Field(None, max_length=10000)
    source:      str | None = Field(None, max_length=200)
    source_url:  str | None = Field(None, max_length=500)
    cover_image: str | None = Field(None, max_length=500)
    tags:        list[str] | None = Field(None, max_length=10)
    target_districts: list[str] | None = None
    published_at: datetime | None = None
    expires_at:   datetime | None = None
    is_active:   bool | None = None


class NewsOut(BaseModel):
    id:               str
    category:         NewsCategory
    title_bn:         str
    title_en:         str | None = None
    body_bn:          str
    body_en:          str | None = None
    source:           str | None = None
    source_url:       str | None = None
    cover_image:      str | None = None
    tags:             list[str] = []
    target_districts: list[str] = []
    published_at:     datetime
    expires_at:       datetime | None = None
    is_active:        bool = True
    created_by:       str
    created_at:       datetime
    updated_at:       datetime | None = None
    views:            int = 0


class NewsPage(BaseModel):
    total:  int
    limit:  int
    offset: int
    items:  list[NewsOut]

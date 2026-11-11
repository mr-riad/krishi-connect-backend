from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class Category(str, Enum):
    paddy = "paddy"          # ধান
    vegetable = "vegetable"  # সবজি
    fruit = "fruit"          # ফল
    pulse = "pulse"          # ডাল
    spice = "spice"          # মসলা
    other = "other"


class Unit(str, Enum):
    kg = "kg"      # কেজি
    mon = "mon"    # মণ (=40 kg)
    ton = "ton"    # টন
    bag = "bag"    # বস্তা (assumed 50 kg)


UNIT_TO_KG = {Unit.kg: 1.0, Unit.mon: 40.0, Unit.ton: 1000.0, Unit.bag: 50.0}


class ListingStatus(str, Enum):
    active = "active"
    sold = "sold"
    closed = "closed"


class ListingSort(str, Enum):
    newest = "newest"
    price_asc = "price_asc"
    nearest = "nearest"


class RateSort(str, Enum):
    newest = "newest"
    rate_desc = "rate_desc"
    nearest = "nearest"


# ---------- users ----------
class UserUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    role: str | None = Field(None, pattern="^(farmer|buyer)$")  # only settable once
    district: str | None = None
    upazila: str | None = None
    address: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)


class UserOut(BaseModel):
    uid: str
    role: str | None = None
    name: str | None = None
    phone: str | None = None
    district: str | None = None
    upazila: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


# ---------- listings ----------
class ListingBase(BaseModel):
    crop_name: str = Field(..., min_length=1, max_length=100)
    category: Category = Category.other
    quantity: float = Field(..., gt=0)
    unit: Unit = Unit.kg
    price_per_unit: float = Field(..., gt=0, description="Target price per chosen unit (BDT)")
    harvest_date: date | None = None
    description: str | None = Field(None, max_length=1000)
    district: str = Field(..., min_length=1)
    upazila: str | None = None
    address: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    photo_urls: list[str] = Field(default_factory=list, max_length=5)


class ListingCreate(ListingBase):
    pass


class ListingUpdate(BaseModel):
    crop_name: str | None = Field(None, min_length=1, max_length=100)
    category: Category | None = None
    quantity: float | None = Field(None, gt=0)
    unit: Unit | None = None
    price_per_unit: float | None = Field(None, gt=0)
    harvest_date: date | None = None
    description: str | None = Field(None, max_length=1000)
    district: str | None = None
    upazila: str | None = None
    address: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    photo_urls: list[str] | None = Field(None, max_length=5)
    status: ListingStatus | None = None


class ListingOut(ListingBase):
    id: str
    status: ListingStatus = ListingStatus.active
    quantity_kg: float
    price_per_kg: float
    farmer_id: str
    farmer_name: str | None = None
    farmer_phone: str | None = None
    created_at: datetime
    distance_km: float | None = None


class ListingPage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[ListingOut]


# ---------- buyer rates ----------
class RateBase(BaseModel):
    crop_name: str = Field(..., min_length=1, max_length=100)
    category: Category = Category.other
    rate_per_unit: float = Field(..., gt=0, description="Buying rate per unit (BDT)")
    unit: Unit = Unit.kg
    demand_quantity: float | None = Field(None, gt=0)
    demand_unit: Unit = Unit.kg
    district: str = Field(..., min_length=1)
    upazila: str | None = None
    address: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    valid_days: int = Field(7, ge=1, le=90, description="Rate stays on the board this many days")


class RateCreate(RateBase):
    pass


class RateUpdate(BaseModel):
    rate_per_unit: float | None = Field(None, gt=0)
    unit: Unit | None = None
    demand_quantity: float | None = Field(None, gt=0)
    demand_unit: Unit | None = None
    valid_days: int | None = Field(None, ge=1, le=90)
    active: bool | None = None


class RateOut(RateBase):
    id: str
    rate_per_kg: float
    active: bool = True
    buyer_id: str
    buyer_name: str | None = None
    buyer_phone: str | None = None
    created_at: datetime
    expires_at: datetime
    distance_km: float | None = None


class RatePage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[RateOut]


# ---------- chat ----------
class ConversationCreate(BaseModel):
    participant_id: str
    listing_id: str | None = None


class ConversationOut(BaseModel):
    id: str
    participants: list[str]
    participant_names: dict[str, str | None] = {}
    listing_id: str | None = None
    listing_title: str | None = None
    last_message: str | None = None
    last_message_at: datetime | None = None
    unread_count: int = 0
    created_at: datetime


class MessageCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    sender_id: str
    text: str
    created_at: datetime


# ---------- call ----------
class CallRequest(BaseModel):
    target_uid: str
    listing_id: str | None = None
    rate_id: str | None = None


class CallOut(BaseModel):
    phone: str
    tel_uri: str
    target_name: str | None = None
    call_log_id: str

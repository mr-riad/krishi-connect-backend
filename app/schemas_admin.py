"""
Pydantic schemas for Admin panel
"""
from datetime import datetime
from pydantic import BaseModel, Field


class AdminUserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    role: str | None = Field(None, pattern="^(farmer|buyer|admin)$")
    district: str | None = None
    upazila: str | None = None
    is_banned: bool | None = None
    is_verified: bool | None = None
    ban_reason: str | None = None
    farm_size_bigha: float | None = None


class AdminUserOut(BaseModel):
    uid: str | None = None
    id: str | None = None
    name: str | None = None
    phone: str | None = None
    role: str | None = None
    district: str | None = None
    upazila: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_banned: bool = False
    is_verified: bool = False
    ban_reason: str | None = None
    farm_size_bigha: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AdminListingModerate(BaseModel):
    status: str = Field(..., description="active | suspended | closed")
    note: str | None = None


class AdminReportResolve(BaseModel):
    action: str = Field(..., pattern="^(resolved|dismissed)$")
    note: str | None = None


class AdminReportOut(BaseModel):
    id: str
    post_id: str | None = None
    reporter_id: str
    reason: str
    status: str = "pending"
    admin_note: str | None = None
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime


class AdminStatsOut(BaseModel):
    total_users: int
    total_farmers: int
    total_buyers: int
    total_listings: int
    active_listings: int
    total_rates: int
    total_forum_posts: int
    pending_reports: int
    active_weather_alerts: int
    total_calls: int
    users_by_district: dict[str, int] = {}

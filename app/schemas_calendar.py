"""Pydantic response schemas for Crop Calendar & Intercropping APIs."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Season ───────────────────────────────────────────────────────────────────

class SeasonOut(BaseModel):
    id: str
    name_bn: str
    name_en: str
    months_bn: str
    months_en: str


# ── Crop ─────────────────────────────────────────────────────────────────────

class CropOut(BaseModel):
    id: str
    season_id: str
    name_bn: str
    name_en: str
    icon: str
    category: str
    sow_months: list[int]
    harvest_months: list[int]
    sow_bn: str
    harvest_bn: str
    companions: list[str] = Field(default_factory=list, description="IDs of companion crops")
    companion_note_bn: str = ""


class CropCompanionOut(BaseModel):
    """Full companion info: the crop itself + its companions expanded."""
    crop: CropOut
    companion_crops: list[CropOut] = Field(default_factory=list)


# ── Intercrop Combo ──────────────────────────────────────────────────────────

class IntercropComboOut(BaseModel):
    id: str
    title_bn: str
    title_en: str
    season_id: str
    primary_crop: str
    companion_crops: list[str]
    benefit_bn: str
    method_bn: str
    expected_benefit: str


# ── Calendar ─────────────────────────────────────────────────────────────────

class SeasonCalendarOut(BaseModel):
    """Full season calendar: season metadata + all crops for that season."""
    season: SeasonOut
    current_month_bn: str
    tip_bn: str
    crops: list[CropOut]


class MonthCalendarOut(BaseModel):
    """Crops whose sow window includes the given month."""
    month: int
    month_bn: str
    crops: list[CropOut]


# ── Full Calendar Response ───────────────────────────────────────────────────

class FullCalendarOut(BaseModel):
    """All 3 seasons with their crops — the entire calendar at once."""
    current_month: int
    current_month_bn: str
    current_season: SeasonOut | None = None
    seasons: list[SeasonCalendarOut]


# ── Intercrop Guide Response ─────────────────────────────────────────────────

class IntercropGuideOut(BaseModel):
    """Full intercropping guide: all combos, optionally filtered."""
    season_id: str | None = None
    combos: list[IntercropComboOut]

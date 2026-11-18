"""
Router for Seasonal Crop Calendar & Intercropping Guide.

Endpoints:
  GET /calendar                       → Full 3-season calendar
  GET /calendar/season/{season_id}    → Single season's crops
  GET /calendar/month/{month}         → Crops sowable in a given month (1-12)

  GET /intercrop                      → All intercrop combo guides
  GET /intercrop/season/{season_id}   → Combos filtered by season
  GET /intercrop/crop/{crop_id}       → Combos involving a specific crop
  GET /intercrop/companions/{crop_id} → Direct companion list for a crop
"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from ..data.crop_calendar import (
    BANGLA_MONTHS,
    INTERCROP_COMBOS,
    SEASONS,
    combos_for_crop,
    combos_for_season,
    companions_for_crop,
    crops_for_month,
    crops_for_season,
    current_season,
    get_crop_by_id,
    get_season_by_id,
)
from ..schemas_calendar import (
    CropCompanionOut,
    CropOut,
    FullCalendarOut,
    IntercropComboOut,
    IntercropGuideOut,
    MonthCalendarOut,
    SeasonCalendarOut,
    SeasonOut,
)

router = APIRouter(tags=["Crop Calendar & Intercropping"])

# ── Season tips (dynamic based on current month vs season) ───────────────────

_SEASON_TIPS = {
    "rabi": "এখন চাষের উপযুক্ত",
    "kharif1": "এখন বপন সময়",
    "kharif2": "আমন মৌসুম চলছে",
}


def _now_month() -> int:
    return datetime.now(timezone.utc).month


# ═══════════════════════════════════════════════════════════════════════════════
#  CALENDAR  ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/calendar", response_model=FullCalendarOut)
def get_full_calendar():
    """Return all 3 seasons with their crops — the entire calendar.
    Also returns the current month & which season it falls in.
    """
    month = _now_month()
    cur_season = current_season(month)

    season_calendars = []
    for s in SEASONS:
        crops = crops_for_season(s["id"])
        season_calendars.append(
            SeasonCalendarOut(
                season=SeasonOut(**{k: s[k] for k in SeasonOut.model_fields}),
                current_month_bn=BANGLA_MONTHS.get(month, ""),
                tip_bn=_SEASON_TIPS.get(s["id"], ""),
                crops=[CropOut(**c) for c in crops],
            )
        )

    return FullCalendarOut(
        current_month=month,
        current_month_bn=BANGLA_MONTHS.get(month, ""),
        current_season=SeasonOut(**{k: cur_season[k] for k in SeasonOut.model_fields}) if cur_season else None,
        seasons=season_calendars,
    )


@router.get("/calendar/season/{season_id}", response_model=SeasonCalendarOut)
def get_season_calendar(season_id: str):
    """Return crops for a specific season (rabi / kharif1 / kharif2)."""
    s = get_season_by_id(season_id)
    if not s:
        raise HTTPException(404, f"Season '{season_id}' not found. Use: rabi, kharif1, kharif2")

    month = _now_month()
    crops = crops_for_season(season_id)
    return SeasonCalendarOut(
        season=SeasonOut(**{k: s[k] for k in SeasonOut.model_fields}),
        current_month_bn=BANGLA_MONTHS.get(month, ""),
        tip_bn=_SEASON_TIPS.get(season_id, ""),
        crops=[CropOut(**c) for c in crops],
    )


@router.get("/calendar/month/{month}", response_model=MonthCalendarOut)
def get_month_calendar(month: int):
    """Return crops whose sow window includes the given month (1-12)."""
    if month < 1 or month > 12:
        raise HTTPException(400, "Month must be 1-12")

    crops = crops_for_month(month)
    return MonthCalendarOut(
        month=month,
        month_bn=BANGLA_MONTHS.get(month, ""),
        crops=[CropOut(**c) for c in crops],
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  INTERCROPPING  ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/intercrop", response_model=IntercropGuideOut)
def get_intercrop_guide(
    season_id: str | None = Query(None, description="Filter by season: rabi, kharif1, kharif2"),
):
    """Return all curated intercropping combination guides.
    Optionally filter by season.
    """
    if isinstance(season_id, str) and season_id.strip():
        sid = season_id.strip()
        if not get_season_by_id(sid):
            raise HTTPException(404, f"Season '{season_id}' not found")
        combos = combos_for_season(sid)
        return IntercropGuideOut(
            season_id=sid,
            combos=[IntercropComboOut(**c) for c in combos],
        )

    return IntercropGuideOut(
        season_id=None,
        combos=[IntercropComboOut(**c) for c in INTERCROP_COMBOS],
    )


@router.get("/intercrop/season/{season_id}", response_model=IntercropGuideOut)
def get_intercrop_by_season(season_id: str):
    """Return intercrop combos for a specific season."""
    if not get_season_by_id(season_id):
        raise HTTPException(404, f"Season '{season_id}' not found")

    combos = combos_for_season(season_id)
    return IntercropGuideOut(
        season_id=season_id,
        combos=[IntercropComboOut(**c) for c in combos],
    )


@router.get("/intercrop/crop/{crop_id}", response_model=IntercropGuideOut)
def get_intercrop_by_crop(crop_id: str):
    """Return intercrop combos involving a specific crop (as primary or companion)."""
    if not get_crop_by_id(crop_id):
        raise HTTPException(404, f"Crop '{crop_id}' not found")

    combos = combos_for_crop(crop_id)
    return IntercropGuideOut(
        season_id=None,
        combos=[IntercropComboOut(**c) for c in combos],
    )


@router.get("/intercrop/companions/{crop_id}", response_model=CropCompanionOut)
def get_companions(crop_id: str):
    """Return direct companion crops for a specific crop."""
    crop = get_crop_by_id(crop_id)
    if not crop:
        raise HTTPException(404, f"Crop '{crop_id}' not found")

    companion_list = companions_for_crop(crop_id)
    return CropCompanionOut(
        crop=CropOut(**crop),
        companion_crops=[CropOut(**c) for c in companion_list],
    )

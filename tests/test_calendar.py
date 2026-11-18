from app.routers.calendar import (
    get_full_calendar,
    get_season_calendar,
    get_month_calendar,
    get_intercrop_guide,
    get_intercrop_by_season,
    get_intercrop_by_crop,
    get_companions,
)
from app.data.crop_calendar import (
    SEASONS,
    CROPS,
    INTERCROP_COMBOS,
    get_crop_by_id,
    crops_for_season,
    crops_for_month,
    current_season,
)
import pytest
from fastapi import HTTPException


def test_calendar_seasons_data():
    assert len(SEASONS) == 3
    season_ids = [s["id"] for s in SEASONS]
    assert "rabi" in season_ids
    assert "kharif1" in season_ids
    assert "kharif2" in season_ids


def test_crops_data_integrity():
    assert len(CROPS) >= 20
    for crop in CROPS:
        assert crop["id"]
        assert crop["name_bn"]
        assert crop["season_id"] in ["rabi", "kharif1", "kharif2"]
        assert len(crop["sow_months"]) > 0
        assert len(crop["harvest_months"]) > 0
        # Verify companion references exist
        for comp_id in crop.get("companions", []):
            assert get_crop_by_id(comp_id) is not None, f"Missing companion {comp_id} for {crop['id']}"


def test_combos_data_integrity():
    assert len(INTERCROP_COMBOS) >= 8
    for combo in INTERCROP_COMBOS:
        assert combo["id"]
        assert combo["title_bn"]
        assert combo["benefit_bn"]
        assert combo["method_bn"]
        assert get_crop_by_id(combo["primary_crop"]) is not None
        for cid in combo["companion_crops"]:
            assert get_crop_by_id(cid) is not None


def test_get_full_calendar():
    res = get_full_calendar()
    assert res.current_month >= 1 and res.current_month <= 12
    assert res.current_month_bn
    assert len(res.seasons) == 3


def test_get_season_calendar():
    res = get_season_calendar("rabi")
    assert res.season.id == "rabi"
    assert len(res.crops) >= 5
    with pytest.raises(HTTPException) as exc:
        get_season_calendar("invalid_season")
    assert exc.value.status_code == 404


def test_get_month_calendar():
    res = get_month_calendar(11)
    assert res.month == 11
    assert res.month_bn == "নভেম্বর"
    assert len(res.crops) >= 5

    with pytest.raises(HTTPException) as exc:
        get_month_calendar(0)
    assert exc.value.status_code == 400

    with pytest.raises(HTTPException) as exc:
        get_month_calendar(13)
    assert exc.value.status_code == 400


def test_get_intercrop_guide():
    res = get_intercrop_guide()
    assert len(res.combos) >= 8

    res_rabi = get_intercrop_guide("rabi")
    assert len(res_rabi.combos) > 0
    assert all(c.season_id == "rabi" for c in res_rabi.combos)

    with pytest.raises(HTTPException) as exc:
        get_intercrop_guide("invalid_season")
    assert exc.value.status_code == 404


def test_get_intercrop_by_crop():
    res = get_intercrop_by_crop("alu")
    assert len(res.combos) >= 2

    with pytest.raises(HTTPException) as exc:
        get_intercrop_by_crop("unknown_crop")
    assert exc.value.status_code == 404


def test_get_companions():
    res = get_companions("gom")
    assert res.crop.id == "gom"
    assert len(res.companion_crops) >= 2
    comp_names = [c.name_bn for c in res.companion_crops]
    assert "মসুর" in comp_names

    with pytest.raises(HTTPException) as exc:
        get_companions("unknown_crop")
    assert exc.value.status_code == 404

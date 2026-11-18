"""
Static crop calendar & intercropping data for Bangladesh.

Three seasons  →  রবি (Rabi), খরিফ-১ (Kharif-1), খরিফ-২ (Kharif-2)
Each crop has  →  Bengali name, icon, sow window, harvest window, category,
                  and companion / intercrop partners.
"""

from __future__ import annotations

# ── Season metadata ──────────────────────────────────────────────────────────

SEASONS: list[dict] = [
    {
        "id": "rabi",
        "name_bn": "রবি",
        "name_en": "Rabi",
        "months_bn": "নভেম্বর – মার্চ",
        "months_en": "November – March",
        "sow_start": 11,   # November
        "sow_end": 3,      # March
    },
    {
        "id": "kharif1",
        "name_bn": "খরিফ-১",
        "name_en": "Kharif-1",
        "months_bn": "মার্চ – জুন",
        "months_en": "March – June",
        "sow_start": 3,
        "sow_end": 6,
    },
    {
        "id": "kharif2",
        "name_bn": "খরিফ-২",
        "name_en": "Kharif-2",
        "months_bn": "জুন – নভেম্বর",
        "months_en": "June – November",
        "sow_start": 6,
        "sow_end": 11,
    },
]

# ── Bangla month names (1-indexed) ───────────────────────────────────────────

BANGLA_MONTHS = {
    1: "জানুয়ারি",
    2: "ফেব্রুয়ারি",
    3: "মার্চ",
    4: "এপ্রিল",
    5: "মে",
    6: "জুন",
    7: "জুলাই",
    8: "আগস্ট",
    9: "সেপ্টেম্বর",
    10: "অক্টোবর",
    11: "নভেম্বর",
    12: "ডিসেম্বর",
}

# ── Crop entries ─────────────────────────────────────────────────────────────
# Each crop belongs to one primary season.
# `sow_months` / `harvest_months` are 1-indexed month numbers.
# `companions` = list of crop_id strings that work well as intercrop.
# `companion_note_bn` = short Bengali explanation of the benefit.

CROPS: list[dict] = [
    # ── রবি (Rabi) ──
    {
        "id": "gom",
        "season_id": "rabi",
        "name_bn": "গম",
        "name_en": "Wheat",
        "icon": "🌾",
        "category": "cereal",
        "sow_months": [11, 12],
        "harvest_months": [3, 4],
        "sow_bn": "নভেম্বর–ডিসেম্বর",
        "harvest_bn": "মার্চ–এপ্রিল",
        "companions": ["mosur", "sorisha", "peyaj"],
        "companion_note_bn": "গমের সারিতে সরিষা বা মসুর আন্তঃফসল হিসেবে ভালো ফলন দেয়।",
    },
    {
        "id": "sorisha",
        "season_id": "rabi",
        "name_bn": "সরিষা",
        "name_en": "Mustard",
        "icon": "🌻",
        "category": "oilseed",
        "sow_months": [10, 11],
        "harvest_months": [2, 3],
        "sow_bn": "অক্টোবর–নভেম্বর",
        "harvest_bn": "ফেব্রুয়ারি–মার্চ",
        "companions": ["mosur", "gom", "peyaj"],
        "companion_note_bn": "সরিষার সাথে মসুর চাষ করলে মাটির নাইট্রোজেন বাড়ে।",
    },
    {
        "id": "alu",
        "season_id": "rabi",
        "name_bn": "আলু",
        "name_en": "Potato",
        "icon": "🥔",
        "category": "tuber",
        "sow_months": [10, 11],
        "harvest_months": [1, 2],
        "sow_bn": "অক্টোবর–নভেম্বর",
        "harvest_bn": "জানুয়ারি–ফেব্রুয়ারি",
        "companions": ["peyaj", "rosun", "dhaniya"],
        "companion_note_bn": "আলুর সারিতে পেঁয়াজ বা ধনিয়া চাষ করলে পোকা কম আসে।",
    },
    {
        "id": "mosur",
        "season_id": "rabi",
        "name_bn": "মসুর",
        "name_en": "Lentil",
        "icon": "🫘",
        "category": "pulse",
        "sow_months": [10, 11],
        "harvest_months": [3, 4],
        "sow_bn": "অক্টোবর–নভেম্বর",
        "harvest_bn": "মার্চ–এপ্রিল",
        "companions": ["sorisha", "gom"],
        "companion_note_bn": "মসুর ডালজাতীয় ফসল—মাটিতে নাইট্রোজেন সংবন্ধন করে সরিষা/গমের উপকারে আসে।",
    },
    {
        "id": "peyaj",
        "season_id": "rabi",
        "name_bn": "পেঁয়াজ",
        "name_en": "Onion",
        "icon": "🧅",
        "category": "spice",
        "sow_months": [11, 12],
        "harvest_months": [3, 4],
        "sow_bn": "নভেম্বর–ডিসেম্বর",
        "harvest_bn": "মার্চ–এপ্রিল",
        "companions": ["rosun", "gom", "alu"],
        "companion_note_bn": "পেঁয়াজ ও রসুন একসাথে চাষে পোকামাকড় দূরে থাকে।",
    },
    {
        "id": "rosun",
        "season_id": "rabi",
        "name_bn": "রসুন",
        "name_en": "Garlic",
        "icon": "🧄",
        "category": "spice",
        "sow_months": [10, 11],
        "harvest_months": [2, 3],
        "sow_bn": "অক্টোবর–নভেম্বর",
        "harvest_bn": "ফেব্রুয়ারি–মার্চ",
        "companions": ["peyaj", "alu", "gom"],
        "companion_note_bn": "রসুনের গন্ধ প্রাকৃতিক কীটনাশক হিসেবে কাজ করে।",
    },
    {
        "id": "dhaniya",
        "season_id": "rabi",
        "name_bn": "ধনিয়া",
        "name_en": "Coriander",
        "icon": "🌿",
        "category": "spice",
        "sow_months": [10, 11],
        "harvest_months": [1, 2],
        "sow_bn": "অক্টোবর–নভেম্বর",
        "harvest_bn": "জানুয়ারি–ফেব্রুয়ারি",
        "companions": ["alu", "peyaj", "mosur"],
        "companion_note_bn": "ধনিয়া দ্রুত বাড়ে ও মাটি ঢেকে রাখে—আগাছা কমায়।",
    },
    {
        "id": "boro_dhan",
        "season_id": "rabi",
        "name_bn": "বোরো ধান",
        "name_en": "Boro Rice",
        "icon": "🌾",
        "category": "paddy",
        "sow_months": [12, 1, 2],
        "harvest_months": [4, 5, 6],
        "sow_bn": "ডিসেম্বর–ফেব্রুয়ারি",
        "harvest_bn": "এপ্রিল–জুন",
        "companions": [],
        "companion_note_bn": "বোরো ধান সাধারণত একক ফসল হিসেবে চাষ হয়।",
    },
    {
        "id": "shobit_sobji",
        "season_id": "rabi",
        "name_bn": "শীতকালীন সবজি",
        "name_en": "Winter Vegetables",
        "icon": "🥬",
        "category": "vegetable",
        "sow_months": [10, 11],
        "harvest_months": [12, 1, 2],
        "sow_bn": "অক্টোবর–নভেম্বর",
        "harvest_bn": "ডিসেম্বর–ফেব্রুয়ারি",
        "companions": ["peyaj", "rosun", "dhaniya"],
        "companion_note_bn": "ফুলকপি/বাঁধাকপির সাথে পেঁয়াজ-রসুন চাষে পোকা কম আসে।",
    },

    # ── খরিফ-১ (Kharif-1) ──
    {
        "id": "aus_dhan",
        "season_id": "kharif1",
        "name_bn": "আউশ ধান",
        "name_en": "Aus Rice",
        "icon": "🌾",
        "category": "paddy",
        "sow_months": [3, 4],
        "harvest_months": [7, 8],
        "sow_bn": "মার্চ–এপ্রিল",
        "harvest_bn": "জুলাই–আগস্ট",
        "companions": [],
        "companion_note_bn": "আউশ ধান একক ফসল হিসেবে চাষ হয়।",
    },
    {
        "id": "mug",
        "season_id": "kharif1",
        "name_bn": "মুগ",
        "name_en": "Mung Bean",
        "icon": "🫘",
        "category": "pulse",
        "sow_months": [2, 3],
        "harvest_months": [5, 6],
        "sow_bn": "ফেব্রুয়ারি–মার্চ",
        "harvest_bn": "মে–জুন",
        "companions": ["til", "grishmo_sobji"],
        "companion_note_bn": "মুগ ডালজাতীয় ফসল—তিলের সাথে আন্তঃফসলে মাটির উর্বরতা বাড়ায়।",
    },
    {
        "id": "til",
        "season_id": "kharif1",
        "name_bn": "তিল",
        "name_en": "Sesame",
        "icon": "🌿",
        "category": "oilseed",
        "sow_months": [3, 4],
        "harvest_months": [6, 7],
        "sow_bn": "মার্চ–এপ্রিল",
        "harvest_bn": "জুন–জুলাই",
        "companions": ["mug"],
        "companion_note_bn": "তিল ও মুগ পাশাপাশি সারিতে চাষ করা যায়।",
    },
    {
        "id": "grishmo_sobji",
        "season_id": "kharif1",
        "name_bn": "গ্রীষ্মকালীন সবজি",
        "name_en": "Summer Vegetables",
        "icon": "🥦",
        "category": "vegetable",
        "sow_months": [2, 3],
        "harvest_months": [5, 6, 7],
        "sow_bn": "ফেব্রুয়ারি–মার্চ",
        "harvest_bn": "মে–জুলাই",
        "companions": ["mug", "til"],
        "companion_note_bn": "লাউ/কুমড়ার মাচায় পুঁইশাক বা মুগ সাথী ফসল হিসেবে চাষ করুন।",
    },
    {
        "id": "jhinga",
        "season_id": "kharif1",
        "name_bn": "ঝিঙা/চিচিঙ্গা",
        "name_en": "Ridge Gourd",
        "icon": "🥒",
        "category": "vegetable",
        "sow_months": [2, 3, 4],
        "harvest_months": [5, 6, 7],
        "sow_bn": "ফেব্রুয়ারি–এপ্রিল",
        "harvest_bn": "মে–জুলাই",
        "companions": ["mug", "puishak"],
        "companion_note_bn": "ঝিঙার মাচায় পুঁইশাক তুলে জমির সর্বোচ্চ ব্যবহার নিশ্চিত করুন।",
    },
    {
        "id": "puishak",
        "season_id": "kharif1",
        "name_bn": "পুঁইশাক",
        "name_en": "Malabar Spinach",
        "icon": "🥬",
        "category": "vegetable",
        "sow_months": [3, 4, 5],
        "harvest_months": [5, 6, 7, 8, 9],
        "sow_bn": "মার্চ–মে",
        "harvest_bn": "মে–সেপ্টেম্বর",
        "companions": ["jhinga", "grishmo_sobji"],
        "companion_note_bn": "পুঁইশাক মাচার ফসলের সাথে সাথী হিসেবে ভালো জন্মে।",
    },

    # ── খরিফ-২ (Kharif-2) ──
    {
        "id": "amon_dhan",
        "season_id": "kharif2",
        "name_bn": "আমন ধান",
        "name_en": "Aman Rice",
        "icon": "🌾",
        "category": "paddy",
        "sow_months": [6, 7, 8],
        "harvest_months": [11, 12],
        "sow_bn": "জুন–আগস্ট",
        "harvest_bn": "নভেম্বর–ডিসেম্বর",
        "companions": [],
        "companion_note_bn": "আমন ধান প্রধানত একক ফসল; আইলে সবজি চাষ সম্ভব।",
    },
    {
        "id": "akh",
        "season_id": "kharif2",
        "name_bn": "আখ",
        "name_en": "Sugarcane",
        "icon": "🎋",
        "category": "cash_crop",
        "sow_months": [1, 2, 3],
        "harvest_months": [11, 12, 1, 2, 3],
        "sow_bn": "জানুয়ারি–মার্চ",
        "harvest_bn": "নভেম্বর–মার্চ",
        "companions": ["alu", "peyaj", "mosur", "mug"],
        "companion_note_bn": "আখের সারির ফাঁকে আলু, পেঁয়াজ বা মুগ আন্তঃফসল করলে অতিরিক্ত আয় হয়।",
    },
    {
        "id": "sheet_sobji_bopon",
        "season_id": "kharif2",
        "name_bn": "শীতকালীন সবজি বপন",
        "name_en": "Winter Veg Nursery",
        "icon": "🥬",
        "category": "vegetable",
        "sow_months": [8, 9],
        "harvest_months": [11, 12, 1],
        "sow_bn": "আগস্ট–সেপ্টেম্বর",
        "harvest_bn": "নভেম্বর–জানুয়ারি",
        "companions": ["peyaj", "rosun"],
        "companion_note_bn": "নার্সারিতে চারা তৈরি করে মূল জমিতে রসুন/পেঁয়াজের সাথে রোপণ করুন।",
    },
    {
        "id": "pat",
        "season_id": "kharif2",
        "name_bn": "পাট",
        "name_en": "Jute",
        "icon": "🪢",
        "category": "fibre",
        "sow_months": [3, 4, 5],
        "harvest_months": [7, 8],
        "sow_bn": "মার্চ–মে",
        "harvest_bn": "জুলাই–আগস্ট",
        "companions": ["mug"],
        "companion_note_bn": "পাটের আগে বা পরে মুগ ক্রপ রোটেশনে মাটির স্বাস্থ্য ভালো থাকে।",
    },
    {
        "id": "morich",
        "season_id": "kharif2",
        "name_bn": "মরিচ",
        "name_en": "Chili",
        "icon": "🌶️",
        "category": "spice",
        "sow_months": [7, 8, 9],
        "harvest_months": [11, 12, 1, 2],
        "sow_bn": "জুলাই–সেপ্টেম্বর",
        "harvest_bn": "নভেম্বর–ফেব্রুয়ারি",
        "companions": ["peyaj", "rosun", "dhaniya"],
        "companion_note_bn": "মরিচের সাথে পেঁয়াজ বা ধনিয়া সাথী ফসল হিসেবে চাষ করুন।",
    },
    {
        "id": "begun",
        "season_id": "kharif2",
        "name_bn": "বেগুন",
        "name_en": "Eggplant",
        "icon": "🍆",
        "category": "vegetable",
        "sow_months": [7, 8, 9],
        "harvest_months": [10, 11, 12, 1, 2, 3],
        "sow_bn": "জুলাই–সেপ্টেম্বর",
        "harvest_bn": "অক্টোবর–মার্চ",
        "companions": ["mug", "peyaj", "dhaniya"],
        "companion_note_bn": "বেগুনের সারিতে ধনিয়া বা পেঁয়াজ চাষে পোকার আক্রমণ কমে।",
    },
]

# ── Intercropping combination guide ──────────────────────────────────────────
# Higher-level curated combination guides beyond per-crop companions.
# These are "proven intercrop recipes" for Bangladeshi farmers.

INTERCROP_COMBOS: list[dict] = [
    {
        "id": "akh_alu",
        "title_bn": "আখ + আলু",
        "title_en": "Sugarcane + Potato",
        "season_id": "rabi",
        "primary_crop": "akh",
        "companion_crops": ["alu"],
        "benefit_bn": "আখের সারির ফাঁকে (৯০ সেমি দূরত্বে) আলু লাগালে অতিরিক্ত ১৫-২০ মণ/বিঘা আলু পাওয়া যায়। আখের বৃদ্ধিতে কোনো ক্ষতি হয় না।",
        "method_bn": "আখ রোপণের পর সারির মাঝে ১ সারি আলু বীজ রোপণ করুন। আলুর জন্য আলাদা সার দিন।",
        "expected_benefit": "১৫-২০% অতিরিক্ত আয়",
    },
    {
        "id": "sorisha_mosur",
        "title_bn": "সরিষা + মসুর",
        "title_en": "Mustard + Lentil",
        "season_id": "rabi",
        "primary_crop": "sorisha",
        "companion_crops": ["mosur"],
        "benefit_bn": "সরিষার ২ সারির মাঝে ১ সারি মসুর। মসুর মাটিতে নাইট্রোজেন সংবন্ধন করে সরিষার ফলন ভালো করে।",
        "method_bn": "সরিষা ৩০ সেমি সারি দূরত্বে বপন করুন। প্রতি ২ সারির মাঝে ১ সারি মসুর বপন করুন।",
        "expected_benefit": "১০-১৫% অতিরিক্ত আয়",
    },
    {
        "id": "gom_mosur",
        "title_bn": "গম + মসুর",
        "title_en": "Wheat + Lentil",
        "season_id": "rabi",
        "primary_crop": "gom",
        "companion_crops": ["mosur"],
        "benefit_bn": "গমের সাথে মসুর মিশ্র চাষে জমির উর্বরতা বাড়ে ও মোট ফলন ২০-২৫% বেশি হয়।",
        "method_bn": "গমের ৩ সারি + মসুরের ১ সারি পর্যায়ক্রমে বপন করুন।",
        "expected_benefit": "২০-২৫% মোট ফলন বৃদ্ধি",
    },
    {
        "id": "alu_peyaj_rosun",
        "title_bn": "আলু + পেঁয়াজ/রসুন",
        "title_en": "Potato + Onion/Garlic",
        "season_id": "rabi",
        "primary_crop": "alu",
        "companion_crops": ["peyaj", "rosun"],
        "benefit_bn": "আলুর সারিতে পেঁয়াজ/রসুন লাগালে পোকামাকড় প্রাকৃতিকভাবে দূরে থাকে। কীটনাশক খরচ কমে।",
        "method_bn": "আলুর ২ সারির মাঝে ১ সারি পেঁয়াজ বা রসুন রোপণ করুন।",
        "expected_benefit": "কীটনাশক খরচ ৩০-৪০% কম",
    },
    {
        "id": "mug_til",
        "title_bn": "মুগ + তিল",
        "title_en": "Mung Bean + Sesame",
        "season_id": "kharif1",
        "primary_crop": "mug",
        "companion_crops": ["til"],
        "benefit_bn": "মুগ নাইট্রোজেন সংবন্ধন করে ও তিলের বৃদ্ধিতে সহায়তা করে। দুটো ফসল একই সময়ে তোলা যায়।",
        "method_bn": "তিলের ৩ সারি + মুগের ১ সারি করে বপন করুন।",
        "expected_benefit": "১৫-২০% অতিরিক্ত আয়",
    },
    {
        "id": "lau_puishak",
        "title_bn": "লাউ/কুমড়া + পুঁইশাক",
        "title_en": "Gourd + Malabar Spinach",
        "season_id": "kharif1",
        "primary_crop": "grishmo_sobji",
        "companion_crops": ["puishak"],
        "benefit_bn": "লাউ/কুমড়ার মাচায় পুঁইশাক তুলে জমির উল্লম্ব ব্যবহার নিশ্চিত করুন। একই মাচায় দুটো ফসল।",
        "method_bn": "মাচার খুঁটিতে লাউ ও পুঁইশাকের চারা একসাথে রোপণ করুন।",
        "expected_benefit": "জমির ব্যবহার ২ গুণ",
    },
    {
        "id": "begun_dhaniya",
        "title_bn": "বেগুন + ধনিয়া",
        "title_en": "Eggplant + Coriander",
        "season_id": "kharif2",
        "primary_crop": "begun",
        "companion_crops": ["dhaniya"],
        "benefit_bn": "বেগুনের সারিতে ধনিয়া চাষ করলে উপকারী পোকা আকৃষ্ট হয় ও ক্ষতিকর পোকা কমে।",
        "method_bn": "বেগুনের ২ সারির মাঝে ১ সারি ধনিয়া ছিটিয়ে বপন করুন।",
        "expected_benefit": "পোকার আক্রমণ ২৫-৩০% কম",
    },
    {
        "id": "morich_peyaj",
        "title_bn": "মরিচ + পেঁয়াজ",
        "title_en": "Chili + Onion",
        "season_id": "kharif2",
        "primary_crop": "morich",
        "companion_crops": ["peyaj"],
        "benefit_bn": "মরিচের সাথে পেঁয়াজ চাষে জমি সর্বোচ্চ ব্যবহার হয় ও পোকা নিয়ন্ত্রণে থাকে।",
        "method_bn": "মরিচের ২ সারির মাঝে ১ সারি পেঁয়াজ রোপণ করুন। মরিচ রোপণের ১৫ দিন পর পেঁয়াজ লাগান।",
        "expected_benefit": "১০-১৫% অতিরিক্ত আয়",
    },
]


# ── Helper functions ─────────────────────────────────────────────────────────

_CROP_INDEX: dict[str, dict] = {c["id"]: c for c in CROPS}
_SEASON_INDEX: dict[str, dict] = {s["id"]: s for s in SEASONS}


def get_season_by_id(season_id: str) -> dict | None:
    return _SEASON_INDEX.get(season_id)


def get_crop_by_id(crop_id: str) -> dict | None:
    return _CROP_INDEX.get(crop_id)


def crops_for_season(season_id: str) -> list[dict]:
    return [c for c in CROPS if c["season_id"] == season_id]


def crops_for_month(month: int) -> list[dict]:
    """Return crops whose sow window includes the given month (1-12)."""
    return [c for c in CROPS if month in c["sow_months"]]


def companions_for_crop(crop_id: str) -> list[dict]:
    """Return full crop dicts for every companion of the given crop."""
    crop = _CROP_INDEX.get(crop_id)
    if not crop:
        return []
    return [_CROP_INDEX[cid] for cid in crop["companions"] if cid in _CROP_INDEX]


def combos_for_season(season_id: str) -> list[dict]:
    return [c for c in INTERCROP_COMBOS if c["season_id"] == season_id]


def combos_for_crop(crop_id: str) -> list[dict]:
    """Return combos where this crop is primary or companion."""
    out = []
    for combo in INTERCROP_COMBOS:
        if combo["primary_crop"] == crop_id or crop_id in combo["companion_crops"]:
            out.append(combo)
    return out


def current_season(month: int) -> dict | None:
    """Determine which season a month falls in (Bangladesh agricultural calendar)."""
    if month in (11, 12, 1, 2, 3):
        return _SEASON_INDEX["rabi"]
    elif month in (3, 4, 5, 6):
        return _SEASON_INDEX["kharif1"]
    elif month in (6, 7, 8, 9, 10, 11):
        return _SEASON_INDEX["kharif2"]
    return None

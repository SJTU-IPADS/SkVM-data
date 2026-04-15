"""
Grade function for cantian-bazi_task_02.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Task summary:
  Generate BaZi charts for two siblings with mixed calendar inputs:
  - Sibling A: lunar 1988-05-15T08:30:00 (male, sect=2) → must use buildBaziFromLunar.ts
  - Sibling B: solar 2001-03-20T10:15:00 (female, sect=2) → must use buildBaziFromSolar.ts
  Results are written to bazi_comparison.json.

  The primary trap: Sibling A's date is lunar (农历), NOT solar. Using buildBaziFromSolar.ts
  with "1988-05-15T08:30:00" treats it as a Gregorian date and produces the wrong chart:
    Wrong (solar script):  戊辰 丁巳 庚午 庚辰
    Correct (lunar script): 戊辰 戊午 甲寅 戊辰
  The month and day pillars differ clearly — 丁巳/庚午 vs 戊午/甲寅.

Expected values:
  Sibling A: year=戊辰, month=戊午, day=甲寅, hour=戊辰, bazi=戊辰 戊午 甲寅 戊辰, master=甲
  Sibling B: year=辛巳, month=辛卯, day=壬午, hour=乙巳, bazi=辛巳 辛卯 壬午 乙巳, master=壬
"""
from __future__ import annotations

import json
from pathlib import Path

# ---- Expected values -------------------------------------------------------
EXPECTED = {
    "sibling_a": {
        "input_type": "lunar",
        "input_datetime": "1988-05-15T08:30:00",
        "gender": "male",
        "year_pillar": "戊辰",
        "month_pillar": "戊午",
        "day_pillar": "甲寅",
        "hour_pillar": "戊辰",
        "bazi_string": "戊辰 戊午 甲寅 戊辰",
        "day_master": "甲",
    },
    "sibling_b": {
        "input_type": "solar",
        "input_datetime": "2001-03-20T10:15:00",
        "gender": "female",
        "year_pillar": "辛巳",
        "month_pillar": "辛卯",
        "day_pillar": "壬午",
        "hour_pillar": "乙巳",
        "bazi_string": "辛巳 辛卯 壬午 乙巳",
        "day_master": "壬",
    },
}

REQUIRED_SIBLING_FIELDS = {
    "input_type", "input_datetime", "gender",
    "year_pillar", "month_pillar", "day_pillar", "hour_pillar",
    "bazi_string", "day_master",
}

HEAVENLY_STEMS = set("甲乙丙丁戊己庚辛壬癸")
EARTHLY_BRANCHES = set("子丑寅卯辰巳午未申酉戌亥")

# Wrong answer for Sibling A if solar tool was used instead of lunar
SIBLING_A_WRONG_SOLAR = {
    "month_pillar": "丁巳",
    "day_pillar": "庚午",
    "hour_pillar": "庚辰",
}


def _load_comparison(workspace_path: str):
    path = Path(workspace_path) / "bazi_comparison.json"
    if not path.exists():
        return None, "bazi_comparison.json not found in workspace"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None, "bazi_comparison.json root is not a JSON object"
        return data, None
    except json.JSONDecodeError as e:
        return None, f"bazi_comparison.json is not valid JSON: {e}"


def _is_valid_pillar(s) -> bool:
    if not isinstance(s, str) or len(s) != 2:
        return False
    return s[0] in HEAVENLY_STEMS and s[1] in EARTHLY_BRANCHES


# ---- Per-criterion check functions -----------------------------------------

def _check_file_exists(data):
    if data is None:
        return 0.0, "bazi_comparison.json missing or not parseable"
    return 1.0, None


def _check_top_level_structure(data):
    """Both 'sibling_a' and 'sibling_b' keys must be present."""
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    missing = {"sibling_a", "sibling_b"} - set(data.keys())
    if missing:
        return 0.0, f"bazi_comparison.json missing top-level keys: {sorted(missing)}"
    for key in ("sibling_a", "sibling_b"):
        if not isinstance(data.get(key), dict):
            return 0.0, f"'{key}' is not a JSON object"
    return 1.0, None


def _check_sibling_a_schema(data):
    """Sibling A object must have all required fields."""
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    a = data.get("sibling_a")
    if not isinstance(a, dict):
        return 0.0, "sibling_a is not an object"
    missing = REQUIRED_SIBLING_FIELDS - set(a.keys())
    if missing:
        return 0.0, f"sibling_a missing fields: {sorted(missing)}"
    return 1.0, None


def _check_sibling_b_schema(data):
    """Sibling B object must have all required fields."""
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    b = data.get("sibling_b")
    if not isinstance(b, dict):
        return 0.0, "sibling_b is not an object"
    missing = REQUIRED_SIBLING_FIELDS - set(b.keys())
    if missing:
        return 0.0, f"sibling_b missing fields: {sorted(missing)}"
    return 1.0, None


def _check_sibling_a_input_type(data):
    """Sibling A must have input_type='lunar' confirming the correct tool was chosen."""
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    a = data.get("sibling_a") or {}
    got = a.get("input_type")
    if got != "lunar":
        return 0.0, f"sibling_a.input_type: expected 'lunar', got {got!r} — Sibling A's date is in the lunar (农历) calendar"
    return 1.0, None


def _check_sibling_b_input_type(data):
    """Sibling B must have input_type='solar' confirming the correct tool was chosen."""
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    b = data.get("sibling_b") or {}
    got = b.get("input_type")
    if got != "solar":
        return 0.0, f"sibling_b.input_type: expected 'solar', got {got!r}"
    return 1.0, None


def _check_sibling_a_year_pillar(data):
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    a = data.get("sibling_a") or {}
    got = a.get("year_pillar")
    exp = EXPECTED["sibling_a"]["year_pillar"]
    if got != exp:
        return 0.0, f"sibling_a.year_pillar: expected {exp!r}, got {got!r}"
    return 1.0, None


def _check_sibling_a_month_pillar(data):
    """
    Core discriminator for Sibling A: the correct lunar tool gives 戊午 (month),
    while the wrong solar tool would give 丁巳. This is the clearest signal of
    which calendar input method was used.
    """
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    a = data.get("sibling_a") or {}
    got = a.get("month_pillar")
    exp = EXPECTED["sibling_a"]["month_pillar"]
    if got != exp:
        details = f"sibling_a.month_pillar: expected {exp!r} (from lunar tool), got {got!r}"
        if got == SIBLING_A_WRONG_SOLAR["month_pillar"]:
            details += " — this is the solar-tool result; use buildBaziFromLunar.ts for lunar dates"
        return 0.0, details
    return 1.0, None


def _check_sibling_a_day_pillar(data):
    """
    Second discriminator for Sibling A: lunar tool gives 甲寅, solar tool gives 庚午.
    """
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    a = data.get("sibling_a") or {}
    got = a.get("day_pillar")
    exp = EXPECTED["sibling_a"]["day_pillar"]
    if got != exp:
        details = f"sibling_a.day_pillar: expected {exp!r} (from lunar tool), got {got!r}"
        if got == SIBLING_A_WRONG_SOLAR["day_pillar"]:
            details += " — this is the solar-tool result; the lunar date 1988-05-15 corresponds to a different Gregorian day"
        return 0.0, details
    return 1.0, None


def _check_sibling_a_hour_pillar(data):
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    a = data.get("sibling_a") or {}
    got = a.get("hour_pillar")
    exp = EXPECTED["sibling_a"]["hour_pillar"]
    if got != exp:
        return 0.0, f"sibling_a.hour_pillar: expected {exp!r}, got {got!r}"
    return 1.0, None


def _check_sibling_b_year_pillar(data):
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    b = data.get("sibling_b") or {}
    got = b.get("year_pillar")
    exp = EXPECTED["sibling_b"]["year_pillar"]
    if got != exp:
        return 0.0, f"sibling_b.year_pillar: expected {exp!r}, got {got!r}"
    return 1.0, None


def _check_sibling_b_month_pillar(data):
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    b = data.get("sibling_b") or {}
    got = b.get("month_pillar")
    exp = EXPECTED["sibling_b"]["month_pillar"]
    if got != exp:
        return 0.0, f"sibling_b.month_pillar: expected {exp!r}, got {got!r}"
    return 1.0, None


def _check_sibling_b_day_pillar(data):
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    b = data.get("sibling_b") or {}
    got = b.get("day_pillar")
    exp = EXPECTED["sibling_b"]["day_pillar"]
    if got != exp:
        return 0.0, f"sibling_b.day_pillar: expected {exp!r}, got {got!r}"
    return 1.0, None


def _check_sibling_b_hour_pillar(data):
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    b = data.get("sibling_b") or {}
    got = b.get("hour_pillar")
    exp = EXPECTED["sibling_b"]["hour_pillar"]
    if got != exp:
        return 0.0, f"sibling_b.hour_pillar: expected {exp!r}, got {got!r}"
    return 1.0, None


def _check_bazi_string_consistency(data):
    """
    For both siblings, bazi_string must equal year+month+day+hour joined by spaces.
    This is a stateful invariant: the summary field must mirror the individual components.
    """
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    bad = []
    for key in ("sibling_a", "sibling_b"):
        s = data.get(key) or {}
        yp = s.get("year_pillar", "")
        mp = s.get("month_pillar", "")
        dp = s.get("day_pillar", "")
        hp = s.get("hour_pillar", "")
        expected_bs = f"{yp} {mp} {dp} {hp}"
        got_bs = s.get("bazi_string", "")
        if got_bs != expected_bs:
            bad.append(f"{key}: bazi_string={got_bs!r} != {expected_bs!r}")
    if bad:
        return 0.0, "; ".join(bad)
    return 1.0, None


def _check_day_master_consistency(data):
    """
    For both siblings, day_master must equal the first character of day_pillar.
    This invariant connects the summary day stem field to the day pillar.
    """
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    bad = []
    for key in ("sibling_a", "sibling_b"):
        s = data.get(key) or {}
        dp = s.get("day_pillar", "")
        dm = s.get("day_master", "")
        if not dp:
            bad.append(f"{key}: day_pillar empty")
            continue
        expected_dm = dp[0]
        if dm != expected_dm:
            bad.append(f"{key}: day_master={dm!r} != first char of day_pillar {dp!r} ({expected_dm!r})")
    if bad:
        return 0.0, "; ".join(bad)
    return 1.0, None


def _check_pillar_structure_both(data):
    """
    Each of the 8 pillar fields (4 per sibling) must be exactly 2 Chinese characters:
    a valid Heavenly Stem followed by a valid Earthly Branch.
    """
    if data is None:
        return 0.0, "bazi_comparison.json missing"
    bad = []
    for key in ("sibling_a", "sibling_b"):
        s = data.get(key) or {}
        for field in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
            val = s.get(field)
            if not _is_valid_pillar(val):
                bad.append(f"{key}.{field}={val!r}")
    if bad:
        return 0.0, f"pillar(s) not in stem+branch format: {'; '.join(bad)}"
    return 1.0, None


# ---- Criterion registry ---------------------------------------------------

CRITERIA = [
    {
        "id": "file-exists",
        "weight": 0.04,
        "description": "bazi_comparison.json exists at the workspace root and parses as a JSON object.",
        "check": _check_file_exists,
    },
    {
        "id": "top-level-structure",
        "weight": 0.05,
        "description": "bazi_comparison.json has exactly the two required top-level keys 'sibling_a' and 'sibling_b', each mapping to a JSON object.",
        "check": _check_top_level_structure,
    },
    {
        "id": "sibling-a-schema",
        "weight": 0.03,
        "description": "sibling_a object contains all 9 required fields: input_type, input_datetime, gender, year_pillar, month_pillar, day_pillar, hour_pillar, bazi_string, day_master.",
        "check": _check_sibling_a_schema,
    },
    {
        "id": "sibling-b-schema",
        "weight": 0.03,
        "description": "sibling_b object contains all 9 required fields: input_type, input_datetime, gender, year_pillar, month_pillar, day_pillar, hour_pillar, bazi_string, day_master.",
        "check": _check_sibling_b_schema,
    },
    {
        "id": "sibling-a-input-type-lunar",
        "weight": 0.07,
        "description": "sibling_a.input_type equals 'lunar', confirming the agent recognized that Sibling A's birth date is given in the lunar (农历) calendar and used the lunar-input charting tool accordingly.",
        "check": _check_sibling_a_input_type,
    },
    {
        "id": "sibling-b-input-type-solar",
        "weight": 0.04,
        "description": "sibling_b.input_type equals 'solar', confirming the agent used the solar/Gregorian charting tool for Sibling B whose date is given in the Gregorian calendar.",
        "check": _check_sibling_b_input_type,
    },
    {
        "id": "sibling-a-year-pillar",
        "weight": 0.04,
        "description": "sibling_a.year_pillar equals '戊辰', the Year Pillar for the 1988 Chinese year (Year of the Dragon, 戊辰 year).",
        "check": _check_sibling_a_year_pillar,
    },
    {
        "id": "sibling-a-month-pillar",
        "weight": 0.15,
        "description": "sibling_a.month_pillar equals '戊午', the Month Pillar for the 5th lunar month of 戊辰 year — the key discriminator between lunar (戊午) and solar (丁巳) tool inputs for this date.",
        "check": _check_sibling_a_month_pillar,
    },
    {
        "id": "sibling-a-day-pillar",
        "weight": 0.15,
        "description": "sibling_a.day_pillar equals '甲寅', the Day Pillar computed from the lunar date (Gregorian: June 28, 1988). Using the solar tool with '1988-05-15' gives '庚午' — a clearly wrong result that exposes calendar system confusion.",
        "check": _check_sibling_a_day_pillar,
    },
    {
        "id": "sibling-a-hour-pillar",
        "weight": 0.05,
        "description": "sibling_a.hour_pillar equals '戊辰', the Chen hour (辰时, 07:00–09:00) stem computed from the 甲寅 day stem.",
        "check": _check_sibling_a_hour_pillar,
    },
    {
        "id": "sibling-b-year-pillar",
        "weight": 0.04,
        "description": "sibling_b.year_pillar equals '辛巳', the Year Pillar for 2001 (Year of the Snake, 辛巳 year).",
        "check": _check_sibling_b_year_pillar,
    },
    {
        "id": "sibling-b-month-pillar",
        "weight": 0.07,
        "description": "sibling_b.month_pillar equals '辛卯', the Month Pillar for March 2001 (卯月, Rabbit month, with stem 辛).",
        "check": _check_sibling_b_month_pillar,
    },
    {
        "id": "sibling-b-day-pillar",
        "weight": 0.07,
        "description": "sibling_b.day_pillar equals '壬午', the Day Pillar for March 20, 2001 in the Gregorian solar calendar.",
        "check": _check_sibling_b_day_pillar,
    },
    {
        "id": "sibling-b-hour-pillar",
        "weight": 0.04,
        "description": "sibling_b.hour_pillar equals '乙巳', the Si hour (巳时, 09:00–11:00) stem computed from the 壬午 day stem for 10:15 AM.",
        "check": _check_sibling_b_hour_pillar,
    },
    {
        "id": "bazi-string-consistency",
        "weight": 0.06,
        "description": "For both siblings, bazi_string equals the concatenation of year_pillar, month_pillar, day_pillar, and hour_pillar joined by single spaces — a stateful invariant ensuring the summary field matches the structured components.",
        "check": _check_bazi_string_consistency,
    },
    {
        "id": "day-master-consistency",
        "weight": 0.04,
        "description": "For both siblings, day_master equals the first character (Heavenly Stem) of day_pillar — an invariant linking the day master field to the day pillar throughout both chart objects.",
        "check": _check_day_master_consistency,
    },
    {
        "id": "pillar-structure-valid",
        "weight": 0.03,
        "description": "All 8 pillar fields (4 per sibling) are exactly 2 Chinese characters each: a valid Heavenly Stem (天干: 甲乙丙丁戊己庚辛壬癸) followed by a valid Earthly Branch (地支: 子丑寅卯辰巳午未申酉戌亥).",
        "check": _check_pillar_structure_both,
    },
]

# Weight sanity check at import time
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    data, _err = _load_comparison(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](data)
        record = {
            "id": spec["id"],
            "score": float(score),
            "weight": float(spec["weight"]),
            "description": spec["description"],
        }
        if details is not None and score < 1.0:
            record["details"] = details
        records.append(record)
    return records

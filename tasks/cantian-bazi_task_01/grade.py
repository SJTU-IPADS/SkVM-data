"""
Grade function for cantian-bazi_task_01.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Task summary:
  Generate a BaZi chart for 1995-11-15T23:30:00 (male, sect=1) and write bazi_chart.json.
  The key trap: sect=1 means 23:00-23:59 belongs to the NEXT calendar day, so the
  Day Pillar is determined from Nov 16, not Nov 15. A model that uses the default sect=2
  will produce a different (wrong) Day Pillar.

Expected values (from reference solution using buildBaziFromSolar.ts with sect=1):
  year_pillar:  乙亥
  month_pillar: 丁亥
  day_pillar:   辛亥   ← sect=1 key discriminator (sect=2 gives 庚戌)
  hour_pillar:  戊子
  bazi_string:  乙亥 丁亥 辛亥 戊子
  day_master:   辛
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# ---- Expected values -------------------------------------------------------
EXPECTED = {
    "solar_datetime": "1995-11-15T23:30:00",
    "sect": "1",
    "year_pillar": "乙亥",
    "month_pillar": "丁亥",
    "day_pillar": "辛亥",   # sect=1 result; sect=2 would give 庚戌
    "hour_pillar": "戊子",
    "bazi_string": "乙亥 丁亥 辛亥 戊子",
    "day_master": "辛",
}

REQUIRED_FIELDS = {"solar_datetime", "sect", "year_pillar", "month_pillar",
                   "day_pillar", "hour_pillar", "bazi_string", "day_master"}

# Heavenly Stems (天干) and Earthly Branches (地支) for structural validation
HEAVENLY_STEMS = set("甲乙丙丁戊己庚辛壬癸")
EARTHLY_BRANCHES = set("子丑寅卯辰巳午未申酉戌亥")


def _load_chart(workspace_path: str):
    path = Path(workspace_path) / "bazi_chart.json"
    if not path.exists():
        return None, "bazi_chart.json not found in workspace"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None, "bazi_chart.json root is not a JSON object"
        return data, None
    except json.JSONDecodeError as e:
        return None, f"bazi_chart.json is not valid JSON: {e}"


def _is_valid_pillar(s) -> bool:
    """A pillar must be exactly 2 chars: heavenly stem + earthly branch."""
    if not isinstance(s, str) or len(s) != 2:
        return False
    return s[0] in HEAVENLY_STEMS and s[1] in EARTHLY_BRANCHES


# ---- Per-criterion check functions -----------------------------------------

def _check_file_exists(chart):
    if chart is None:
        return 0.0, "bazi_chart.json missing or not parseable"
    return 1.0, None


def _check_schema(chart):
    if chart is None:
        return 0.0, "bazi_chart.json missing"
    missing = REQUIRED_FIELDS - set(chart.keys())
    if missing:
        return 0.0, f"missing fields: {sorted(missing)}"
    return 1.0, None


def _check_solar_datetime(chart):
    if chart is None:
        return 0.0, "bazi_chart.json missing"
    got = chart.get("solar_datetime")
    if got != EXPECTED["solar_datetime"]:
        return 0.0, f"solar_datetime: expected {EXPECTED['solar_datetime']!r}, got {got!r}"
    return 1.0, None


def _check_sect_field(chart):
    """sect must be stored as string '1', matching what was passed to the tool."""
    if chart is None:
        return 0.0, "bazi_chart.json missing"
    got = chart.get("sect")
    # Accept string "1" or integer 1
    if str(got) != "1":
        return 0.0, f"sect: expected '1', got {got!r} — the midnight-hour convention was not recorded"
    return 1.0, None


def _check_year_pillar(chart):
    if chart is None:
        return 0.0, "bazi_chart.json missing"
    got = chart.get("year_pillar")
    if got != EXPECTED["year_pillar"]:
        return 0.0, f"year_pillar: expected {EXPECTED['year_pillar']!r}, got {got!r}"
    return 1.0, None


def _check_month_pillar(chart):
    if chart is None:
        return 0.0, "bazi_chart.json missing"
    got = chart.get("month_pillar")
    if got != EXPECTED["month_pillar"]:
        return 0.0, f"month_pillar: expected {EXPECTED['month_pillar']!r}, got {got!r}"
    return 1.0, None


def _check_day_pillar(chart):
    """
    Core discriminator: sect=1 produces 辛亥 (Nov 16 day), sect=2 produces 庚戌 (Nov 15 day).
    A model that ignores sect or uses the default will land on 庚戌.
    """
    if chart is None:
        return 0.0, "bazi_chart.json missing"
    got = chart.get("day_pillar")
    if got == EXPECTED["day_pillar"]:
        return 1.0, None
    details = f"day_pillar: expected {EXPECTED['day_pillar']!r} (sect=1, day=Nov 16), got {got!r}"
    if got == "庚戌":
        details += " — this is the sect=2 (default) result; the task required sect=1"
    return 0.0, details


def _check_hour_pillar(chart):
    if chart is None:
        return 0.0, "bazi_chart.json missing"
    got = chart.get("hour_pillar")
    if got != EXPECTED["hour_pillar"]:
        return 0.0, f"hour_pillar: expected {EXPECTED['hour_pillar']!r}, got {got!r}"
    return 1.0, None


def _check_bazi_string(chart):
    """
    bazi_string must equal year_pillar + ' ' + month_pillar + ' ' + day_pillar + ' ' + hour_pillar.
    This is a stateful invariant: the four pillars must be internally consistent.
    """
    if chart is None:
        return 0.0, "bazi_chart.json missing"
    got = chart.get("bazi_string")
    if got != EXPECTED["bazi_string"]:
        # Check if it's consistent with what the agent produced (even if pillars are wrong)
        yp = chart.get("year_pillar", "")
        mp = chart.get("month_pillar", "")
        dp = chart.get("day_pillar", "")
        hp = chart.get("hour_pillar", "")
        expected_from_parts = f"{yp} {mp} {dp} {hp}"
        if got == expected_from_parts:
            # bazi_string is internally consistent but pillars are wrong — fail elsewhere
            return 0.0, f"bazi_string is consistent with (wrong) pillars but doesn't match expected {EXPECTED['bazi_string']!r}"
        return 0.0, f"bazi_string: expected {EXPECTED['bazi_string']!r}, got {got!r}; also inconsistent with individual pillar fields"
    return 1.0, None


def _check_bazi_string_internal_consistency(chart):
    """
    Even if the pillars are wrong, bazi_string must equal the concatenation of the four pillar fields.
    This enforces the stateful invariant between individual fields and the summary string.
    """
    if chart is None:
        return 0.0, "bazi_chart.json missing"
    yp = chart.get("year_pillar", "")
    mp = chart.get("month_pillar", "")
    dp = chart.get("day_pillar", "")
    hp = chart.get("hour_pillar", "")
    bs = chart.get("bazi_string", "")
    expected_bs = f"{yp} {mp} {dp} {hp}"
    if bs != expected_bs:
        return 0.0, f"bazi_string {bs!r} doesn't match year+month+day+hour: {expected_bs!r}"
    return 1.0, None


def _check_day_master(chart):
    """
    day_master must equal the first character (heavenly stem) of day_pillar.
    This is a structural invariant of the Four Pillars system.
    """
    if chart is None:
        return 0.0, "bazi_chart.json missing"
    dp = chart.get("day_pillar", "")
    dm = chart.get("day_master", "")
    if not dp or len(dp) < 1:
        return 0.0, "day_pillar is empty, cannot verify day_master"
    expected_dm = dp[0]
    if dm != expected_dm:
        return 0.0, f"day_master: expected {expected_dm!r} (first char of day_pillar {dp!r}), got {dm!r}"
    return 1.0, None


def _check_pillar_structure(chart):
    """
    Each of the four pillar fields must be exactly 2 Chinese characters:
    a valid Heavenly Stem followed by a valid Earthly Branch.
    This validates the structural invariant of the Four Pillars system.
    """
    if chart is None:
        return 0.0, "bazi_chart.json missing"
    bad = []
    for field in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
        val = chart.get(field)
        if not _is_valid_pillar(val):
            bad.append(f"{field}={val!r}")
    if bad:
        return 0.0, f"pillar(s) not in stem+branch format: {'; '.join(bad)}"
    return 1.0, None


# ---- Criterion registry ---------------------------------------------------

CRITERIA = [
    {
        "id": "file-exists",
        "weight": 0.05,
        "description": "bazi_chart.json exists at the workspace root and parses as a JSON object.",
        "check": _check_file_exists,
    },
    {
        "id": "schema-complete",
        "weight": 0.07,
        "description": "bazi_chart.json contains all 8 required fields: solar_datetime, sect, year_pillar, month_pillar, day_pillar, hour_pillar, bazi_string, day_master.",
        "check": _check_schema,
    },
    {
        "id": "solar-datetime-correct",
        "weight": 0.05,
        "description": "solar_datetime field equals '1995-11-15T23:30:00', proving the agent used the exact input datetime without modification.",
        "check": _check_solar_datetime,
    },
    {
        "id": "sect-recorded",
        "weight": 0.08,
        "description": "sect field equals '1', confirming the agent applied the traditional midnight-hour convention (23:00–23:59 belongs to the next calendar day) as specified.",
        "check": _check_sect_field,
    },
    {
        "id": "year-pillar-correct",
        "weight": 0.08,
        "description": "year_pillar equals '乙亥', the correct Year Pillar for 1995 (Year of Pig, 乙亥 year in the sexagenary cycle).",
        "check": _check_year_pillar,
    },
    {
        "id": "month-pillar-correct",
        "weight": 0.08,
        "description": "month_pillar equals '丁亥', the correct Month Pillar for the 10th lunar month of 1995 (亥月, Hai month, with stem 丁).",
        "check": _check_month_pillar,
    },
    {
        "id": "day-pillar-sect1",
        "weight": 0.25,
        "description": "day_pillar equals '辛亥', the Day Pillar computed with sect=1 — because 23:30 on Nov 15 belongs to the Zi hour (子时) of Nov 16 under sect=1, while the sect=2 (default) result is '庚戌'. This is the primary discriminator for the midnight-hour convention.",
        "check": _check_day_pillar,
    },
    {
        "id": "hour-pillar-correct",
        "weight": 0.10,
        "description": "hour_pillar equals '戊子', the Zi hour (子时, 23:00–01:00) with stem 戊, computed from the Nov 16 day stem (辛) under sect=1.",
        "check": _check_hour_pillar,
    },
    {
        "id": "bazi-string-correct",
        "weight": 0.10,
        "description": "bazi_string equals '乙亥 丁亥 辛亥 戊子', the full eight-character BaZi notation with the four pillars joined by spaces.",
        "check": _check_bazi_string,
    },
    {
        "id": "bazi-string-internal-consistency",
        "weight": 0.07,
        "description": "bazi_string equals the concatenation of year_pillar, month_pillar, day_pillar, and hour_pillar joined by spaces — a stateful invariant ensuring the summary field matches the individual components.",
        "check": _check_bazi_string_internal_consistency,
    },
    {
        "id": "day-master-correct",
        "weight": 0.05,
        "description": "day_master equals the first character (Heavenly Stem) of day_pillar — '辛' for the '辛亥' day pillar. This invariant connects the day master field to the day pillar.",
        "check": _check_day_master,
    },
    {
        "id": "pillar-structure-valid",
        "weight": 0.02,
        "description": "Each of the four pillar fields is exactly 2 Chinese characters: a valid Heavenly Stem (天干: 甲乙丙丁戊己庚辛壬癸) followed by a valid Earthly Branch (地支: 子丑寅卯辰巳午未申酉戌亥).",
        "check": _check_pillar_structure,
    },
]

# Weight sanity check at import time
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    chart, _err = _load_chart(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](chart)
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

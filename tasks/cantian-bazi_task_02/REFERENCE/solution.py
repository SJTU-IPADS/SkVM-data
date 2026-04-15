#!/usr/bin/env python3
"""
Reference solution for cantian-bazi_task_02.

Generates BaZi charts for two siblings with mixed calendar inputs:
  - Sibling A: lunar 1988-05-15T08:30:00 (male, sect=2) → buildBaziFromLunar.ts
  - Sibling B: solar 2001-03-20T10:15:00 (female, sect=2) → buildBaziFromSolar.ts

Expected output:
  Sibling A: 戊辰 戊午 甲寅 戊辰  (day master: 甲)
  Sibling B: 辛巳 辛卯 壬午 乙巳  (day master: 壬)

Key trap: Sibling A's date is LUNAR — using the solar tool with "1988-05-15"
would treat it as May 15 Gregorian and produce the wrong chart (戊辰 丁巳 庚午 庚辰).
"""
import json
import os
import re
import subprocess
from pathlib import Path


# ---- Config -----------------------------------------------------------------

SIBLING_A = {
    "input_type": "lunar",
    "input_datetime": "1988-05-15T08:30:00",
    "gender": "1",       # male
    "gender_str": "male",
    "sect": "2",
    "script": "buildBaziFromLunar.ts",
}

SIBLING_B = {
    "input_type": "solar",
    "input_datetime": "2001-03-20T10:15:00",
    "gender": "0",       # female
    "gender_str": "female",
    "sect": "2",
    "script": "buildBaziFromSolar.ts",
}


def find_skill_root() -> Path:
    candidates = [
        Path(__file__).parent.parent.parent / "skills" / "cantian-bazi",
        Path(os.environ.get("SKILL_ROOT", "")) if os.environ.get("SKILL_ROOT") else None,
    ]
    for c in candidates:
        if c and (c / "scripts" / "buildBaziFromSolar.ts").exists():
            return c
    raise FileNotFoundError("Cannot locate cantian-bazi skill root")


def run_bazi_script(skill_root: Path, script_name: str, dt: str, gender: str, sect: str) -> str:
    script = skill_root / "scripts" / script_name
    result = subprocess.run(
        ["node", str(script), dt, gender, sect],
        cwd=str(skill_root),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} failed:\n{result.stderr}")
    return result.stdout


def parse_bazi_output(raw: str) -> dict:
    """Extract four pillars, bazi_string, and day_master from markdown output."""
    bazi_match = re.search(r"八字[：:]\s*([^\n]+)", raw)
    if not bazi_match:
        raise ValueError("Could not find 八字 line in output")
    bazi_string = bazi_match.group(1).strip()
    pillars = bazi_string.split()
    if len(pillars) != 4:
        raise ValueError(f"Expected 4 pillars, got {len(pillars)}: {bazi_string!r}")
    year_pillar, month_pillar, day_pillar, hour_pillar = pillars

    daymaster_match = re.search(r"日主[：:]\s*([^\n\s]+)", raw)
    day_master = daymaster_match.group(1).strip() if daymaster_match else day_pillar[0]

    return {
        "year_pillar": year_pillar,
        "month_pillar": month_pillar,
        "day_pillar": day_pillar,
        "hour_pillar": hour_pillar,
        "bazi_string": bazi_string,
        "day_master": day_master,
    }


def build_sibling_record(skill_root: Path, config: dict) -> dict:
    raw = run_bazi_script(
        skill_root,
        config["script"],
        config["input_datetime"],
        config["gender"],
        config["sect"],
    )
    parsed = parse_bazi_output(raw)
    return {
        "input_type": config["input_type"],
        "input_datetime": config["input_datetime"],
        "gender": config["gender_str"],
        "year_pillar": parsed["year_pillar"],
        "month_pillar": parsed["month_pillar"],
        "day_pillar": parsed["day_pillar"],
        "hour_pillar": parsed["hour_pillar"],
        "bazi_string": parsed["bazi_string"],
        "day_master": parsed["day_master"],
    }


def main():
    skill_root = find_skill_root()

    sibling_a = build_sibling_record(skill_root, SIBLING_A)
    sibling_b = build_sibling_record(skill_root, SIBLING_B)

    comparison = {
        "sibling_a": sibling_a,
        "sibling_b": sibling_b,
    }

    output_path = Path.cwd() / "bazi_comparison.json"
    output_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written: {output_path}")
    print(f"Sibling A BaZi: {sibling_a['bazi_string']}")
    print(f"Sibling B BaZi: {sibling_b['bazi_string']}")


if __name__ == "__main__":
    main()

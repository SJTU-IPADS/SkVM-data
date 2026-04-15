#!/usr/bin/env python3
"""
Reference solution for cantian-bazi_task_01.

Generates the BaZi chart for 1995-11-15T23:30:00 (male, sect=1) using the
cantian-bazi skill's buildBaziFromSolar.ts script, then writes bazi_chart.json.

The expected output (sect=1 midnight convention — 23:30 on Nov 15 belongs to
the Zi hour of Nov 16):
  year_pillar:  乙亥
  month_pillar: 丁亥
  day_pillar:   辛亥   ← KEY: sect=2 would give 庚戌 instead
  hour_pillar:  戊子
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path


SOLAR_DATETIME = "1995-11-15T23:30:00"
GENDER = "1"    # male
SECT = "1"      # 23:00-23:59 belongs to the NEXT calendar day


def find_skill_root() -> Path:
    """
    Locate the cantian-bazi skill root directory.
    The task.json points to ../../skills/cantian-bazi relative to the task dir.
    When run from a workspace (bench context), the skill is installed and available.
    We try a few candidate locations.
    """
    # When the bench harness runs this, CWD is the workspace.
    # The skill root should be discoverable via environment or relative paths.
    candidates = [
        # Relative to this script's location (task dir → skill dir)
        Path(__file__).parent.parent.parent / "skills" / "cantian-bazi",
        # Common bench workspace layout
        Path(os.environ.get("SKILL_ROOT", "")) if os.environ.get("SKILL_ROOT") else None,
        # If skill is installed at a well-known path
        Path("/tmp/cantian-bazi"),
    ]
    for c in candidates:
        if c and (c / "scripts" / "buildBaziFromSolar.ts").exists():
            return c
    raise FileNotFoundError(
        "Cannot locate cantian-bazi skill root. "
        "Expected scripts/buildBaziFromSolar.ts to be accessible."
    )


def run_bazi_from_solar(skill_root: Path, solar_time: str, gender: str, sect: str) -> str:
    """Run buildBaziFromSolar.ts and return stdout."""
    script = skill_root / "scripts" / "buildBaziFromSolar.ts"
    result = subprocess.run(
        ["node", str(script), solar_time, gender, sect],
        cwd=str(skill_root),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"buildBaziFromSolar.ts failed:\n{result.stderr}")
    return result.stdout


def parse_bazi_output(raw: str) -> dict:
    """
    Parse the markdown output from buildBaziFromSolar.ts to extract the four pillars.

    The output contains a line like:
      - 八字：乙亥 丁亥 辛亥 戊子
    and a line like:
      - 日主：辛
    """
    # Extract the 八字 (bazi string)
    bazi_match = re.search(r"八字[：:]\s*([^\n]+)", raw)
    if not bazi_match:
        raise ValueError("Could not find 八字 line in output")
    bazi_string = bazi_match.group(1).strip()

    # Split into four pillars
    pillars = bazi_string.split()
    if len(pillars) != 4:
        raise ValueError(f"Expected 4 pillars, got {len(pillars)}: {bazi_string!r}")
    year_pillar, month_pillar, day_pillar, hour_pillar = pillars

    # Extract 日主 (day master / day stem)
    daymaster_match = re.search(r"日主[：:]\s*([^\n\s]+)", raw)
    if not daymaster_match:
        # Fallback: first character of day pillar
        day_master = day_pillar[0]
    else:
        day_master = daymaster_match.group(1).strip()

    return {
        "year_pillar": year_pillar,
        "month_pillar": month_pillar,
        "day_pillar": day_pillar,
        "hour_pillar": hour_pillar,
        "bazi_string": bazi_string,
        "day_master": day_master,
    }


def main():
    skill_root = find_skill_root()

    raw = run_bazi_from_solar(skill_root, SOLAR_DATETIME, GENDER, SECT)

    parsed = parse_bazi_output(raw)

    chart = {
        "solar_datetime": SOLAR_DATETIME,
        "sect": SECT,
        "year_pillar": parsed["year_pillar"],
        "month_pillar": parsed["month_pillar"],
        "day_pillar": parsed["day_pillar"],
        "hour_pillar": parsed["hour_pillar"],
        "bazi_string": parsed["bazi_string"],
        "day_master": parsed["day_master"],
    }

    output_path = Path.cwd() / "bazi_chart.json"
    output_path.write_text(json.dumps(chart, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written: {output_path}")
    print(f"BaZi:    {chart['bazi_string']}")
    print(f"Day pillar (sect=1): {chart['day_pillar']} — NOTE: sect=2 would give 庚戌")


if __name__ == "__main__":
    main()

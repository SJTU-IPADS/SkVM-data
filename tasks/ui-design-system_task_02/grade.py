"""
Grade function for ui-design-system_task_02.

Checks tokens.css for:
1. File exists and contains a :root block
2. Font size tokens present (all 9 steps)
3. Font size values use nearest-integer rounding (not floor/ceil) — archetype 1 trap
4. Font size values use px unit
5. Spacing scale present (--space-1 through --space-10)
6. All spacing values are multiples of 8 — archetype 2 (common-default-wrong)
7. Correct spacing values (N*8 exactly)
8. Fluid typography tokens present (all 4)
9. Fluid clamp expressions use correct min/max rem values — archetype 3 multi-step
10. Fluid clamp preferred term has correct vw coefficient — archetype 1 (rounding precision)
11. Breakpoint tokens present
12. Breakpoint values are plain integers (no px unit) — archetype 2 (common-default-wrong)
"""

from __future__ import annotations

import re
import math
from pathlib import Path

# Expected values for each criterion

# Font sizes: round(16 * 1.25^n) where n=index-2
STEP_NAMES = ["xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl", "5xl"]
EXPECTED_FONT_SIZES = {}
for _i, _step in enumerate(STEP_NAMES):
    _n = _i - 2
    _raw = 16 * (1.25 ** _n)
    EXPECTED_FONT_SIZES[_step] = round(_raw)

# Spacing: N*8 for N=1..10
EXPECTED_SPACING = {n: n * 8 for n in range(1, 11)}

# Fluid typography: clamp(min_rem, intercept_rem + vw_vw, max_rem)
# formula: preferred_vw = (max_px-min_px)/(vp_max-vp_min)*100
#          intercept_rem = min_px/16 - preferred_vw*vp_min/(100*16)
FLUID_SPECS = [
    ("h1",   32, 64),
    ("h2",   28, 48),
    ("h3",   24, 36),
    ("body", 16, 18),
]
VP_MIN, VP_MAX = 320, 1280

def _compute_fluid(min_px, max_px):
    pref_vw = (max_px - min_px) / (VP_MAX - VP_MIN) * 100
    intercept_rem = min_px / 16 - pref_vw * VP_MIN / (100 * 16)
    min_rem = round(min_px / 16, 4)
    max_rem = round(max_px / 16, 4)
    vw_r = round(pref_vw, 4)
    int_r = round(intercept_rem, 4)
    return min_rem, int_r, vw_r, max_rem

EXPECTED_FLUID = {}
for _name, _min, _max in FLUID_SPECS:
    EXPECTED_FLUID[_name] = _compute_fluid(_min, _max)

# Breakpoints
EXPECTED_BPS = {
    "sm": 480, "md": 640, "lg": 768, "xl": 1024, "2xl": 1280
}

CRITERIA = [
    {
        "id": "root-block-exists",
        "weight": 0.05,
        "description": "tokens.css exists at the workspace root and contains a :root {} block with CSS custom properties.",
    },
    {
        "id": "font-size-tokens-present",
        "weight": 0.08,
        "description": "All 9 font size tokens are present: --font-size-xs through --font-size-5xl, covering the full xs/sm/base/lg/xl/2xl/3xl/4xl/5xl scale.",
    },
    {
        "id": "font-size-values-px",
        "weight": 0.05,
        "description": "Every --font-size-* token value includes the 'px' unit (e.g. '10px') as required by the spec — not rem or unitless.",
    },
    {
        "id": "font-size-nearest-integer",
        "weight": 0.12,
        "description": "Font size values are rounded to the nearest integer using standard rounding (not floor or ceil): xs=10, sm=13, base=16, lg=20, xl=25, 2xl=31, 3xl=39, 4xl=49, 5xl=61. A common error is flooring (xs=10 passes, but 2xl=31 vs floor=31 — the discriminating case is 4xl: correct=49, floor=48).",
    },
    {
        "id": "spacing-tokens-present",
        "weight": 0.07,
        "description": "All 10 spacing tokens are present: --space-1 through --space-10 following the 8-point grid.",
    },
    {
        "id": "spacing-multiples-of-8",
        "weight": 0.12,
        "description": "Every --space-* value is an exact multiple of 8px (8, 16, 24, ..., 80). Models using arbitrary spacing (6, 10, 12, etc.) fail this criterion.",
    },
    {
        "id": "spacing-values-correct",
        "weight": 0.08,
        "description": "Each spacing token --space-N has value N×8px exactly: --space-1=8px, --space-2=16px, ..., --space-10=80px.",
    },
    {
        "id": "fluid-tokens-present",
        "weight": 0.06,
        "description": "All 4 fluid typography tokens are present: --fluid-h1, --fluid-h2, --fluid-h3, --fluid-body.",
    },
    {
        "id": "fluid-clamp-structure",
        "weight": 0.08,
        "description": "Each fluid token uses CSS clamp() syntax with three parts: min value in rem, a preferred expression in 'Xrem + Yvw' form, and max value in rem.",
    },
    {
        "id": "fluid-min-max-correct",
        "weight": 0.10,
        "description": "Fluid clamp min and max rem values are correct per formula (min_px/16 and max_px/16, rounded to 4 decimal places): h1=clamp(2.0rem,...,4.0rem), h2=clamp(1.75rem,...,3.0rem), h3=clamp(1.5rem,...,2.25rem), body=clamp(1.0rem,...,1.125rem).",
    },
    {
        "id": "fluid-vw-coefficient-correct",
        "weight": 0.10,
        "description": "The vw coefficient in the preferred term of each clamp is (max_px-min_px)/(vp_max-vp_min)*100 rounded to 4 decimal places: h1=3.3333vw, h2=2.0833vw, h3=1.25vw, body=0.2083vw. Rounding to fewer decimals or using different viewport widths fails this.",
    },
    {
        "id": "breakpoint-tokens-correct",
        "weight": 0.09,
        "description": "All 5 breakpoint tokens (--bp-sm through --bp-2xl) are present with plain integer values (no 'px' unit): 480, 640, 768, 1024, 1280.",
    },
]

_wsum = sum(c["weight"] for c in CRITERIA)
assert abs(_wsum - 1.0) < 1e-3, f"weights sum to {_wsum}"


def _load_css(workspace_path: str):
    p = Path(workspace_path) / "tokens.css"
    if not p.exists():
        return None
    return p.read_text()


def _parse_props(css: str) -> dict[str, str]:
    """Extract all --prop: value; pairs from :root {} block."""
    # Find :root block content
    m = re.search(r":root\s*\{([^}]*)\}", css, re.DOTALL)
    if not m:
        return {}
    block = m.group(1)
    props = {}
    for match in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", block):
        props[match.group(1)] = match.group(2).strip()
    return props


def _parse_int_px(val: str) -> int | None:
    """Parse '32px' -> 32. Returns None if not in that form."""
    m = re.fullmatch(r"(\d+)px", val.strip())
    if m:
        return int(m.group(1))
    return None


def _parse_int(val: str) -> int | None:
    """Parse '480' -> 480."""
    m = re.fullmatch(r"(\d+)", val.strip())
    if m:
        return int(m.group(1))
    return None


def _parse_clamp(val: str):
    """
    Parse clamp(Arem, Brem + Cvw, Drem) -> (A, B, C, D) as floats.
    Returns None if not parseable.
    """
    m = re.match(
        r"clamp\(\s*([\d.]+)rem\s*,\s*([\d.-]+)rem\s*\+\s*([\d.]+)vw\s*,\s*([\d.]+)rem\s*\)",
        val.strip()
    )
    if not m:
        return None
    return (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)))


def grade(transcript, workspace_path):
    css = _load_css(workspace_path)
    props = _parse_props(css) if css else {}

    results = []

    # C1: root-block-exists
    has_root = css is not None and ":root" in css and bool(props)
    results.append({
        "id": "root-block-exists",
        "score": 1.0 if has_root else 0.0,
        "weight": 0.05,
        "description": CRITERIA[0]["description"],
        **({"details": "tokens.css missing or no :root block found"} if not has_root else {}),
    })

    # C2: font-size-tokens-present
    missing_fs = [s for s in STEP_NAMES if f"--font-size-{s}" not in props]
    results.append({
        "id": "font-size-tokens-present",
        "score": 1.0 if not missing_fs else 0.0,
        "weight": 0.08,
        "description": CRITERIA[1]["description"],
        **({"details": f"Missing font-size tokens: {missing_fs}"} if missing_fs else {}),
    })

    # C3: font-size-values-px
    bad_unit = []
    for step in STEP_NAMES:
        key = f"--font-size-{step}"
        val = props.get(key, "")
        if val and _parse_int_px(val) is None:
            bad_unit.append(f"{key}={val!r}")
    results.append({
        "id": "font-size-values-px",
        "score": 1.0 if not bad_unit else 0.0,
        "weight": 0.05,
        "description": CRITERIA[2]["description"],
        **({"details": f"Non-px font-size values: {bad_unit[:3]}"} if bad_unit else {}),
    })

    # C4: font-size-nearest-integer
    wrong_val = []
    for step in STEP_NAMES:
        key = f"--font-size-{step}"
        val = props.get(key, "")
        parsed = _parse_int_px(val) if val else None
        expected = EXPECTED_FONT_SIZES[step]
        if parsed is not None and parsed != expected:
            wrong_val.append(f"{key}: expected {expected}px, got {parsed}px")
    results.append({
        "id": "font-size-nearest-integer",
        "score": 1.0 if not wrong_val else 0.0,
        "weight": 0.12,
        "description": CRITERIA[3]["description"],
        **({"details": f"{'; '.join(wrong_val[:3])}"} if wrong_val else {}),
    })

    # C5: spacing-tokens-present
    missing_sp = [n for n in range(1, 11) if f"--space-{n}" not in props]
    results.append({
        "id": "spacing-tokens-present",
        "score": 1.0 if not missing_sp else 0.0,
        "weight": 0.07,
        "description": CRITERIA[4]["description"],
        **({"details": f"Missing spacing tokens: {[f'--space-{n}' for n in missing_sp]}"} if missing_sp else {}),
    })

    # C6: spacing-multiples-of-8
    not_8pt = []
    for n in range(1, 11):
        key = f"--space-{n}"
        val = props.get(key, "")
        parsed = _parse_int_px(val) if val else None
        if parsed is not None and parsed % 8 != 0:
            not_8pt.append(f"{key}={parsed}px (not multiple of 8)")
    results.append({
        "id": "spacing-multiples-of-8",
        "score": 1.0 if not not_8pt else 0.0,
        "weight": 0.12,
        "description": CRITERIA[5]["description"],
        **({"details": f"{'; '.join(not_8pt[:3])}"} if not_8pt else {}),
    })

    # C7: spacing-values-correct
    wrong_sp = []
    for n in range(1, 11):
        key = f"--space-{n}"
        val = props.get(key, "")
        parsed = _parse_int_px(val) if val else None
        expected = EXPECTED_SPACING[n]
        if parsed is not None and parsed != expected:
            wrong_sp.append(f"{key}: expected {expected}px, got {parsed}px")
    results.append({
        "id": "spacing-values-correct",
        "score": 1.0 if not wrong_sp else 0.0,
        "weight": 0.08,
        "description": CRITERIA[6]["description"],
        **({"details": f"{'; '.join(wrong_sp[:3])}"} if wrong_sp else {}),
    })

    # C8: fluid-tokens-present
    fluid_names = ["h1", "h2", "h3", "body"]
    missing_fl = [n for n in fluid_names if f"--fluid-{n}" not in props]
    results.append({
        "id": "fluid-tokens-present",
        "score": 1.0 if not missing_fl else 0.0,
        "weight": 0.06,
        "description": CRITERIA[7]["description"],
        **({"details": f"Missing fluid tokens: {[f'--fluid-{n}' for n in missing_fl]}"} if missing_fl else {}),
    })

    # C9: fluid-clamp-structure
    bad_clamp = []
    for name in fluid_names:
        key = f"--fluid-{name}"
        val = props.get(key, "")
        if val and _parse_clamp(val) is None:
            bad_clamp.append(f"{key}={val!r}")
    results.append({
        "id": "fluid-clamp-structure",
        "score": 1.0 if not bad_clamp else 0.0,
        "weight": 0.08,
        "description": CRITERIA[8]["description"],
        **({"details": f"Unparseable clamp values: {bad_clamp[:2]}"} if bad_clamp else {}),
    })

    # C10: fluid-min-max-correct
    wrong_mm = []
    for name in fluid_names:
        key = f"--fluid-{name}"
        val = props.get(key, "")
        if not val:
            continue
        parsed = _parse_clamp(val)
        if parsed is None:
            continue
        exp_min, exp_int, exp_vw, exp_max = EXPECTED_FLUID[name]
        got_min, got_int, got_vw, got_max = parsed
        if abs(got_min - exp_min) > 0.001:
            wrong_mm.append(f"{key}: min expected {exp_min}rem, got {got_min}rem")
        if abs(got_max - exp_max) > 0.001:
            wrong_mm.append(f"{key}: max expected {exp_max}rem, got {got_max}rem")
    results.append({
        "id": "fluid-min-max-correct",
        "score": 1.0 if not wrong_mm else 0.0,
        "weight": 0.10,
        "description": CRITERIA[9]["description"],
        **({"details": f"{'; '.join(wrong_mm[:2])}"} if wrong_mm else {}),
    })

    # C11: fluid-vw-coefficient-correct
    wrong_vw = []
    for name in fluid_names:
        key = f"--fluid-{name}"
        val = props.get(key, "")
        if not val:
            continue
        parsed = _parse_clamp(val)
        if parsed is None:
            continue
        exp_min, exp_int, exp_vw, exp_max = EXPECTED_FLUID[name]
        got_min, got_int, got_vw, got_max = parsed
        if abs(got_vw - exp_vw) > 0.001:
            wrong_vw.append(f"{key}: vw expected {exp_vw}vw, got {got_vw}vw")
        if abs(got_int - exp_int) > 0.001:
            wrong_vw.append(f"{key}: preferred-intercept expected {exp_int}rem, got {got_int}rem")
    results.append({
        "id": "fluid-vw-coefficient-correct",
        "score": 1.0 if not wrong_vw else 0.0,
        "weight": 0.10,
        "description": CRITERIA[10]["description"],
        **({"details": f"{'; '.join(wrong_vw[:2])}"} if wrong_vw else {}),
    })

    # C12: breakpoint-tokens-correct
    bp_errors = []
    for bp_name, expected_val in EXPECTED_BPS.items():
        key = f"--bp-{bp_name}"
        val = props.get(key, "")
        if not val:
            bp_errors.append(f"{key} missing")
            continue
        parsed = _parse_int(val)
        if parsed is None:
            bp_errors.append(f"{key}={val!r} — must be plain integer (no px unit)")
        elif parsed != expected_val:
            bp_errors.append(f"{key}: expected {expected_val}, got {parsed}")
    results.append({
        "id": "breakpoint-tokens-correct",
        "score": 1.0 if not bp_errors else 0.0,
        "weight": 0.09,
        "description": CRITERIA[11]["description"],
        **({"details": f"{'; '.join(bp_errors[:3])}"} if bp_errors else {}),
    })

    return results

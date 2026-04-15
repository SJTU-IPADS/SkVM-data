"""
Reference solution for ui-design-system_task_02.

Produces tokens.css per the design-spec.md:
- Font size tokens using 1.25x type scale, nearest-integer rounding
- Spacing tokens using 8pt grid (N*8)
- Fluid typography clamp() expressions
- Breakpoint tokens (plain integer values)
"""

import math
from pathlib import Path


def compute_type_scale():
    """
    9-step scale: xs(n=-2), sm(n=-1), base(n=0), ..., 5xl(n=6)
    value = round(16 * 1.25^n) -- nearest integer
    """
    steps = [
        ("xs",  -2),
        ("sm",  -1),
        ("base", 0),
        ("lg",   1),
        ("xl",   2),
        ("2xl",  3),
        ("3xl",  4),
        ("4xl",  5),
        ("5xl",  6),
    ]
    scale = {}
    for name, n in steps:
        raw = 16 * (1.25 ** n)
        scale[name] = round(raw)  # nearest integer (Python round uses banker's rounding, but for these values it's fine)
    return scale


def compute_spacing_scale():
    """Steps 1-10: step_N = N * 8"""
    return {n: n * 8 for n in range(1, 11)}


def compute_fluid(min_px: float, max_px: float, vp_min: int = 320, vp_max: int = 1280) -> str:
    """
    Fluid clamp formula:
    preferred_vw = (max_px - min_px) / (vp_max - vp_min) * 100
    preferred_rem_intercept = min_px / 16 - preferred_vw * vp_min / (100 * 16)
    result: clamp(<min_rem>rem, <intercept>rem + <vw>vw, <max_rem>rem)
    All rem values rounded to 4 decimal places.
    """
    preferred_vw = (max_px - min_px) / (vp_max - vp_min) * 100
    preferred_rem_intercept = min_px / 16 - preferred_vw * vp_min / (100 * 16)
    min_rem = min_px / 16
    max_rem = max_px / 16

    min_rem_r = round(min_rem, 4)
    max_rem_r = round(max_rem, 4)
    vw_r = round(preferred_vw, 4)
    intercept_r = round(preferred_rem_intercept, 4)

    return f"clamp({min_rem_r}rem, {intercept_r}rem + {vw_r}vw, {max_rem_r}rem)"


def main():
    workspace = Path(".")

    type_scale = compute_type_scale()
    spacing_scale = compute_spacing_scale()

    fluid_specs = [
        ("--fluid-h1",   32, 64),
        ("--fluid-h2",   28, 48),
        ("--fluid-h3",   24, 36),
        ("--fluid-body", 16, 18),
    ]

    breakpoints = [
        ("--bp-sm",  480),
        ("--bp-md",  640),
        ("--bp-lg",  768),
        ("--bp-xl",  1024),
        ("--bp-2xl", 1280),
    ]

    lines = [":root {"]

    # 1. Font size tokens
    step_names = ["xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl", "5xl"]
    for step in step_names:
        lines.append(f"  --font-size-{step}: {type_scale[step]}px;")

    # 2. Spacing tokens
    for n in range(1, 11):
        lines.append(f"  --space-{n}: {spacing_scale[n]}px;")

    # 3. Fluid typography
    for prop_name, min_px, max_px in fluid_specs:
        clamp_val = compute_fluid(min_px, max_px)
        lines.append(f"  {prop_name}: {clamp_val};")

    # 4. Breakpoints
    for prop_name, px in breakpoints:
        lines.append(f"  {prop_name}: {px};")

    lines.append("}")

    css = "\n".join(lines) + "\n"
    (workspace / "tokens.css").write_text(css)
    print("tokens.css written")
    print()
    print("--- Type scale ---")
    for step in step_names:
        raw = 16 * (1.25 ** ["xs","sm","base","lg","xl","2xl","3xl","4xl","5xl"].index(step) - 2)
        print(f"  --font-size-{step}: {type_scale[step]}px  (raw={16*(1.25**(list(['xs','sm','base','lg','xl','2xl','3xl','4xl','5xl']).index(step)-2)):.4f})")

    print()
    print("--- Fluid ---")
    for prop_name, min_px, max_px in fluid_specs:
        print(f"  {prop_name}: {compute_fluid(min_px, max_px)}")


if __name__ == "__main__":
    main()

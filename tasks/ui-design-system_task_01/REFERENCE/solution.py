"""
Reference solution for ui-design-system_task_01.

Reads: fixtures/brand-brief.md (implicitly — we know the spec from the task)
Produces:
  tokens.json   — full design token palette + semantic tokens
  contrast-audit.json — WCAG 2.1 contrast ratios for required pairs

Color generation:
- Brand anchor: #1A56DB -> primary-500
- primary palette: generate a 9-step scale (50,100,...,900) using HSL manipulation
- neutral palette: desaturated gray family based on the primary hue
- semantic tokens: reference palette token keys exactly

WCAG contrast formula (2.1 spec):
  relative_luminance = sum(0.2126*R + 0.7152*G + 0.0722*B)
  where each channel is linearized: c <= 0.03928 -> c/12.92, else ((c+0.055)/1.055)^2.4
  contrast = (L_lighter + 0.05) / (L_darker + 0.05)
"""

import json
import math
import colorsys
from pathlib import Path


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return h, s, l


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return round(r * 255), round(g * 255), round(b * 255)


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def generate_primary_scale(anchor_hex: str) -> dict[str, str]:
    """
    Generate 9-step primary scale from anchor hex (which becomes step 500).
    Lighter steps (50-400): increase lightness, reduce saturation slightly.
    Darker steps (600-900): decrease lightness.
    """
    r, g, b = hex_to_rgb(anchor_hex)
    h, s, l = rgb_to_hsl(r, g, b)

    # anchor is 500
    # Steps and their target lightness values (normalized 0-1)
    step_lightness = {
        50:  0.97,
        100: 0.94,
        200: 0.88,
        300: 0.78,
        400: 0.65,
        500: l,          # original
        600: l * 0.78,
        700: l * 0.58,
        800: l * 0.38,
        900: l * 0.20,
    }

    # Saturation adjustments (lighter steps are more muted)
    step_saturation = {
        50:  clamp(s * 0.40, 0, 1),
        100: clamp(s * 0.50, 0, 1),
        200: clamp(s * 0.62, 0, 1),
        300: clamp(s * 0.74, 0, 1),
        400: clamp(s * 0.86, 0, 1),
        500: s,
        600: clamp(s * 1.00, 0, 1),
        700: clamp(s * 1.00, 0, 1),
        800: clamp(s * 1.00, 0, 1),
        900: clamp(s * 1.00, 0, 1),
    }

    scale = {}
    for step in [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]:
        target_l = clamp(step_lightness[step], 0.01, 0.99)
        target_s = step_saturation[step]
        r2, g2, b2 = hsl_to_rgb(h, target_s, target_l)
        scale[step] = rgb_to_hex(r2, g2, b2)

    return scale


def generate_neutral_scale(anchor_hex: str) -> dict[str, str]:
    """
    Generate neutral gray scale. Use same hue but very low saturation.
    """
    r, g, b = hex_to_rgb(anchor_hex)
    h, s, l = rgb_to_hsl(r, g, b)

    # Neutral: near-zero saturation, full lightness range
    step_lightness = {
        50:  0.975,
        100: 0.955,
        200: 0.92,
        300: 0.84,
        400: 0.72,
        500: 0.56,
        600: 0.42,
        700: 0.30,
        800: 0.18,
        900: 0.08,
    }
    neutral_saturation = 0.06  # very low, slightly chromatic

    scale = {}
    for step in [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]:
        target_l = step_lightness[step]
        r2, g2, b2 = hsl_to_rgb(h, neutral_saturation, target_l)
        scale[step] = rgb_to_hex(r2, g2, b2)

    return scale


def linearize(c: float) -> float:
    """Convert sRGB channel (0-1) to linear light."""
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    r, g, b = hex_to_rgb(hex_color)
    R = linearize(r / 255)
    G = linearize(g / 255)
    B = linearize(b / 255)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def contrast_ratio(hex1: str, hex2: str) -> float:
    l1 = relative_luminance(hex1)
    l2 = relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def main():
    workspace = Path(".")

    # Generate palettes
    primary_scale = generate_primary_scale("#1A56DB")
    neutral_scale = generate_neutral_scale("#1A56DB")

    # Build flat token dict (palette tokens)
    tokens = {}
    for step in [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]:
        tokens[f"color.brand.primary.{step}"] = primary_scale[step]
    for step in [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]:
        tokens[f"color.brand.neutral.{step}"] = neutral_scale[step]

    # Add semantic tokens (values are REFERENCES to palette token keys)
    semantic_map = {
        "color.semantic.action":         "color.brand.primary.500",
        "color.semantic.action-hover":   "color.brand.primary.600",
        "color.semantic.action-text":    "color.brand.primary.900",
        "color.semantic.background":     "color.brand.neutral.50",
        "color.semantic.surface":        "color.brand.neutral.100",
        "color.semantic.border":         "color.brand.neutral.300",
        "color.semantic.text-primary":   "color.brand.neutral.900",
        "color.semantic.text-secondary": "color.brand.neutral.600",
    }
    for sem_key, palette_ref in semantic_map.items():
        tokens[sem_key] = palette_ref

    # Write tokens.json
    (workspace / "tokens.json").write_text(json.dumps(tokens, indent=2))
    print("tokens.json written")

    # Now compute contrast audit
    # Resolve a semantic token to its hex value
    def resolve_hex(token_key: str) -> str:
        val = tokens[token_key]
        # If val is itself a token reference, resolve it
        if val in tokens:
            return tokens[val]
        return val

    audit_pairs = [
        ("color.semantic.action-text",    "color.semantic.background"),
        ("color.semantic.text-primary",   "color.semantic.background"),
        ("color.semantic.text-secondary", "color.semantic.background"),
        ("color.semantic.action-text",    "color.semantic.surface"),
        ("color.semantic.text-primary",   "color.semantic.surface"),
    ]

    audit = []
    for fg_token, bg_token in audit_pairs:
        fg_hex = resolve_hex(fg_token)
        bg_hex = resolve_hex(bg_token)
        ratio = contrast_ratio(fg_hex, bg_hex)
        ratio_rounded = round(ratio, 2)
        audit.append({
            "pair": f"{fg_token} on {bg_token}",
            "ratio": ratio_rounded,
            "aa_normal": ratio_rounded >= 4.5,
            "aa_large": ratio_rounded >= 3.0,
            "aaa_normal": ratio_rounded >= 7.0,
        })

    (workspace / "contrast-audit.json").write_text(json.dumps(audit, indent=2))
    print("contrast-audit.json written")

    # Print expected values for grade.py authoring
    print("\n--- Token values (for grade.py) ---")
    for k, v in tokens.items():
        print(f"  {k!r}: {v!r}")

    print("\n--- Contrast audit ---")
    for entry in audit:
        print(f"  {entry}")


if __name__ == "__main__":
    main()

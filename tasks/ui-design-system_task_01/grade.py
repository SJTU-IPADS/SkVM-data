"""
Grade function for ui-design-system_task_01.

Checks:
1. tokens.json exists and parses as JSON
2. Flat dot-notation key structure (not nested — archetype 1: naming convention trap)
3. All 9-step palette keys present for color.brand.primary and color.brand.neutral
4. Semantic token keys all present
5. Semantic token values are palette token references (not hex colors) — archetype 5 invariant
6. Semantic token reference target exists in the token set
7. contrast-audit.json exists and parses
8. Audit contains exactly 5 entries with required pair names (archetype 3: multi-step coordination)
9. Each audit entry has ratio, aa_normal, aa_large, aaa_normal fields
10. WCAG contrast ratios are computed correctly (within 0.15 tolerance — archetype 4: formula correctness)
11. aa_normal / aa_large / aaa_normal booleans match the ratio (self-consistency invariant — archetype 5)
12. Semantic references all resolve to valid hex tokens in the file
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

PALETTE_STEPS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]
PALETTE_NAMES = ["primary", "neutral"]
REQUIRED_PALETTE_KEYS = {
    f"color.brand.{palette}.{step}"
    for palette in PALETTE_NAMES
    for step in PALETTE_STEPS
}

REQUIRED_SEMANTIC_KEYS = {
    "color.semantic.action",
    "color.semantic.action-hover",
    "color.semantic.action-text",
    "color.semantic.background",
    "color.semantic.surface",
    "color.semantic.border",
    "color.semantic.text-primary",
    "color.semantic.text-secondary",
}

SEMANTIC_REQUIRED_REFS = {
    "color.semantic.action":         "color.brand.primary.500",
    "color.semantic.action-hover":   "color.brand.primary.600",
    "color.semantic.action-text":    "color.brand.primary.900",
    "color.semantic.background":     "color.brand.neutral.50",
    "color.semantic.surface":        "color.brand.neutral.100",
    "color.semantic.border":         "color.brand.neutral.300",
    "color.semantic.text-primary":   "color.brand.neutral.900",
    "color.semantic.text-secondary": "color.brand.neutral.600",
}

REQUIRED_AUDIT_PAIRS = [
    "color.semantic.action-text on color.semantic.background",
    "color.semantic.text-primary on color.semantic.background",
    "color.semantic.text-secondary on color.semantic.background",
    "color.semantic.action-text on color.semantic.surface",
    "color.semantic.text-primary on color.semantic.surface",
]

HEX_RE = re.compile(r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int] | None:
    if not HEX_RE.match(hex_color):
        return None
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _linearize(c: float) -> float:
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def _luminance(hex_color: str) -> float | None:
    rgb = _hex_to_rgb(hex_color)
    if rgb is None:
        return None
    r, g, b = rgb
    R = _linearize(r / 255)
    G = _linearize(g / 255)
    B = _linearize(b / 255)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def _contrast_ratio(hex1: str, hex2: str) -> float | None:
    l1 = _luminance(hex1)
    l2 = _luminance(hex2)
    if l1 is None or l2 is None:
        return None
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _load_tokens(workspace_path: str) -> tuple[dict | None, str | None]:
    p = Path(workspace_path) / "tokens.json"
    if not p.exists():
        return None, "tokens.json not found"
    try:
        obj = json.loads(p.read_text())
    except Exception as e:
        return None, f"tokens.json parse error: {e}"
    if not isinstance(obj, dict):
        return None, "tokens.json is not a JSON object"
    return obj, None


def _load_audit(workspace_path: str) -> tuple[list | None, str | None]:
    p = Path(workspace_path) / "contrast-audit.json"
    if not p.exists():
        return None, "contrast-audit.json not found"
    try:
        obj = json.loads(p.read_text())
    except Exception as e:
        return None, f"contrast-audit.json parse error: {e}"
    if not isinstance(obj, list):
        return None, "contrast-audit.json is not a JSON array"
    return obj, None


CRITERIA = [
    # C1: tokens.json exists
    {
        "id": "tokens-exists",
        "weight": 0.04,
        "description": "tokens.json exists at the workspace root and is valid JSON — the primary output artifact.",
    },
    # C2: Flat dot-notation keys (not nested JSON) — archetype 1 trap
    {
        "id": "flat-dot-notation",
        "weight": 0.10,
        "description": "tokens.json uses a flat object with dot-notation keys like 'color.brand.primary.500', not a nested JSON tree. Models default to nested JSON; the spec requires flat keys.",
    },
    # C3: All palette keys present
    {
        "id": "palette-keys-complete",
        "weight": 0.10,
        "description": "tokens.json contains all 20 palette token keys: 9 steps (50–900) for color.brand.primary and color.brand.neutral each.",
    },
    # C4: Palette values are hex colors
    {
        "id": "palette-values-hex",
        "weight": 0.06,
        "description": "Every palette token value (color.brand.primary.* and color.brand.neutral.*) is a valid hex color string like '#1A56DB'.",
    },
    # C5: All semantic keys present
    {
        "id": "semantic-keys-present",
        "weight": 0.06,
        "description": "tokens.json contains all 8 required semantic token keys (color.semantic.action, color.semantic.action-hover, etc.).",
    },
    # C6: Semantic values are token references, not hex — archetype 5 invariant
    {
        "id": "semantic-values-are-refs",
        "weight": 0.14,
        "description": "Every semantic token value is a reference to a palette token key (a string that is itself a key in tokens.json), not a raw hex color. This is the alias-reference pattern that lets themes compose without editing semantic tokens.",
    },
    # C7: Semantic references match the specified mapping — archetype 1
    {
        "id": "semantic-ref-mapping",
        "weight": 0.12,
        "description": "Each semantic token references the specific palette token prescribed in the spec: action→primary.500, action-hover→primary.600, action-text→primary.900, background→neutral.50, surface→neutral.100, border→neutral.300, text-primary→neutral.900, text-secondary→neutral.600.",
    },
    # C8: contrast-audit.json exists
    {
        "id": "audit-exists",
        "weight": 0.04,
        "description": "contrast-audit.json exists at the workspace root and is a JSON array.",
    },
    # C9: Audit has exactly 5 entries with correct pair strings — archetype 3
    {
        "id": "audit-pairs-correct",
        "weight": 0.10,
        "description": "contrast-audit.json contains exactly the 5 required pair strings in the specified order: action-text on background, text-primary on background, text-secondary on background, action-text on surface, text-primary on surface.",
    },
    # C10: Audit entries have required fields
    {
        "id": "audit-fields-present",
        "weight": 0.04,
        "description": "Each contrast audit entry has the fields: pair (string), ratio (number), aa_normal (boolean), aa_large (boolean), aaa_normal (boolean).",
    },
    # C11: WCAG ratios are correct within tolerance — archetype 4
    {
        "id": "audit-ratios-correct",
        "weight": 0.12,
        "description": "Contrast ratios in contrast-audit.json are computed using the WCAG 2.1 formula (gamma-corrected relative luminance) and match the expected values within ±0.15. A common error is using simplified sRGB averaging instead of the linearization formula.",
    },
    # C12: Boolean flags are self-consistent with ratios — archetype 5
    {
        "id": "audit-booleans-consistent",
        "weight": 0.08,
        "description": "aa_normal (≥4.5), aa_large (≥3.0), and aaa_normal (≥7.0) in each audit entry correctly reflect the entry's own ratio value — a self-consistency invariant that catches rounding or threshold errors.",
    },
]

# Verify weights at import time
_wsum = sum(c["weight"] for c in CRITERIA)
assert abs(_wsum - 1.0) < 1e-3, f"CRITERIA weights sum to {_wsum}"


def grade(transcript, workspace_path):
    tokens, _terr = _load_tokens(workspace_path)
    audit, _aerr = _load_audit(workspace_path)

    results = []

    # C1: tokens-exists
    score = 1.0 if tokens is not None else 0.0
    results.append({"id": "tokens-exists", "score": score, "weight": 0.04,
                    "description": CRITERIA[0]["description"],
                    **({"details": _terr} if score < 1.0 else {})})

    # C2: flat-dot-notation
    if tokens is None:
        results.append({"id": "flat-dot-notation", "score": 0.0, "weight": 0.10,
                        "description": CRITERIA[1]["description"],
                        "details": "tokens.json missing"})
    else:
        # Check values are not dicts (would indicate nested structure)
        nested_keys = [k for k, v in tokens.items() if isinstance(v, dict)]
        if nested_keys:
            results.append({"id": "flat-dot-notation", "score": 0.0, "weight": 0.10,
                            "description": CRITERIA[1]["description"],
                            "details": f"tokens.json has nested objects at keys: {nested_keys[:3]}"})
        else:
            # Check keys use dot-notation (contain dots)
            dot_keys = [k for k in tokens if "." in k]
            if len(dot_keys) < 10:
                results.append({"id": "flat-dot-notation", "score": 0.0, "weight": 0.10,
                                "description": CRITERIA[1]["description"],
                                "details": f"Only {len(dot_keys)} keys use dot-notation; expected ≥10"})
            else:
                results.append({"id": "flat-dot-notation", "score": 1.0, "weight": 0.10,
                                "description": CRITERIA[1]["description"]})

    # C3: palette-keys-complete
    if tokens is None:
        results.append({"id": "palette-keys-complete", "score": 0.0, "weight": 0.10,
                        "description": CRITERIA[2]["description"], "details": "tokens.json missing"})
    else:
        missing = REQUIRED_PALETTE_KEYS - set(tokens.keys())
        if missing:
            results.append({"id": "palette-keys-complete", "score": 0.0, "weight": 0.10,
                            "description": CRITERIA[2]["description"],
                            "details": f"Missing palette keys: {sorted(missing)[:5]}"})
        else:
            results.append({"id": "palette-keys-complete", "score": 1.0, "weight": 0.10,
                            "description": CRITERIA[2]["description"]})

    # C4: palette-values-hex
    if tokens is None:
        results.append({"id": "palette-values-hex", "score": 0.0, "weight": 0.06,
                        "description": CRITERIA[3]["description"], "details": "tokens.json missing"})
    else:
        bad = []
        for key in REQUIRED_PALETTE_KEYS:
            val = tokens.get(key)
            if val is None:
                continue  # already caught by C3
            if not isinstance(val, str) or not HEX_RE.match(val):
                bad.append(f"{key}={val!r}")
        if bad:
            results.append({"id": "palette-values-hex", "score": 0.0, "weight": 0.06,
                            "description": CRITERIA[3]["description"],
                            "details": f"Non-hex palette values: {bad[:3]}"})
        else:
            results.append({"id": "palette-values-hex", "score": 1.0, "weight": 0.06,
                            "description": CRITERIA[3]["description"]})

    # C5: semantic-keys-present
    if tokens is None:
        results.append({"id": "semantic-keys-present", "score": 0.0, "weight": 0.06,
                        "description": CRITERIA[4]["description"], "details": "tokens.json missing"})
    else:
        missing_sem = REQUIRED_SEMANTIC_KEYS - set(tokens.keys())
        if missing_sem:
            results.append({"id": "semantic-keys-present", "score": 0.0, "weight": 0.06,
                            "description": CRITERIA[4]["description"],
                            "details": f"Missing semantic keys: {sorted(missing_sem)}"})
        else:
            results.append({"id": "semantic-keys-present", "score": 1.0, "weight": 0.06,
                            "description": CRITERIA[4]["description"]})

    # C6: semantic-values-are-refs — key invariant
    if tokens is None:
        results.append({"id": "semantic-values-are-refs", "score": 0.0, "weight": 0.14,
                        "description": CRITERIA[5]["description"], "details": "tokens.json missing"})
    else:
        bad_refs = []
        for sem_key in REQUIRED_SEMANTIC_KEYS:
            val = tokens.get(sem_key)
            if val is None:
                continue
            # Value must be a string that is itself a key in the token dict
            if not isinstance(val, str) or val not in tokens:
                bad_refs.append(f"{sem_key}={val!r}")
        if bad_refs:
            results.append({"id": "semantic-values-are-refs", "score": 0.0, "weight": 0.14,
                            "description": CRITERIA[5]["description"],
                            "details": f"Semantic tokens with non-reference values: {bad_refs[:3]}"})
        else:
            results.append({"id": "semantic-values-are-refs", "score": 1.0, "weight": 0.14,
                            "description": CRITERIA[5]["description"]})

    # C7: semantic-ref-mapping
    if tokens is None:
        results.append({"id": "semantic-ref-mapping", "score": 0.0, "weight": 0.12,
                        "description": CRITERIA[6]["description"], "details": "tokens.json missing"})
    else:
        wrong = []
        for sem_key, expected_ref in SEMANTIC_REQUIRED_REFS.items():
            actual = tokens.get(sem_key)
            if actual != expected_ref:
                wrong.append(f"{sem_key}: expected {expected_ref!r}, got {actual!r}")
        if wrong:
            results.append({"id": "semantic-ref-mapping", "score": 0.0, "weight": 0.12,
                            "description": CRITERIA[6]["description"],
                            "details": f"Wrong references: {'; '.join(wrong[:3])}"})
        else:
            results.append({"id": "semantic-ref-mapping", "score": 1.0, "weight": 0.12,
                            "description": CRITERIA[6]["description"]})

    # C8: audit-exists
    score = 1.0 if audit is not None else 0.0
    results.append({"id": "audit-exists", "score": score, "weight": 0.04,
                    "description": CRITERIA[7]["description"],
                    **({"details": _aerr} if score < 1.0 else {})})

    # C9: audit-pairs-correct
    if audit is None:
        results.append({"id": "audit-pairs-correct", "score": 0.0, "weight": 0.10,
                        "description": CRITERIA[8]["description"], "details": "contrast-audit.json missing"})
    else:
        actual_pairs = [entry.get("pair") for entry in audit if isinstance(entry, dict)]
        if actual_pairs == REQUIRED_AUDIT_PAIRS:
            results.append({"id": "audit-pairs-correct", "score": 1.0, "weight": 0.10,
                            "description": CRITERIA[8]["description"]})
        else:
            results.append({"id": "audit-pairs-correct", "score": 0.0, "weight": 0.10,
                            "description": CRITERIA[8]["description"],
                            "details": f"Expected pairs: {REQUIRED_AUDIT_PAIRS}, got: {actual_pairs}"})

    # C10: audit-fields-present
    if audit is None:
        results.append({"id": "audit-fields-present", "score": 0.0, "weight": 0.04,
                        "description": CRITERIA[9]["description"], "details": "contrast-audit.json missing"})
    else:
        required_fields = {"pair", "ratio", "aa_normal", "aa_large", "aaa_normal"}
        bad_entries = []
        for i, entry in enumerate(audit):
            if not isinstance(entry, dict):
                bad_entries.append(f"entry {i} not a dict")
                continue
            missing_f = required_fields - set(entry.keys())
            if missing_f:
                bad_entries.append(f"entry {i} missing: {sorted(missing_f)}")
        if bad_entries:
            results.append({"id": "audit-fields-present", "score": 0.0, "weight": 0.04,
                            "description": CRITERIA[9]["description"],
                            "details": f"{bad_entries[:2]}"})
        else:
            results.append({"id": "audit-fields-present", "score": 1.0, "weight": 0.04,
                            "description": CRITERIA[9]["description"]})

    # C11: audit-ratios-correct
    # We need the tokens to resolve semantic token refs to hex for computing expected ratios
    if audit is None or tokens is None:
        results.append({"id": "audit-ratios-correct", "score": 0.0, "weight": 0.12,
                        "description": CRITERIA[10]["description"],
                        "details": "tokens.json or contrast-audit.json missing"})
    else:
        def resolve_hex(tok_key: str) -> str | None:
            val = tokens.get(tok_key)
            if val is None:
                return None
            if HEX_RE.match(val):
                return val
            # It's a reference; resolve one level
            resolved = tokens.get(val)
            if resolved and HEX_RE.match(resolved):
                return resolved
            return None

        ratio_errors = []
        for entry in audit:
            if not isinstance(entry, dict):
                continue
            pair_str = entry.get("pair", "")
            reported_ratio = entry.get("ratio")
            if not isinstance(reported_ratio, (int, float)):
                ratio_errors.append(f"{pair_str}: ratio not numeric")
                continue
            # Parse pair string
            parts = pair_str.split(" on ", 1)
            if len(parts) != 2:
                ratio_errors.append(f"Unparseable pair: {pair_str!r}")
                continue
            fg_tok, bg_tok = parts[0].strip(), parts[1].strip()
            fg_hex = resolve_hex(fg_tok)
            bg_hex = resolve_hex(bg_tok)
            if fg_hex is None or bg_hex is None:
                # Can't verify - tokens might be missing; skip ratio check
                continue
            expected_ratio = _contrast_ratio(fg_hex, bg_hex)
            if expected_ratio is None:
                continue
            if abs(float(reported_ratio) - expected_ratio) > 0.15:
                ratio_errors.append(
                    f"{pair_str}: expected ≈{expected_ratio:.2f}, got {reported_ratio}"
                )
        if ratio_errors:
            results.append({"id": "audit-ratios-correct", "score": 0.0, "weight": 0.12,
                            "description": CRITERIA[10]["description"],
                            "details": f"{ratio_errors[:2]}"})
        else:
            results.append({"id": "audit-ratios-correct", "score": 1.0, "weight": 0.12,
                            "description": CRITERIA[10]["description"]})

    # C12: audit-booleans-consistent
    if audit is None:
        results.append({"id": "audit-booleans-consistent", "score": 0.0, "weight": 0.08,
                        "description": CRITERIA[11]["description"], "details": "contrast-audit.json missing"})
    else:
        bool_errors = []
        for entry in audit:
            if not isinstance(entry, dict):
                continue
            ratio = entry.get("ratio")
            aa_n = entry.get("aa_normal")
            aa_l = entry.get("aa_large")
            aaa_n = entry.get("aaa_normal")
            pair_str = entry.get("pair", "?")
            if not isinstance(ratio, (int, float)):
                continue
            r = float(ratio)
            if aa_n != (r >= 4.5):
                bool_errors.append(f"{pair_str}: aa_normal={aa_n} but ratio={r} (expect {r >= 4.5})")
            if aa_l != (r >= 3.0):
                bool_errors.append(f"{pair_str}: aa_large={aa_l} but ratio={r} (expect {r >= 3.0})")
            if aaa_n != (r >= 7.0):
                bool_errors.append(f"{pair_str}: aaa_normal={aaa_n} but ratio={r} (expect {r >= 7.0})")
        if bool_errors:
            results.append({"id": "audit-booleans-consistent", "score": 0.0, "weight": 0.08,
                            "description": CRITERIA[11]["description"],
                            "details": f"{bool_errors[:2]}"})
        else:
            results.append({"id": "audit-booleans-consistent", "score": 1.0, "weight": 0.08,
                            "description": CRITERIA[11]["description"]})

    return results

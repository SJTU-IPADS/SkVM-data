"""
Grade function for revenue-operations_task_01.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: direct checks on forecast_audit.json and gtm_report.json.
All expected values are hardcoded from the deterministic fixture (seed 20260412
in _gen_fixture.py). grade.py does NOT re-run the fixture generator.

Expected outputs:
  forecast_audit.json:
    input_periods: 8
    valid_periods: 7
    excluded_periods: ["2025-Q4"]
    mape_pct: 6.0197
    bias_pct: 6.0197
    bias_direction: "over_forecast"
    rating: "Excellent"
    trend: "Improving" (second-half lower than first-half MAPE)
    category_breakdowns.by_rep: 3 entries with mape_pct

  gtm_report.json:
    metrics.magic_number: ~0.6667
    metrics.ltv_cac: ~16.4766
    metrics.cac_payback_months: ~9.2308
    metrics.burn_multiple: ~1.25
    metrics.rule_of_40: ~23.2
    metrics.ndr_pct: ~105.2632
    ratings.ndr_pct: "Fair"
    below_target: includes "ndr_pct" and "rule_of_40"
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path


# ---- Expected values --------------------------------------------------------

EXP_FORECAST = {
    "input_periods": 8,
    "valid_periods": 7,
    "excluded_periods": ["2025-Q4"],
    "mape_pct": 6.0197,
    "bias_pct": 6.0197,
    "bias_direction": "over_forecast",
    "rating": "Excellent",
}

EXP_GTM = {
    "magic_number": 0.6667,
    "ltv_cac": 16.4766,
    "cac_payback_months": 9.2308,
    "burn_multiple": 1.25,
    "rule_of_40": 23.2,
    "ndr_pct": 105.2632,
}

EXP_GTM_RATINGS = {
    "magic_number": "Good",
    "ltv_cac": "Excellent",
    "cac_payback_months": "Excellent",
    "burn_multiple": "Good",
    "rule_of_40": "Good",
    "ndr_pct": "Fair",
}


# ---- Helpers ----------------------------------------------------------------

def _approx(a, b, rel_tol=0.005, abs_tol=0.01):
    """True if a and b are within relative or absolute tolerance."""
    if a is None or b is None:
        return False
    try:
        return math.isclose(float(a), float(b), rel_tol=rel_tol, abs_tol=abs_tol)
    except (TypeError, ValueError):
        return False


def _load_forecast(workspace_path):
    p = Path(workspace_path) / "forecast_audit.json"
    if not p.exists():
        return None, "forecast_audit.json not found"
    try:
        return json.loads(p.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"forecast_audit.json invalid JSON: {e}"


def _load_gtm(workspace_path):
    p = Path(workspace_path) / "gtm_report.json"
    if not p.exists():
        return None, "gtm_report.json not found"
    try:
        return json.loads(p.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"gtm_report.json invalid JSON: {e}"


# ---- Criterion checks -------------------------------------------------------

def _check_forecast_exists(fa, gr):
    if fa is None:
        return 0.0, "forecast_audit.json missing or unparseable"
    return 1.0, None


def _check_gtm_exists(fa, gr):
    if gr is None:
        return 0.0, "gtm_report.json missing or unparseable"
    return 1.0, None


def _check_forecast_schema(fa, gr):
    if fa is None:
        return 0.0, "forecast_audit.json missing"
    required = {"input_periods", "valid_periods", "excluded_periods", "mape_pct",
                "bias_pct", "bias_direction", "rating"}
    missing = required - set(fa.keys())
    if missing:
        return 0.0, f"forecast_audit.json missing keys: {sorted(missing)}"
    return 1.0, None


def _check_zero_actual_exclusion(fa, gr):
    """The period with actual=0 (2025-Q4) must be EXCLUDED from MAPE computation.
    The grader looks for valid_periods=7 and excluded_periods containing 2025-Q4.
    Agents that include the zero period get MAPE=infinity (division by zero) or skip
    it silently with wrong count."""
    if fa is None:
        return 0.0, "forecast_audit.json missing"
    vp = fa.get("valid_periods")
    ep = fa.get("excluded_periods") or []
    if vp != EXP_FORECAST["valid_periods"]:
        return 0.0, f"valid_periods: expected 7, got {vp} — period with actual=0 must be excluded from MAPE"
    if "2025-Q4" not in ep:
        return 0.0, f"excluded_periods does not contain '2025-Q4' (actual=0 must be excluded); got {ep}"
    return 1.0, None


def _check_mape_value(fa, gr):
    """MAPE computed over exactly 7 valid periods (excluding actual=0).
    Expected: 6.0197%. Agents that include 2025-Q4 in the denominator get
    a different value; agents that compute MAPE wrong (e.g. (f-a)/f instead
    of (f-a)/|a|) also diverge."""
    if fa is None:
        return 0.0, "forecast_audit.json missing"
    got = fa.get("mape_pct")
    if not _approx(got, EXP_FORECAST["mape_pct"], rel_tol=0.01, abs_tol=0.05):
        return 0.0, f"mape_pct: expected ~{EXP_FORECAST['mape_pct']}, got {got}"
    return 1.0, None


def _check_bias_direction(fa, gr):
    """Bias must be identified as 'over_forecast' (forecast > actual consistently).
    Positive bias_pct = over-forecast. Agents may compute bias as actual-forecast
    (negative = under) and label it incorrectly."""
    if fa is None:
        return 0.0, "forecast_audit.json missing"
    direction = fa.get("bias_direction", "")
    if "over" not in str(direction).lower():
        return 0.0, f"bias_direction: expected 'over_forecast', got {direction!r} — all valid periods have forecast > actual"
    bias = fa.get("bias_pct")
    if bias is not None:
        try:
            if float(bias) < 0:
                return 0.0, f"bias_pct is negative ({bias}), but over-forecasting should be positive (forecast > actual)"
        except (TypeError, ValueError):
            pass
    return 1.0, None


def _check_forecast_rating(fa, gr):
    """Rating must be 'Excellent' (MAPE < 10%). This tests that the agent applies
    the four-tier threshold table correctly: Excellent < 10%, Good 10-15%, Fair 15-25%, Poor > 25%."""
    if fa is None:
        return 0.0, "forecast_audit.json missing"
    got = fa.get("rating", "")
    if str(got).lower() != "excellent":
        return 0.0, f"rating: expected 'Excellent' (MAPE=6.02% < 10%), got {got!r}"
    return 1.0, None


def _check_category_breakdown(fa, gr):
    """category_breakdowns must include a by_rep key with 3 entries, each
    carrying mape_pct and bias_pct computed at the category level (not the
    aggregate MAPE). Agents who copy the aggregate MAPE to all categories fail."""
    if fa is None:
        return 0.0, "forecast_audit.json missing"
    cb = fa.get("category_breakdowns") or {}
    by_rep = cb.get("by_rep")
    if not by_rep or not isinstance(by_rep, list):
        return 0.0, "category_breakdowns.by_rep missing or not a list"
    if len(by_rep) != 3:
        return 0.0, f"expected 3 rep entries in by_rep, got {len(by_rep)}"
    # Each entry must have category, mape_pct, bias_pct
    for entry in by_rep:
        for field in ("category", "mape_pct", "bias_pct"):
            if field not in entry:
                return 0.0, f"by_rep entry missing field '{field}': {entry}"
    # Verify MAPE values are distinct per category (not copied from aggregate)
    mape_vals = [entry.get("mape_pct") for entry in by_rep]
    if len(set(str(round(float(v), 2)) if v is not None else "None" for v in mape_vals)) < 2:
        return 0.0, f"all rep mape_pct values are identical ({mape_vals}) — they must be computed per-rep"
    return 1.0, None


def _check_gtm_schema(fa, gr):
    if gr is None:
        return 0.0, "gtm_report.json missing"
    metrics = gr.get("metrics") or {}
    ratings = gr.get("ratings") or {}
    required_metrics = {"magic_number", "ltv_cac", "cac_payback_months", "burn_multiple", "rule_of_40", "ndr_pct"}
    missing_m = required_metrics - set(metrics.keys())
    missing_r = required_metrics - set(ratings.keys())
    if missing_m:
        return 0.0, f"gtm_report.json metrics missing: {sorted(missing_m)}"
    if missing_r:
        return 0.0, f"gtm_report.json ratings missing: {sorted(missing_r)}"
    return 1.0, None


def _check_ndr_formula(fa, gr):
    """NDR must be computed from the customer ARR formula:
    (beginning_arr + expansion_arr - contraction_arr - churned_arr) / beginning_arr * 100.
    Expected: 105.2632%. Agents who use net_new_arr instead of the expansion/contraction/churn
    components (which includes new logo ARR not in the NDR formula) get the wrong answer."""
    if gr is None:
        return 0.0, "gtm_report.json missing"
    ndr = (gr.get("metrics") or {}).get("ndr_pct")
    if not _approx(ndr, EXP_GTM["ndr_pct"], rel_tol=0.005, abs_tol=0.1):
        return 0.0, (
            f"ndr_pct: expected ~{EXP_GTM['ndr_pct']} "
            f"(from beginning+expansion-contraction-churn)/beginning*100, "
            f"got {ndr}"
        )
    return 1.0, None


def _check_ndr_rating(fa, gr):
    """NDR=105.26% must be rated 'Fair' (below the 110% 'Good' threshold).
    Agents often rate NDR > 100% as 'Good' because it's above 1x; the correct
    threshold for SaaS is >110% = Good."""
    if gr is None:
        return 0.0, "gtm_report.json missing"
    ndr_rating = (gr.get("ratings") or {}).get("ndr_pct", "")
    if str(ndr_rating).lower() != "fair":
        return 0.0, f"ratings.ndr_pct: expected 'Fair' (105.26% < 110% threshold), got {ndr_rating!r}"
    return 1.0, None


def _check_rule_of_40(fa, gr):
    """Rule of 40 = Revenue Growth % + FCF Margin %.
    FCF margin is -8.4% (negative), so Rule of 40 = 31.6 + (-8.4) = 23.2.
    Agents who take the absolute value of FCF margin get 40.0 = 'Excellent'."""
    if gr is None:
        return 0.0, "gtm_report.json missing"
    r40 = (gr.get("metrics") or {}).get("rule_of_40")
    if not _approx(r40, EXP_GTM["rule_of_40"], rel_tol=0.01, abs_tol=0.5):
        return 0.0, (
            f"rule_of_40: expected ~{EXP_GTM['rule_of_40']} "
            f"(growth 31.6% + FCF -8.4%), got {r40} — FCF margin must not be treated as absolute"
        )
    return 1.0, None


def _check_below_target_list(fa, gr):
    """below_target list must include 'ndr_pct' and 'rule_of_40' (both rated below Excellent/Good
    against SaaS targets). This tests multi-step coordination: the agent must cross-reference
    computed metric values with their ratings to identify which metrics missed target."""
    if gr is None:
        return 0.0, "gtm_report.json missing"
    bt = gr.get("below_target") or []
    missing = []
    for expected_metric in ("ndr_pct", "rule_of_40"):
        if expected_metric not in bt:
            missing.append(expected_metric)
    if missing:
        return 0.0, f"below_target missing metrics: {missing}; got {bt}"
    return 1.0, None


# ---- Criterion registry -----------------------------------------------------

CRITERIA = [
    {
        "id": "forecast-exists",
        "weight": 0.03,
        "description": "forecast_audit.json exists at the workspace root and parses as valid JSON.",
        "check": _check_forecast_exists,
    },
    {
        "id": "gtm-exists",
        "weight": 0.03,
        "description": "gtm_report.json exists at the workspace root and parses as valid JSON.",
        "check": _check_gtm_exists,
    },
    {
        "id": "forecast-schema",
        "weight": 0.04,
        "description": "forecast_audit.json contains required top-level keys: input_periods, valid_periods, excluded_periods, mape_pct, bias_pct, bias_direction, rating.",
        "check": _check_forecast_schema,
    },
    {
        "id": "zero-actual-exclusion",
        "weight": 0.14,
        "description": "Period 2025-Q4 (actual=0) is excluded from MAPE computation and listed in excluded_periods. Dividing by zero or including the period silently produces incorrect MAPE.",
        "check": _check_zero_actual_exclusion,
    },
    {
        "id": "mape-value",
        "weight": 0.13,
        "description": "mape_pct equals ~6.0197 (mean absolute percentage error over 7 valid periods, computed as mean(|actual-forecast|/|actual|)*100). Wrong formula or wrong period count shifts this value.",
        "check": _check_mape_value,
    },
    {
        "id": "bias-direction",
        "weight": 0.08,
        "description": "bias_direction is 'over_forecast' and bias_pct is positive, because forecast > actual in all 7 valid periods. Agents who compute bias as (actual - forecast) get a negative value and label it 'under_forecast'.",
        "check": _check_bias_direction,
    },
    {
        "id": "forecast-rating",
        "weight": 0.05,
        "description": "rating is 'Excellent' (MAPE < 10%), per the four-tier threshold table in the skill: Excellent < 10%, Good 10-15%, Fair 15-25%, Poor > 25%.",
        "check": _check_forecast_rating,
    },
    {
        "id": "category-breakdown",
        "weight": 0.06,
        "description": "category_breakdowns.by_rep contains 3 entries with per-rep mape_pct and bias_pct computed at category level — not the aggregate MAPE copied uniformly.",
        "check": _check_category_breakdown,
    },
    {
        "id": "gtm-schema",
        "weight": 0.04,
        "description": "gtm_report.json contains a metrics object and a ratings object, each with six keys: magic_number, ltv_cac, cac_payback_months, burn_multiple, rule_of_40, ndr_pct.",
        "check": _check_gtm_schema,
    },
    {
        "id": "ndr-formula",
        "weight": 0.15,
        "description": "ndr_pct is ~105.2632, computed from (beginning_arr + expansion_arr - contraction_arr - churned_arr) / beginning_arr * 100. Agents who substitute net_new_arr for the expansion-net computation get ~131.6%.",
        "check": _check_ndr_formula,
    },
    {
        "id": "ndr-rating",
        "weight": 0.08,
        "description": "ratings.ndr_pct is 'Fair' because NDR=105.26% falls below the SaaS 'Good' threshold of 110%. Agents who rate NDR > 100% as 'Good' without applying the 110% threshold fail this check.",
        "check": _check_ndr_rating,
    },
    {
        "id": "rule-of-40",
        "weight": 0.10,
        "description": "rule_of_40 metric equals ~23.2 (revenue_growth_pct 31.6 + fcf_margin_pct -8.4). Agents who take absolute value of FCF margin compute 40.0 instead.",
        "check": _check_rule_of_40,
    },
    {
        "id": "below-target-list",
        "weight": 0.07,
        "description": "below_target list contains both 'ndr_pct' and 'rule_of_40', identifying the two metrics that fall below their SaaS benchmark targets in this dataset.",
        "check": _check_below_target_list,
    },
]

# Sanity check at import time
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    fa, _ = _load_forecast(workspace_path)
    gr, _ = _load_gtm(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](fa, gr)
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

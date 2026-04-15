"""
Reference solution for revenue-operations_task_01.

Reads forecast_data.json and gtm_data.json from the workspace (cwd).
Produces:
  forecast_audit.json   — forecast accuracy analysis
  gtm_report.json       — GTM efficiency metrics
"""
import json
import math
from pathlib import Path

# --- Load inputs ---
forecast_data = json.loads(Path("forecast_data.json").read_text())
gtm_data = json.loads(Path("gtm_data.json").read_text())

# ============================================================
# FORECAST AUDIT
# ============================================================

periods = forecast_data["forecast_periods"]

# Step 1: Filter out zero-actual periods before computing MAPE
# (dividing by zero is undefined; must exclude, not substitute 0)
valid_periods = [p for p in periods if p["actual"] > 0]
excluded_periods = [p["period"] for p in periods if p["actual"] <= 0]

# Step 2: MAPE = mean(|actual - forecast| / |actual|) * 100
ape_values = [abs(p["actual"] - p["forecast"]) / p["actual"] * 100 for p in valid_periods]
mape = sum(ape_values) / len(ape_values)

# Step 3: Bias = mean((forecast - actual) / actual) * 100
# Positive bias = systematic over-forecasting (forecast > actual)
bias_values = [(p["forecast"] - p["actual"]) / p["actual"] * 100 for p in valid_periods]
bias = sum(bias_values) / len(bias_values)

# Step 4: Rating
if mape < 10:
    rating = "Excellent"
elif mape < 15:
    rating = "Good"
elif mape < 25:
    rating = "Fair"
else:
    rating = "Poor"

# Step 5: Trend — compare first half vs second half of valid periods
mid = len(valid_periods) // 2
first_half_mape = sum(abs(p["actual"] - p["forecast"]) / p["actual"] * 100 for p in valid_periods[:mid]) / mid
second_half_mape = sum(abs(p["actual"] - p["forecast"]) / p["actual"] * 100 for p in valid_periods[mid:]) / (len(valid_periods) - mid)
if second_half_mape < first_half_mape * 0.9:
    trend = "Improving"
elif second_half_mape > first_half_mape * 1.1:
    trend = "Declining"
else:
    trend = "Stable"

# Step 6: Category breakdown (by_rep for latest available period context)
category_breakdowns = {}
for dim, entries in forecast_data.get("category_breakdowns", {}).items():
    breakdown = []
    for entry in entries:
        if entry["actual"] > 0:
            cat_ape = abs(entry["actual"] - entry["forecast"]) / entry["actual"] * 100
            cat_bias = (entry["forecast"] - entry["actual"]) / entry["actual"] * 100
        else:
            cat_ape = None
            cat_bias = None
        breakdown.append({
            "category": entry["category"],
            "forecast": entry["forecast"],
            "actual": entry["actual"],
            "mape_pct": round(cat_ape, 4) if cat_ape is not None else None,
            "bias_pct": round(cat_bias, 4) if cat_bias is not None else None,
        })
    category_breakdowns[dim] = breakdown

# Step 7: Periods summary
periods_summary = []
for p in periods:
    if p["actual"] > 0:
        ape = abs(p["actual"] - p["forecast"]) / p["actual"] * 100
        bias_val = (p["forecast"] - p["actual"]) / p["actual"] * 100
        periods_summary.append({
            "period": p["period"],
            "forecast": p["forecast"],
            "actual": p["actual"],
            "ape_pct": round(ape, 4),
            "bias_pct": round(bias_val, 4),
            "excluded": False,
        })
    else:
        periods_summary.append({
            "period": p["period"],
            "forecast": p["forecast"],
            "actual": p["actual"],
            "ape_pct": None,
            "bias_pct": None,
            "excluded": True,
            "exclusion_reason": "zero_actual",
        })

forecast_audit = {
    "input_periods": len(periods),
    "valid_periods": len(valid_periods),
    "excluded_periods": excluded_periods,
    "mape_pct": round(mape, 4),
    "bias_pct": round(bias, 4),
    "bias_direction": "over_forecast" if bias > 0 else "under_forecast",
    "rating": rating,
    "trend": trend,
    "periods_detail": periods_summary,
    "category_breakdowns": category_breakdowns,
}

Path("forecast_audit.json").write_text(json.dumps(forecast_audit, indent=2))
print(f"forecast_audit.json: MAPE={mape:.4f}%, bias={bias:.4f}%, rating={rating}")

# ============================================================
# GTM REPORT
# ============================================================

rev = gtm_data["revenue"]
costs = gtm_data["costs"]
customers = gtm_data["customers"]

# Magic Number = Net New ARR / Prior Period S&M Spend
magic_number = rev["net_new_arr"] / costs["sales_marketing_spend"]

# LTV:CAC = (ARPA * 12 * Gross Margin / Churn Rate) / CAC
gross_margin_frac = costs["gross_margin_pct"] / 100
annual_churn_rate = customers["annual_churn_rate_pct"] / 100
ltv_cac = (rev["arpa_monthly"] * 12 * gross_margin_frac / annual_churn_rate) / costs["cac"]

# CAC Payback = CAC / (ARPA * Gross Margin) in months
cac_payback_months = costs["cac"] / (rev["arpa_monthly"] * gross_margin_frac)

# Burn Multiple = Net Burn / Net New ARR
burn_multiple = costs["net_burn"] / rev["net_new_arr"]

# Rule of 40 = Revenue Growth % + FCF Margin %
rule_of_40 = rev["revenue_growth_pct"] + costs["fcf_margin_pct"]

# NDR = (Beginning ARR + Expansion - Contraction - Churn) / Beginning ARR * 100
# NOTE: This uses the customer ARR components, NOT net_new_arr
# net_new_arr includes new logo ARR; NDR only covers the existing cohort
ndr_pct = (
    (customers["beginning_arr"] + customers["expansion_arr"]
     - customers["contraction_arr"] - customers["churned_arr"])
    / customers["beginning_arr"]
) * 100

# Ratings
def rate_magic(v):
    if v > 0.75: return "Excellent"
    if v > 0.5: return "Good"
    if v > 0.25: return "Fair"
    return "Poor"

def rate_ltv_cac(v):
    if v > 3: return "Excellent"
    if v > 2: return "Good"
    if v > 1: return "Fair"
    return "Poor"

def rate_cac_payback(v):
    if v < 12: return "Excellent"
    if v < 18: return "Good"
    if v < 24: return "Fair"
    return "Poor"

def rate_burn_multiple(v):
    if v < 1: return "Excellent"
    if v < 2: return "Good"
    if v < 4: return "Fair"
    return "Poor"

def rate_rule_of_40(v):
    if v >= 40: return "Excellent"
    if v >= 25: return "Good"
    if v >= 10: return "Fair"
    return "Poor"

def rate_ndr(v):
    if v >= 120: return "Excellent"
    if v >= 110: return "Good"
    if v >= 100: return "Fair"
    return "Poor"

# Collect all ratings
all_ratings = {
    "magic_number": rate_magic(magic_number),
    "ltv_cac": rate_ltv_cac(ltv_cac),
    "cac_payback_months": rate_cac_payback(cac_payback_months),
    "burn_multiple": rate_burn_multiple(burn_multiple),
    "rule_of_40": rate_rule_of_40(rule_of_40),
    "ndr_pct": rate_ndr(ndr_pct),
}

# "Below target" means not Excellent — i.e. the industry benchmark is not met
# Per the skill's defined targets: Magic >0.75, NDR >110%, Rule of 40 >40%
BELOW_TARGET_THRESHOLD = {"Poor", "Fair"}

gtm_report = {
    "metrics": {
        "magic_number": round(magic_number, 4),
        "ltv_cac": round(ltv_cac, 4),
        "cac_payback_months": round(cac_payback_months, 4),
        "burn_multiple": round(burn_multiple, 4),
        "rule_of_40": round(rule_of_40, 4),
        "ndr_pct": round(ndr_pct, 4),
    },
    "ratings": all_ratings,
    "below_target": [k for k, r in all_ratings.items() if r in BELOW_TARGET_THRESHOLD],
}

Path("gtm_report.json").write_text(json.dumps(gtm_report, indent=2))
print(f"gtm_report.json: NDR={ndr_pct:.4f}%, magic={magic_number:.4f}, rule_of_40={rule_of_40:.4f}")
print(f"Below target: {gtm_report['below_target']}")

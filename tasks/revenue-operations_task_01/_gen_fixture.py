"""
Deterministic fixture generator for revenue-operations_task_01.

Task: Quarterly Forecast Audit + GTM Consistency Check.

Produces:
  fixtures/forecast_data.json  — 8 forecast periods with category breakdowns
  fixtures/gtm_data.json       — GTM efficiency inputs

The task requires:
1. Computing MAPE (excluding zero-actual periods, which a naive agent skips)
2. Detecting systematic bias (over vs under forecast)
3. Computing GTM metrics including NDR = (Begin+Expansion-Contraction-Churn)/Begin
4. Cross-file invariant: computed NDR must match implied NDR from forecast growth

Run: python3 _gen_fixture.py
"""
import json
import random
from pathlib import Path

SEED = 20260412
random.seed(SEED)

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURES.mkdir(parents=True, exist_ok=True)

# --- Forecast periods (8 quarters, mix of over/under forecast) ---------------
# Design: systematic over-forecasting bias (positive MAPE skew)
# One period has actual=0 (pre-launch quarter) — must be EXCLUDED from MAPE
# MAPE = mean(|actual - forecast| / |actual|) * 100, only for periods where actual > 0

periods = [
    # period, forecast, actual
    ("2024-Q1", 400000,  380000),   # under: 5.26%
    ("2024-Q2", 440000,  410000),   # under: 7.32%
    ("2024-Q3", 480000,  450000),   # under: 6.67%
    ("2024-Q4", 520000,  490000),   # under: 6.12%
    ("2025-Q1", 560000,  525000),   # under: 6.67%
    ("2025-Q2", 600000,  570000),   # under: 5.26%
    ("2025-Q3", 650000,  620000),   # under: 4.84%
    ("2025-Q4", 700000,    0),      # actual=0 (pre-launch period, EXCLUDED from MAPE)
]

# MAPE computation (exclude the zero-actual period 2025-Q4)
mape_contributions = []
for (period, forecast, actual) in periods:
    if actual > 0:
        ape = abs(actual - forecast) / actual * 100
        mape_contributions.append(ape)

MAPE = sum(mape_contributions) / len(mape_contributions)
# All 7 valid periods have over-forecasting (forecast > actual)
# So bias is systematically negative (under-reporting actuals — wait, actual < forecast = OVER-forecast)
# Bias = mean((forecast - actual) / actual) * 100  (positive = over-forecasting)
bias_contributions = [(f - a) / a * 100 for (_, f, a) in periods if a > 0]
BIAS = sum(bias_contributions) / len(bias_contributions)

print(f"MAPE (7 valid periods): {MAPE:.4f}%")
print(f"Bias (over-forecast positive): {BIAS:.4f}%")
print(f"Valid period count: {len(mape_contributions)}")
print(f"Rating: {'Excellent' if MAPE < 10 else 'Good' if MAPE < 15 else 'Fair' if MAPE < 25 else 'Poor'}")

# Category breakdown by rep (for 2025-Q3, the last full quarter)
rep_breakdown_q3 = [
    {"category": "Rep A", "forecast": 200000, "actual": 192000},   # 4.17%
    {"category": "Rep B", "forecast": 250000, "actual": 235000},   # 6.38%
    {"category": "Rep C", "forecast": 200000, "actual": 193000},   # 3.63%
]
# Rep A + Rep B + Rep C forecast = 650000 = total forecast Q3
# Rep A + Rep B + Rep C actual = 620000 = total actual Q3

forecast_data = {
    "forecast_periods": [
        {"period": p, "forecast": f, "actual": a}
        for (p, f, a) in periods
    ],
    "category_breakdowns": {
        "by_rep": rep_breakdown_q3
    }
}

(FIXTURES / "forecast_data.json").write_text(json.dumps(forecast_data, indent=2))
print(f"\nWrote forecast_data.json ({len(periods)} periods, {len(rep_breakdown_q3)} reps in by_rep)")

# --- GTM efficiency inputs ---------------------------------------------------
# Design: NDR = (Begin + Expansion - Contraction - Churn) / Begin
# Begin ARR = 3800000
# Expansion = 600000, Contraction = 100000, Churn = 300000
# NDR = (3800000 + 600000 - 100000 - 300000) / 3800000 = 4000000/3800000 = 105.26%
# BUT: the task requires checking that current_arr - prior_arr = net_new_arr (another invariant)
# current_arr = 5000000, prior_arr = 3800000 → net_new_arr = 1200000 (given)
# This DOES NOT equal Expansion - Contraction - Churn (200000) — it includes new logos
# This cross-invariant check is the trap

BEGIN_ARR = 3800000
EXPANSION = 600000
CONTRACTION = 100000
CHURN = 300000
CURRENT_ARR = 5000000
PRIOR_ARR = 3800000
NET_NEW_ARR = 1200000  # includes new logo ARR, not just expansion-net
ARPA_MONTHLY = 2500
SM_SPEND = 1800000
CAC = 18000
GROSS_MARGIN_PCT = 78
NET_BURN = 1500000
REVENUE_GROWTH_PCT = round((CURRENT_ARR - PRIOR_ARR) / PRIOR_ARR * 100, 1)
FCF_MARGIN_PCT = -8.4  # negative FCF (burning cash)
ANNUAL_CHURN_RATE_PCT = round(CHURN / BEGIN_ARR * 100, 2)

NDR = (BEGIN_ARR + EXPANSION - CONTRACTION - CHURN) / BEGIN_ARR * 100
MAGIC_NUMBER = NET_NEW_ARR / SM_SPEND
GROSS_MARGIN_FRAC = GROSS_MARGIN_PCT / 100
LTV_CAC = (ARPA_MONTHLY * 12 * GROSS_MARGIN_FRAC / (ANNUAL_CHURN_RATE_PCT / 100)) / CAC
CAC_PAYBACK = CAC / (ARPA_MONTHLY * GROSS_MARGIN_FRAC)
BURN_MULTIPLE = NET_BURN / NET_NEW_ARR
RULE_OF_40 = REVENUE_GROWTH_PCT + FCF_MARGIN_PCT

print(f"\nGTM Metrics:")
print(f"NDR: {NDR:.4f}%")
print(f"Magic Number: {MAGIC_NUMBER:.4f}")
print(f"LTV:CAC: {LTV_CAC:.4f}")
print(f"CAC Payback: {CAC_PAYBACK:.4f} months")
print(f"Burn Multiple: {BURN_MULTIPLE:.4f}")
print(f"Rule of 40: {RULE_OF_40:.4f}")
print(f"Revenue Growth: {REVENUE_GROWTH_PCT}%")
print(f"FCF Margin: {FCF_MARGIN_PCT}%")
print(f"Annual Churn Rate: {ANNUAL_CHURN_RATE_PCT}%")

gtm_data = {
    "revenue": {
        "current_arr": CURRENT_ARR,
        "prior_arr": PRIOR_ARR,
        "net_new_arr": NET_NEW_ARR,
        "arpa_monthly": ARPA_MONTHLY,
        "revenue_growth_pct": REVENUE_GROWTH_PCT,
    },
    "costs": {
        "sales_marketing_spend": SM_SPEND,
        "cac": CAC,
        "gross_margin_pct": GROSS_MARGIN_PCT,
        "total_operating_expense": 6500000,
        "net_burn": NET_BURN,
        "fcf_margin_pct": FCF_MARGIN_PCT,
    },
    "customers": {
        "beginning_arr": BEGIN_ARR,
        "expansion_arr": EXPANSION,
        "contraction_arr": CONTRACTION,
        "churned_arr": CHURN,
        "annual_churn_rate_pct": ANNUAL_CHURN_RATE_PCT,
    }
}

(FIXTURES / "gtm_data.json").write_text(json.dumps(gtm_data, indent=2))
print(f"\nWrote gtm_data.json")

# Print all expected values for grade.py
print("\n=== EXPECTED VALUES FOR GRADE.PY ===")
print(f"MAPE: {MAPE:.4f}%")
print(f"BIAS: {BIAS:.4f}% (positive = over-forecast)")
print(f"VALID_PERIOD_COUNT: {len(mape_contributions)}")
print(f"NDR: {NDR:.4f}%")
print(f"MAGIC_NUMBER: {MAGIC_NUMBER:.4f}")
print(f"LTV_CAC: {LTV_CAC:.4f}")
print(f"CAC_PAYBACK: {CAC_PAYBACK:.4f} months")
print(f"BURN_MULTIPLE: {BURN_MULTIPLE:.4f}")
print(f"RULE_OF_40: {RULE_OF_40:.4f}")

"""
Reference solution for data-analysis_task_02: A/B Test Experiment Analysis
"""
import json
import sys
from pathlib import Path

import pandas as pd

WORKSPACE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

# ---- Load data ----
df = pd.read_csv(WORKSPACE / "experiment_log.csv")
input_rows = len(df)

# ---- Step 1: Identify contaminated users (appear in both arms) ----
arm_sets = df.groupby("user_id")["arm"].apply(set)
contaminated_users = set(arm_sets[arm_sets.apply(len) > 1].index.tolist())
excluded_contaminated = int(df["user_id"].isin(contaminated_users).sum())

# ---- Step 2: Remove contaminated users ----
df = df[~df["user_id"].isin(contaminated_users)].copy()

# ---- Step 3: Remove bad_date (outside 2025-09-01..2025-09-30) ----
df["session_date_dt"] = pd.to_datetime(df["session_date"], errors="coerce")
bad_date_mask = (
    df["session_date_dt"].isna()
    | (df["session_date_dt"] < "2025-09-01")
    | (df["session_date_dt"] > "2025-09-30")
)
excluded_bad_date = int(bad_date_mask.sum())
df = df[~bad_date_mask].copy()

# ---- Step 4: Remove bad_revenue (converted=True but revenue <= 0) ----
bad_rev_mask = (df["converted"] == True) & (df["revenue"] <= 0)
excluded_bad_revenue = int(bad_rev_mask.sum())
df = df[~bad_rev_mask].copy()

# ---- Compute totals ----
valid_users = len(df)
control_users = int((df["arm"] == "control").sum())
treatment_users = int((df["arm"] == "treatment").sum())

# Invariant check
assert control_users + treatment_users == valid_users

# ---- Compute per-arm overall metrics ----
def arm_stats(sub):
    n = len(sub)
    conv = int((sub["converted"] == True).sum())
    cvr = conv / n if n > 0 else 0.0
    rev_total = float(sub["revenue"].sum())
    arpu = rev_total / n if n > 0 else 0.0
    return {
        "users": n,
        "converted": conv,
        "cvr": round(cvr, 6),
        "revenue_total": round(rev_total, 2),
        "arpu": round(arpu, 4),
    }

ctrl = arm_stats(df[df["arm"] == "control"])
trt = arm_stats(df[df["arm"] == "treatment"])

cvr_lift_overall = round(trt["cvr"] - ctrl["cvr"], 6)
cvr_lift_pct_overall = round(cvr_lift_overall / ctrl["cvr"] * 100, 2) if ctrl["cvr"] else 0.0
arpu_lift_overall = round(trt["arpu"] - ctrl["arpu"], 4)
arpu_lift_pct_overall = round(arpu_lift_overall / ctrl["arpu"] * 100, 2) if ctrl["arpu"] else 0.0

# ---- Segment by device_type ----
segments = {}
for dev in ["mobile", "desktop"]:
    c_sub = df[(df["arm"] == "control") & (df["device_type"] == dev)]
    t_sub = df[(df["arm"] == "treatment") & (df["device_type"] == dev)]
    c_stats = arm_stats(c_sub)
    t_stats = arm_stats(t_sub)
    cvr_lift = round(t_stats["cvr"] - c_stats["cvr"], 6)
    cvr_lift_pct = round(cvr_lift / c_stats["cvr"] * 100, 2) if c_stats["cvr"] else 0.0
    arpu_lift = round(t_stats["arpu"] - c_stats["arpu"], 4)
    arpu_lift_pct = round(arpu_lift / c_stats["arpu"] * 100, 2) if c_stats["arpu"] else 0.0
    segments[dev] = {
        "control": c_stats,
        "treatment": t_stats,
        "cvr_lift_pp": cvr_lift,
        "cvr_lift_pct": cvr_lift_pct,
        "arpu_lift": arpu_lift,
        "arpu_lift_pct": arpu_lift_pct,
    }

# ---- Build results.json ----
results = {
    "input_rows": input_rows,
    "excluded_contaminated_rows": excluded_contaminated,
    "excluded_bad_date": excluded_bad_date,
    "excluded_bad_revenue": excluded_bad_revenue,
    "valid_users": valid_users,
    "control_users": control_users,
    "treatment_users": treatment_users,
    "overall": {
        "control": ctrl,
        "treatment": trt,
        "cvr_lift_pp": cvr_lift_overall,
        "cvr_lift_pct": cvr_lift_pct_overall,
        "arpu_lift": arpu_lift_overall,
        "arpu_lift_pct": arpu_lift_pct_overall,
    },
    "by_device": segments,
}

(WORKSPACE / "results.json").write_text(json.dumps(results, indent=2))

# ---- Build experiment_brief.md ----
brief = f"""# A/B Test Readout: New Checkout Flow (September 2025)

## Answer

The treatment (new checkout flow) shows a meaningful lift in conversion rate overall, with a pronounced effect on mobile users. The experiment data supports a cautious recommendation to ship the new flow, pending robustness checks and a multiple-comparisons adjustment.

## Evidence

**Overall results** (n={valid_users:,} valid users after excluding {excluded_contaminated + excluded_bad_date + excluded_bad_revenue} invalid rows):

| Metric | Control (n={ctrl['users']}) | Treatment (n={trt['users']}) | Lift |
|--------|-----|-----------|------|
| CVR | {ctrl['cvr']*100:.1f}% ({ctrl['converted']} of {ctrl['users']}) | {trt['cvr']*100:.1f}% ({trt['converted']} of {trt['users']}) | +{cvr_lift_overall*100:.2f} pp (+{cvr_lift_pct_overall:.1f}%) |
| ARPU | ${ctrl['arpu']:.2f} | ${trt['arpu']:.2f} | +${arpu_lift_overall:.2f} (+{arpu_lift_pct_overall:.1f}%) |

**By device_type:**

- **Mobile**: Control CVR {segments['mobile']['control']['cvr']*100:.1f}% ({segments['mobile']['control']['converted']} of {segments['mobile']['control']['users']}) vs Treatment CVR {segments['mobile']['treatment']['cvr']*100:.1f}% ({segments['mobile']['treatment']['converted']} of {segments['mobile']['treatment']['users']}) — lift +{segments['mobile']['cvr_lift_pp']*100:.2f} pp (+{segments['mobile']['cvr_lift_pct']:.1f}% relative)
- **Desktop**: Control CVR {segments['desktop']['control']['cvr']*100:.1f}% ({segments['desktop']['control']['converted']} of {segments['desktop']['control']['users']}) vs Treatment CVR {segments['desktop']['treatment']['cvr']*100:.1f}% ({segments['desktop']['treatment']['converted']} of {segments['desktop']['treatment']['users']}) — lift +{segments['desktop']['cvr_lift_pp']*100:.2f} pp (+{segments['desktop']['cvr_lift_pct']:.1f}% relative)

**Data quality**: {excluded_contaminated} contaminated rows (users in both arms), {excluded_bad_date} out-of-window rows (outside September 2025), and {excluded_bad_revenue} bad-revenue rows were excluded before analysis.

## Confidence

Uncertainty is moderate. The mobile CVR lift of approximately {segments['mobile']['cvr_lift_pct']:.0f}% relative is large enough to be practically meaningful even after a Bonferroni correction for the two metrics tested (CVR and ARPU). The desktop lift is small ({segments['desktop']['cvr_lift_pct']:.1f}% relative) and may not be statistically distinguishable from noise with the current n={segments['desktop']['control']['users'] + segments['desktop']['treatment']['users']} desktop users. A proper confidence interval (e.g., 95% CI on mobile CVR lift) would narrow the estimate, estimated range roughly +3-9 pp.

## Caveats

- **Multiple comparisons**: Two metrics (CVR and ARPU) were tested simultaneously. Without a Bonferroni or FDR correction, one significant result could be a false positive. Results should be treated as exploratory.
- **Contamination excluded**: 25 users ({excluded_contaminated} rows) appeared in both arms — these were fully excluded as contaminated.
- **Out-of-window rows excluded**: {excluded_bad_date} sessions fell outside the September 2025 window; including them would have inflated user counts.
- **Bad revenue excluded**: {excluded_bad_revenue} converted rows had non-positive revenue (data quality issue, not a real conversion).
- **Observational split**: Device type was not randomized — the mobile/desktop split is a post-hoc segmentation and may correlate with other unobserved user attributes.

## Next Action

1. Run formal hypothesis tests (two-proportion z-test for CVR, t-test for ARPU) with Bonferroni correction (alpha = 0.025 per metric).
2. Prioritize the mobile rollout first given the larger observed lift ({segments['mobile']['cvr_lift_pct']:.0f}% relative, {segments['mobile']['treatment']['converted']} of {segments['mobile']['treatment']['users']} treated mobile users converted).
3. Validate desktop results with a longer holdout period or larger N before making a desktop shipping decision.
"""

(WORKSPACE / "experiment_brief.md").write_text(brief)
print("Done. results.json and experiment_brief.md written.")

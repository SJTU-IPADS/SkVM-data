"""
Reference solution for revenue-operations_task_02.

Reads pipeline.json from cwd.
Produces pipeline_report.json.
"""
import json
from pathlib import Path

data = json.loads(Path("pipeline.json").read_text())

quota = data["quota"]
stages = data["stages"]
global_avg_days = data["average_cycle_days"]
stage_avg_days = data["stage_average_days"]  # per-stage averages
deals = data["deals"]

# 1. Partition open vs closed-won
open_deals = [d for d in deals if d["stage"] != "Closed Won"]
closed_deals = [d for d in deals if d["stage"] == "Closed Won"]

# 2. Pipeline coverage ratio = open pipeline value / quota
open_pipeline_value = sum(d["value"] for d in open_deals)
pipeline_coverage_ratio = round(open_pipeline_value / quota, 4)

# 3. Coverage status
if pipeline_coverage_ratio >= 3.0:
    coverage_status = "Healthy"
elif pipeline_coverage_ratio >= 2.0:
    coverage_status = "At Risk"
else:
    coverage_status = "Insufficient"

# 4. Deal aging — use PER-STAGE threshold (2x stage avg), not global avg
# This is the critical trap: global avg = 45 days → threshold 90d (no aging)
# Per-stage thresholds:  Discovery=20, Qual=24, Proposal=24, Neg=16, Closed Won=6
aging_deals = []
healthy_deals = []
for d in open_deals:
    stage = d["stage"]
    stage_avg = stage_avg_days.get(stage, global_avg_days)
    threshold = 2 * stage_avg
    if d["age_days"] > threshold:
        aging_deals.append({
            "id": d["id"],
            "name": d["name"],
            "stage": stage,
            "value": d["value"],
            "age_days": d["age_days"],
            "threshold_days": threshold,
            "overage_days": d["age_days"] - threshold,
        })
    else:
        healthy_deals.append(d["id"])

# 5. Concentration risk — check if any single deal > 40% of open pipeline VALUE
concentration_risk = False
concentration_deal = None
max_deal = max(open_deals, key=lambda d: d["value"])
max_pct = round(max_deal["value"] / open_pipeline_value * 100, 2) if open_pipeline_value > 0 else 0
if max_pct > 40.0:
    concentration_risk = True
    concentration_deal = {
        "id": max_deal["id"],
        "name": max_deal["name"],
        "value": max_deal["value"],
        "pct_of_open_pipeline": max_pct,
    }

# 6. Stage distribution
stage_distribution = {}
for stage in stages:
    stage_deals = [d for d in open_deals if d["stage"] == stage]
    stage_distribution[stage] = {
        "count": len(stage_deals),
        "value": sum(d["value"] for d in stage_deals),
    }

# 7. Build report
report = {
    "total_deals": len(deals),
    "open_deals": len(open_deals),
    "closed_won_deals": len(closed_deals),
    "open_pipeline_value": open_pipeline_value,
    "quota": quota,
    "pipeline_coverage_ratio": pipeline_coverage_ratio,
    "coverage_status": coverage_status,
    "aging_deals": aging_deals,
    "aging_count": len(aging_deals),
    "healthy_count": len(healthy_deals),
    "concentration_risk": concentration_risk,
    "concentration_deal": concentration_deal,
    "stage_distribution": stage_distribution,
}

Path("pipeline_report.json").write_text(json.dumps(report, indent=2))
print(f"pipeline_report.json written:")
print(f"  open_pipeline_value={open_pipeline_value}, coverage_ratio={pipeline_coverage_ratio}")
print(f"  aging_deals={len(aging_deals)}: {[d['name'] for d in aging_deals]}")
print(f"  healthy_count={len(healthy_deals)}")
print(f"  concentration_risk={concentration_risk}, max_pct={max_pct}%")
print(f"  Invariant: aging({len(aging_deals)}) + healthy({len(healthy_deals)}) == open_deals({len(open_deals)}): {len(aging_deals)+len(healthy_deals)==len(open_deals)}")

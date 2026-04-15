"""
Deterministic fixture generator for revenue-operations_task_02.

Task: Pipeline Health Analysis with Per-Stage Aging and Concentration Risk.

Produces: fixtures/pipeline.json

Design traps:
1. Deal aging is checked against per-stage thresholds (2x stage avg), not
   the global average_cycle_days. Agents using the global avg get wrong aging flags.
2. Concentration risk fires on >40% of pipeline VALUE in a single deal,
   not >40% of deal COUNT. Agents checking count % miss this.
3. Stateful invariant: aging_deals + healthy_deals == total_deals (all deals accounted for).
4. Pipeline coverage ratio must exclude Closed Won deals from numerator
   (only open pipeline counts), which is an under-specified step.

Run: python3 _gen_fixture.py
Prints expected values to stdout for grade.py.
"""
import json
import random
from pathlib import Path

SEED = 20260412
random.seed(SEED)

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURES.mkdir(parents=True, exist_ok=True)

# Stage configuration with per-stage average cycle times
# total_cycle = 45 days (global average)
# Per-stage breakdown:
STAGES = ["Discovery", "Qualification", "Proposal", "Negotiation", "Closed Won"]
STAGE_AVG_DAYS = {
    "Discovery":     10,
    "Qualification": 12,
    "Proposal":      12,
    "Negotiation":    8,
    "Closed Won":     3,
}
GLOBAL_AVG = 45  # used in the pipeline JSON; NOT used for aging threshold

# Each stage's aging threshold = 2x stage avg
AGING_THRESHOLD = {stage: 2 * avg for stage, avg in STAGE_AVG_DAYS.items()}
# Discovery: 20d, Qualification: 24d, Proposal: 24d, Negotiation: 16d, Closed Won: 6d

QUOTA = 500000

# Design the deals carefully:
# - 1 whale deal that creates concentration risk (value > 40% of total open pipeline)
# - Several aging deals (age > 2x stage avg for their stage)
# - Some healthy deals
# - Some Closed Won (excluded from coverage ratio numerator)

deals = []
oid = [1000]

def new_deal(name, stage, value, age_days, close_date, owner):
    oid[0] += 1
    return {
        "id": f"D{oid[0]:03d}",
        "name": name,
        "stage": stage,
        "value": value,
        "age_days": age_days,
        "close_date": close_date,
        "owner": owner,
    }

# Healthy open deals (no aging)
deals.append(new_deal("Acme Corp",      "Discovery",     45000, 8,  "2025-05-15", "rep_1"))  # 8 < 20 OK
deals.append(new_deal("Beacon Inc",     "Qualification", 62000, 10, "2025-05-20", "rep_2"))  # 10 < 24 OK
deals.append(new_deal("Centurion LLC",  "Proposal",      38000, 15, "2025-06-01", "rep_1"))  # 15 < 24 OK
deals.append(new_deal("Delphi Systems", "Negotiation",   29000, 7,  "2025-04-30", "rep_3"))  # 7 < 16 OK
deals.append(new_deal("Epsilon Co",     "Qualification", 41000, 20, "2025-05-25", "rep_2"))  # 20 < 24 OK

# Whale deal — creates concentration risk (>40% of open pipeline VALUE)
# Open pipeline (non-Closed Won) value so far: 45+62+38+29+41 = 215000
# Adding 95000 → total = 310000 → whale needs > 40% of total
# Let's add whale = 220000. Then total open = 215000 + 220000 = 435000
# whale / total_open = 220000 / 435000 = 50.6% > 40% → concentration risk triggered
deals.append(new_deal("Frontier Tech",  "Proposal",      220000, 18, "2025-06-15", "rep_3"))  # 18 < 24 OK (not aging)

# Aging deals (age > 2x stage threshold)
deals.append(new_deal("Glacier Ind",    "Discovery",     32000, 25, "2025-05-30", "rep_1"))  # 25 > 20 AGING
deals.append(new_deal("Harbor Ltd",     "Negotiation",   48000, 19, "2025-04-25", "rep_2"))  # 19 > 16 AGING
deals.append(new_deal("Ironclad Corp",  "Proposal",      27000, 30, "2025-06-10", "rep_3"))  # 30 > 24 AGING

# Closed Won deals — should NOT count in open pipeline coverage
deals.append(new_deal("Jasper Energy",  "Closed Won",    75000, 2,  "2025-03-31", "rep_1"))  # closed
deals.append(new_deal("Kestrel Inc",    "Closed Won",    55000, 1,  "2025-03-15", "rep_2"))  # closed

# Compute expected outputs
open_deals = [d for d in deals if d["stage"] != "Closed Won"]
closed_deals = [d for d in deals if d["stage"] == "Closed Won"]

open_pipeline_value = sum(d["value"] for d in open_deals)
total_pipeline_value = sum(d["value"] for d in deals)  # including closed

# Pipeline coverage = open pipeline / quota
pipeline_coverage_ratio = open_pipeline_value / QUOTA

# Aging: per-stage threshold
aging_deals = [d for d in open_deals if d["age_days"] > AGING_THRESHOLD[d["stage"]]]
healthy_open_deals = [d for d in open_deals if d["age_days"] <= AGING_THRESHOLD[d["stage"]]]

# Concentration risk check (on open pipeline)
max_deal = max(open_deals, key=lambda d: d["value"])
max_concentration_pct = max_deal["value"] / open_pipeline_value * 100

# Stage distribution
from collections import Counter
stage_counts = Counter(d["stage"] for d in open_deals)
stage_values = {}
for d in open_deals:
    stage_values[d["stage"]] = stage_values.get(d["stage"], 0) + d["value"]

print("=== EXPECTED VALUES ===")
print(f"Total deals: {len(deals)}")
print(f"Open deals: {len(open_deals)}")
print(f"Closed Won deals: {len(closed_deals)}")
print(f"Open pipeline value: {open_pipeline_value}")
print(f"Total pipeline value (incl closed): {total_pipeline_value}")
print(f"Quota: {QUOTA}")
print(f"Pipeline coverage ratio: {pipeline_coverage_ratio:.4f}")
print(f"Aging deals: {len(aging_deals)} -> {[d['name'] for d in aging_deals]}")
print(f"Healthy open deals: {len(healthy_open_deals)}")
print(f"Concentration risk: max deal={max_deal['name']}, value={max_deal['value']}, pct={max_concentration_pct:.2f}%")
print(f"Aging thresholds used: {AGING_THRESHOLD}")
print(f"Stage distribution: {dict(stage_counts)}")

for d in aging_deals:
    threshold = AGING_THRESHOLD[d["stage"]]
    stage_avg = STAGE_AVG_DAYS[d["stage"]]
    print(f"  Aging: {d['name']} stage={d['stage']} age={d['age_days']} > 2x{stage_avg}={threshold}")

print(f"\nInvariant check: aging({len(aging_deals)}) + healthy({len(healthy_open_deals)}) == open_deals({len(open_deals)}): {len(aging_deals)+len(healthy_open_deals)==len(open_deals)}")

# Write pipeline.json
pipeline = {
    "quota": QUOTA,
    "stages": STAGES,
    "average_cycle_days": GLOBAL_AVG,
    "stage_average_days": STAGE_AVG_DAYS,
    "deals": deals,
}

(FIXTURES / "pipeline.json").write_text(json.dumps(pipeline, indent=2))
print(f"\nWrote fixtures/pipeline.json ({len(deals)} deals)")

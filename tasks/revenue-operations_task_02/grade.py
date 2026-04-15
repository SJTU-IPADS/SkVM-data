"""
Grade function for revenue-operations_task_02.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: direct checks on pipeline_report.json against hardcoded expected
values derived from the deterministic fixture (seed 20260412 in _gen_fixture.py).

Key expected values:
  total_deals: 11
  open_deals: 9
  closed_won_deals: 2
  open_pipeline_value: 542000
  pipeline_coverage_ratio: 1.084
  coverage_status: "Insufficient"
  aging_count: 3 (Glacier Ind, Harbor Ltd, Ironclad Corp)
  healthy_count: 6
  concentration_risk: True
  concentration_deal.name: "Frontier Tech"
  concentration_deal.pct_of_open_pipeline: ~40.59
"""
from __future__ import annotations

import json
import math
from pathlib import Path

# ---- Expected values --------------------------------------------------------

EXPECTED = {
    "total_deals": 11,
    "open_deals": 9,
    "closed_won_deals": 2,
    "open_pipeline_value": 542000,
    "pipeline_coverage_ratio": 1.084,
    "coverage_status": "Insufficient",
    "aging_count": 3,
    "healthy_count": 6,
    "aging_deal_names": {"Glacier Ind", "Harbor Ltd", "Ironclad Corp"},
    "concentration_risk": True,
    "concentration_deal_name": "Frontier Tech",
    "concentration_pct": 40.59,
}


# ---- Helpers ----------------------------------------------------------------

def _approx(a, b, rel_tol=0.005, abs_tol=0.01):
    if a is None or b is None:
        return False
    try:
        return math.isclose(float(a), float(b), rel_tol=rel_tol, abs_tol=abs_tol)
    except (TypeError, ValueError):
        return False


def _load_report(workspace_path):
    p = Path(workspace_path) / "pipeline_report.json"
    if not p.exists():
        return None, "pipeline_report.json not found"
    try:
        return json.loads(p.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"pipeline_report.json invalid JSON: {e}"


# ---- Criterion checks -------------------------------------------------------

def _check_report_exists(r):
    if r is None:
        return 0.0, "pipeline_report.json missing or unparseable"
    return 1.0, None


def _check_report_schema(r):
    if r is None:
        return 0.0, "pipeline_report.json missing"
    required = {
        "total_deals", "open_deals", "closed_won_deals", "open_pipeline_value",
        "pipeline_coverage_ratio", "coverage_status", "aging_deals",
        "aging_count", "healthy_count", "concentration_risk", "stage_distribution"
    }
    missing = required - set(r.keys())
    if missing:
        return 0.0, f"pipeline_report.json missing keys: {sorted(missing)}"
    return 1.0, None


def _check_open_vs_closed_split(r):
    """open_deals + closed_won_deals must equal total_deals, and closed_won_deals
    must equal 2 — proving that Closed Won stage is correctly excluded from the
    open pipeline. Agents who include Closed Won in open_deals get open_deals=11."""
    if r is None:
        return 0.0, "pipeline_report.json missing"
    td = r.get("total_deals")
    od = r.get("open_deals")
    cw = r.get("closed_won_deals")
    if td != EXPECTED["total_deals"]:
        return 0.0, f"total_deals: expected {EXPECTED['total_deals']}, got {td}"
    if cw != EXPECTED["closed_won_deals"]:
        return 0.0, f"closed_won_deals: expected {EXPECTED['closed_won_deals']}, got {cw}"
    if od != EXPECTED["open_deals"]:
        return 0.0, f"open_deals: expected {EXPECTED['open_deals']}, got {od}"
    if od + cw != td:
        return 0.0, f"open_deals({od}) + closed_won_deals({cw}) != total_deals({td})"
    return 1.0, None


def _check_pipeline_value(r):
    """open_pipeline_value must equal 542000 — the sum of non-Closed-Won deal values.
    Including Closed Won deals inflates this to 672000."""
    if r is None:
        return 0.0, "pipeline_report.json missing"
    got = r.get("open_pipeline_value")
    if got != EXPECTED["open_pipeline_value"]:
        return 0.0, (
            f"open_pipeline_value: expected {EXPECTED['open_pipeline_value']}, got {got}. "
            f"Closed Won deals ({EXPECTED['closed_won_deals']}) must be excluded from pipeline value."
        )
    return 1.0, None


def _check_coverage_ratio(r):
    """Pipeline coverage ratio = open_pipeline_value / quota = 542000/500000 = 1.084.
    Agents including Closed Won get 672000/500000 = 1.344."""
    if r is None:
        return 0.0, "pipeline_report.json missing"
    got = r.get("pipeline_coverage_ratio")
    if not _approx(got, EXPECTED["pipeline_coverage_ratio"], rel_tol=0.005, abs_tol=0.005):
        return 0.0, f"pipeline_coverage_ratio: expected ~{EXPECTED['pipeline_coverage_ratio']}, got {got}"
    return 1.0, None


def _check_coverage_status(r):
    """coverage_status must be 'Insufficient' because ratio 1.084 < 2.0.
    Healthy requires ≥3x quota; At Risk requires ≥2x; Insufficient is < 2x."""
    if r is None:
        return 0.0, "pipeline_report.json missing"
    got = str(r.get("coverage_status", "")).lower()
    if "insufficient" not in got:
        return 0.0, f"coverage_status: expected 'Insufficient' (ratio 1.084 < 2.0), got {r.get('coverage_status')!r}"
    return 1.0, None


def _check_aging_count(r):
    """Exactly 3 deals are aging (age > 2x stage average cycle time).
    Using per-stage thresholds: Discovery=20d, Qualification=24d, Proposal=24d,
    Negotiation=16d. Agents who use the global average_cycle_days (45d, threshold 90d)
    find ZERO aging deals because no deal exceeds 90 days."""
    if r is None:
        return 0.0, "pipeline_report.json missing"
    got = r.get("aging_count")
    if got != EXPECTED["aging_count"]:
        return 0.0, (
            f"aging_count: expected {EXPECTED['aging_count']}, got {got}. "
            f"Aging must use per-stage average (2x stage avg), not the global average_cycle_days."
        )
    return 1.0, None


def _check_aging_identities(r):
    """The three aging deals must be Glacier Ind (Discovery, 25d > 20d threshold),
    Harbor Ltd (Negotiation, 19d > 16d threshold), and Ironclad Corp (Proposal, 30d > 24d threshold).
    Each deal's threshold is 2x its stage-specific average, not the global average."""
    if r is None:
        return 0.0, "pipeline_report.json missing"
    aging = r.get("aging_deals") or []
    if not isinstance(aging, list):
        return 0.0, "aging_deals is not a list"
    got_names = {d.get("name") for d in aging if isinstance(d, dict)}
    expected = EXPECTED["aging_deal_names"]
    missing = expected - got_names
    extra = got_names - expected
    if missing or extra:
        problems = []
        if missing: problems.append(f"missing: {missing}")
        if extra: problems.append(f"extra: {extra}")
        return 0.0, f"aging deal names wrong — {'; '.join(problems)}"
    # Each entry should have threshold_days field showing per-stage threshold was applied
    for d in aging:
        if "threshold_days" not in d:
            return 0.0, f"aging deal entry {d.get('name')!r} missing 'threshold_days' field"
    return 1.0, None


def _check_aging_healthy_invariant(r):
    """aging_count + healthy_count must equal open_deals — every open deal is
    accounted for as either aging or healthy, with no double-counting."""
    if r is None:
        return 0.0, "pipeline_report.json missing"
    aging = r.get("aging_count")
    healthy = r.get("healthy_count")
    open_d = r.get("open_deals")
    try:
        if int(aging) + int(healthy) != int(open_d):
            return 0.0, f"aging_count({aging}) + healthy_count({healthy}) != open_deals({open_d})"
    except (TypeError, ValueError):
        return 0.0, f"non-integer counts: aging={aging}, healthy={healthy}, open_deals={open_d}"
    return 1.0, None


def _check_concentration_risk_flag(r):
    """concentration_risk must be True because Frontier Tech (220000) represents
    40.59% of open pipeline value (542000), which exceeds the 40% threshold.
    Agents who compute concentration as a fraction of deal COUNT (1/9 = 11%) miss this."""
    if r is None:
        return 0.0, "pipeline_report.json missing"
    got = r.get("concentration_risk")
    if got is not True and str(got).lower() != "true":
        return 0.0, (
            f"concentration_risk: expected True (Frontier Tech = 40.59% of open pipeline value > 40% threshold), "
            f"got {got!r}. Concentration is measured as % of total open pipeline VALUE, not deal count."
        )
    return 1.0, None


def _check_concentration_deal(r):
    """concentration_deal must identify Frontier Tech with pct_of_open_pipeline ≈ 40.59%.
    The deal's percentage must reflect its share of OPEN pipeline value (not total including closed)."""
    if r is None:
        return 0.0, "pipeline_report.json missing"
    cd = r.get("concentration_deal")
    if not cd or not isinstance(cd, dict):
        return 0.0, "concentration_deal missing or not an object"
    name = cd.get("name", "")
    if "Frontier" not in name and "frontier" not in name.lower():
        return 0.0, f"concentration_deal.name: expected 'Frontier Tech', got {name!r}"
    pct = cd.get("pct_of_open_pipeline")
    if not _approx(pct, EXPECTED["concentration_pct"], rel_tol=0.01, abs_tol=0.5):
        return 0.0, (
            f"concentration_deal.pct_of_open_pipeline: expected ~{EXPECTED['concentration_pct']}%, "
            f"got {pct}% — must be computed as deal_value/open_pipeline_value*100"
        )
    return 1.0, None


def _check_stage_distribution_keys(r):
    """stage_distribution must include all 5 pipeline stages as keys (including
    Closed Won with count=0, value=0 for completeness). Missing stages indicate
    the agent filtered out stages instead of classifying them."""
    if r is None:
        return 0.0, "pipeline_report.json missing"
    sd = r.get("stage_distribution") or {}
    expected_stages = {"Discovery", "Qualification", "Proposal", "Negotiation", "Closed Won"}
    present = set(sd.keys())
    missing = expected_stages - present
    if missing:
        return 0.0, f"stage_distribution missing stages: {sorted(missing)}"
    return 1.0, None


# ---- Criterion registry -----------------------------------------------------

CRITERIA = [
    {
        "id": "report-exists",
        "weight": 0.03,
        "description": "pipeline_report.json exists at the workspace root and parses as valid JSON.",
        "check": _check_report_exists,
    },
    {
        "id": "report-schema",
        "weight": 0.05,
        "description": "pipeline_report.json contains all required top-level keys: total_deals, open_deals, closed_won_deals, open_pipeline_value, pipeline_coverage_ratio, coverage_status, aging_deals, aging_count, healthy_count, concentration_risk, stage_distribution.",
        "check": _check_report_schema,
    },
    {
        "id": "open-closed-split",
        "weight": 0.09,
        "description": "Closed Won deals (2) are correctly separated from open deals (9), and open_deals + closed_won_deals == total_deals. Agents who treat Closed Won as open inflate open_deals to 11.",
        "check": _check_open_vs_closed_split,
    },
    {
        "id": "pipeline-value",
        "weight": 0.09,
        "description": "open_pipeline_value equals 542000 — sum of non-Closed-Won deal values only. Including the two Closed Won deals inflates this to 672000 and cascades through coverage ratio and concentration risk.",
        "check": _check_pipeline_value,
    },
    {
        "id": "coverage-ratio",
        "weight": 0.09,
        "description": "pipeline_coverage_ratio equals ~1.084 (open pipeline 542000 / quota 500000). Using total pipeline including Closed Won gives 1.344.",
        "check": _check_coverage_ratio,
    },
    {
        "id": "coverage-status",
        "weight": 0.05,
        "description": "coverage_status is 'Insufficient' because ratio 1.084 falls below the 2.0x threshold. Healthy requires ≥3x, At Risk requires ≥2x, Insufficient is <2x.",
        "check": _check_coverage_status,
    },
    {
        "id": "aging-count",
        "weight": 0.16,
        "description": "aging_count equals 3, using 2x per-stage average as the threshold (Discovery=20d, Qualification=24d, Proposal=24d, Negotiation=16d). Using the global average_cycle_days (45d) yields threshold 90d and finds zero aging deals.",
        "check": _check_aging_count,
    },
    {
        "id": "aging-identities",
        "weight": 0.14,
        "description": "The three aging deals are exactly Glacier Ind (Discovery, 25d > 20d), Harbor Ltd (Negotiation, 19d > 16d), and Ironclad Corp (Proposal, 30d > 24d). Each aging entry must include threshold_days showing the per-stage threshold applied.",
        "check": _check_aging_identities,
    },
    {
        "id": "aging-healthy-invariant",
        "weight": 0.07,
        "description": "aging_count + healthy_count == open_deals (3 + 6 = 9). Every open deal must be classified as either aging or healthy with no double-counting or omissions.",
        "check": _check_aging_healthy_invariant,
    },
    {
        "id": "concentration-risk-flag",
        "weight": 0.12,
        "description": "concentration_risk is True because Frontier Tech represents 40.59% of open pipeline VALUE, exceeding the 40% threshold. Agents measuring concentration as % of deal COUNT (1/9 = 11%) incorrectly report False.",
        "check": _check_concentration_risk_flag,
    },
    {
        "id": "concentration-deal",
        "weight": 0.08,
        "description": "concentration_deal identifies Frontier Tech with pct_of_open_pipeline ≈ 40.59%, computed as deal_value / open_pipeline_value * 100. Using total pipeline (including Closed Won) gives 32.7% which is below the 40% trigger.",
        "check": _check_concentration_deal,
    },
    {
        "id": "stage-distribution-keys",
        "weight": 0.03,
        "description": "stage_distribution includes all 5 pipeline stages as keys, including Closed Won (with count=0, value=0), confirming that closed deals were recognized but excluded from open pipeline metrics.",
        "check": _check_stage_distribution_keys,
    },
]

# Sanity check
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    report, _ = _load_report(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](report)
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

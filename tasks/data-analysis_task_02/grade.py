"""
grade.py for data-analysis_task_02: A/B Test Experiment Analysis

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Trap archetypes hit:
1. Under-specified step (arch 1): device_type segmentation protocol with per-device CVR lift
2. Common-default-wrong (arch 2): percentages without underlying counts in brief
3. Known-edge-case (arch 4): multiple comparisons must be noted in brief caveats
4. Stateful invariant (arch 5): control_users + treatment_users == valid_users

Expected values hardcoded from _gen_fixture.py (seed 20260412).
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path


# ---- Expected values (from _gen_fixture.py seed 20260412) -------------------

EXPECTED = {
    "input_rows": 1180,
    "valid_users": 1100,
    "control_users": 550,
    "treatment_users": 550,
    "excluded_contaminated_rows": 50,
    "excluded_bad_date": 18,
    "excluded_bad_revenue": 12,
    "overall_control_cvr": 0.136364,
    "overall_treatment_cvr": 0.174545,
    "overall_control_arpu": 5.9334,
    "overall_treatment_arpu": 7.3644,
    "overall_cvr_lift_pp": 0.038181,
    "overall_cvr_lift_pct": 28.0,
    "by_device": {
        "mobile": {
            "control_n": 311,
            "treatment_n": 321,
            "control_cvr": 0.109325,
            "treatment_cvr": 0.17134,
            "cvr_lift_pp": 0.062015,
            "cvr_lift_pct": 56.73,
        },
        "desktop": {
            "control_n": 239,
            "treatment_n": 229,
            "control_cvr": 0.171548,
            "treatment_cvr": 0.179039,
            "cvr_lift_pp": 0.007491,
            "cvr_lift_pct": 4.37,
        },
    },
}

REQUIRED_RESULTS_KEYS = {
    "input_rows", "valid_users", "control_users", "treatment_users",
    "overall", "by_device",
}

REQUIRED_BRIEF_SECTIONS = {"answer", "evidence", "confidence", "caveats", "next action"}


# ---- Helpers -----------------------------------------------------------------

def _approx(a, b, tol_abs=0.005, tol_rel=0.005):
    """Loose numeric equality for rates (CVR) and lifts."""
    if a is None or b is None:
        return False
    try:
        return math.isclose(float(a), float(b), abs_tol=tol_abs, rel_tol=tol_rel)
    except (TypeError, ValueError):
        return False


def _approx_pct(a, b, tol_abs=2.0, tol_rel=0.05):
    """Looser check for lift percentages (allow ±2pp or 5% relative)."""
    if a is None or b is None:
        return False
    try:
        return math.isclose(float(a), float(b), abs_tol=tol_abs, rel_tol=tol_rel)
    except (TypeError, ValueError):
        return False


def _load_results(workspace_path: str):
    path = Path(workspace_path) / "results.json"
    if not path.exists():
        return None, "results.json not found in workspace"
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"results.json not valid JSON: {e}"


def _load_brief(workspace_path: str):
    path = Path(workspace_path) / "experiment_brief.md"
    if not path.exists():
        return None, "experiment_brief.md not found in workspace"
    return path.read_text(), None


# ---- Per-criterion checks ----------------------------------------------------

def _check_results_exists(results, brief):
    if results is None:
        return 0.0, "results.json missing or unparseable"
    return 1.0, None


def _check_results_schema(results, brief):
    if results is None:
        return 0.0, "results.json missing"
    missing = REQUIRED_RESULTS_KEYS - set(results.keys())
    if missing:
        return 0.0, f"results.json missing keys: {sorted(missing)}"
    # Check overall has control and treatment sub-dicts
    overall = results.get("overall", {})
    if not isinstance(overall, dict):
        return 0.0, "overall is not an object"
    if "control" not in overall or "treatment" not in overall:
        return 0.0, f"overall missing 'control' or 'treatment' sub-keys; got: {list(overall.keys())}"
    # Check by_device has mobile and desktop
    bd = results.get("by_device", {})
    if not isinstance(bd, dict):
        return 0.0, "by_device is not an object"
    if "mobile" not in bd or "desktop" not in bd:
        return 0.0, f"by_device missing 'mobile' or 'desktop' keys; got: {list(bd.keys())}"
    return 1.0, None


def _check_input_rows(results, brief):
    if results is None:
        return 0.0, "results.json missing"
    got = results.get("input_rows")
    if got != EXPECTED["input_rows"]:
        return 0.0, f"input_rows: expected {EXPECTED['input_rows']}, got {got}"
    return 1.0, None


def _check_valid_users(results, brief):
    if results is None:
        return 0.0, "results.json missing"
    got = results.get("valid_users")
    if got != EXPECTED["valid_users"]:
        return 0.0, f"valid_users: expected {EXPECTED['valid_users']}, got {got}"
    return 1.0, None


def _check_user_split_invariant(results, brief):
    """control_users + treatment_users == valid_users (stateful invariant)."""
    if results is None:
        return 0.0, "results.json missing"
    try:
        cu = int(results.get("control_users"))
        tu = int(results.get("treatment_users"))
        vu = int(results.get("valid_users"))
    except (TypeError, ValueError):
        return 0.0, "control_users/treatment_users/valid_users not integers"
    if cu + tu != vu:
        return 0.0, f"Invariant broken: control_users ({cu}) + treatment_users ({tu}) != valid_users ({vu})"
    if cu != EXPECTED["control_users"]:
        return 0.0, f"control_users: expected {EXPECTED['control_users']}, got {cu}"
    if tu != EXPECTED["treatment_users"]:
        return 0.0, f"treatment_users: expected {EXPECTED['treatment_users']}, got {tu}"
    return 1.0, None


def _check_contamination_exclusion(results, brief):
    """Agent must exclude all rows for users appearing in both arms."""
    if results is None:
        return 0.0, "results.json missing"
    # Accept either excluded_contaminated_rows or a count on contaminated_users (25 users = 50 rows)
    # We check valid_users == 1100 which can only be achieved by correct exclusion
    vu = results.get("valid_users")
    if vu != EXPECTED["valid_users"]:
        return 0.0, (
            f"valid_users={vu} != {EXPECTED['valid_users']}; likely contaminated users were not fully excluded "
            f"(25 users each appear in both control and treatment — all their rows must be dropped)"
        )
    # Optionally check the excluded_contaminated_rows field if present
    excl = results.get("excluded_contaminated_rows")
    if excl is not None and int(excl) != EXPECTED["excluded_contaminated_rows"]:
        return 0.0, (
            f"excluded_contaminated_rows={excl}, expected {EXPECTED['excluded_contaminated_rows']} "
            f"(25 contaminated users × 2 rows each)"
        )
    return 1.0, None


def _check_overall_cvr(results, brief):
    """Overall CVR values for control and treatment must be correct."""
    if results is None:
        return 0.0, "results.json missing"
    overall = results.get("overall") or {}
    ctrl = overall.get("control") or {}
    trt = overall.get("treatment") or {}
    problems = []
    ctrl_cvr = ctrl.get("cvr")
    trt_cvr = trt.get("cvr")
    if not _approx(ctrl_cvr, EXPECTED["overall_control_cvr"]):
        problems.append(f"control CVR: expected ~{EXPECTED['overall_control_cvr']:.4f}, got {ctrl_cvr}")
    if not _approx(trt_cvr, EXPECTED["overall_treatment_cvr"]):
        problems.append(f"treatment CVR: expected ~{EXPECTED['overall_treatment_cvr']:.4f}, got {trt_cvr}")
    if problems:
        return 0.0, "; ".join(problems)
    return 1.0, None


def _check_device_segmentation(results, brief):
    """by_device must report per-device CVR for both control and treatment with correct values."""
    if results is None:
        return 0.0, "results.json missing"
    bd = results.get("by_device") or {}
    problems = []
    for dev in ["mobile", "desktop"]:
        dev_data = bd.get(dev) or {}
        exp = EXPECTED["by_device"][dev]
        # Check control and treatment sub-objects exist
        ctrl = dev_data.get("control") or {}
        trt = dev_data.get("treatment") or {}
        if not ctrl and not trt:
            problems.append(f"{dev}: missing control/treatment sub-objects")
            continue
        ctrl_cvr = ctrl.get("cvr")
        trt_cvr = trt.get("cvr")
        if not _approx(ctrl_cvr, exp["control_cvr"], tol_abs=0.01):
            problems.append(f"{dev} control CVR: expected ~{exp['control_cvr']:.4f}, got {ctrl_cvr}")
        if not _approx(trt_cvr, exp["treatment_cvr"], tol_abs=0.01):
            problems.append(f"{dev} treatment CVR: expected ~{exp['treatment_cvr']:.4f}, got {trt_cvr}")
    if problems:
        return 0.0, "; ".join(problems)
    return 1.0, None


def _check_device_lift(results, brief):
    """CVR lift per device must be computed (absolute pp and/or relative %) and present in results or brief."""
    if results is None:
        return 0.0, "results.json missing"
    bd = results.get("by_device") or {}
    problems = []
    for dev in ["mobile", "desktop"]:
        dev_data = bd.get(dev) or {}
        exp = EXPECTED["by_device"][dev]
        # Accept lift stored either as cvr_lift_pp or derivable from control/treatment CVR
        lift_pp = dev_data.get("cvr_lift_pp")
        lift_pct = dev_data.get("cvr_lift_pct")
        # If lift_pp not present, try to derive from control/treatment
        if lift_pp is None:
            ctrl = dev_data.get("control") or {}
            trt = dev_data.get("treatment") or {}
            c = ctrl.get("cvr")
            t = trt.get("cvr")
            if c is not None and t is not None:
                try:
                    lift_pp = float(t) - float(c)
                except (TypeError, ValueError):
                    pass
        if lift_pp is None:
            problems.append(f"{dev}: cvr_lift_pp not present and cannot be derived")
            continue
        if not _approx(lift_pp, exp["cvr_lift_pp"], tol_abs=0.015, tol_rel=0.1):
            problems.append(f"{dev} CVR lift pp: expected ~{exp['cvr_lift_pp']:.4f}, got {lift_pp}")
    if problems:
        return 0.0, "; ".join(problems)
    return 1.0, None


def _check_brief_exists(results, brief):
    if brief is None:
        return 0.0, "experiment_brief.md not found"
    if len(brief.strip()) < 50:
        return 0.0, f"experiment_brief.md is too short ({len(brief.strip())} chars)"
    return 1.0, None


def _check_brief_sections(results, brief):
    if brief is None:
        return 0.0, "experiment_brief.md not found"
    headers = [h.strip().lower().rstrip(":") for h in re.findall(r"^\s*#{1,6}\s*(.+?)\s*$", brief, re.MULTILINE)]
    missing = [req for req in REQUIRED_BRIEF_SECTIONS if not any(req in h for h in headers)]
    if missing:
        return 0.0, f"missing sections: {missing}; found: {headers}"
    return 1.0, None


def _check_brief_counts_with_percentages(results, brief):
    """Every percentage in the brief must be accompanied by its raw count on the same or adjacent line."""
    if brief is None:
        return 0.0, "experiment_brief.md not found"
    pct_re = re.compile(r"(\d+(?:\.\d+)?)\s*%")
    lines = brief.splitlines()
    violations = []
    count_patterns = [
        re.compile(r"\d+\s*(?:of|/)\s*\d+"),
        re.compile(r"n\s*=\s*\d+", re.IGNORECASE),
        re.compile(r"\(\s*\d+\s*\)", re.IGNORECASE),  # e.g. (34)
    ]
    for i, line in enumerate(lines):
        if not pct_re.search(line):
            continue
        window = "\n".join(lines[max(0, i - 1):min(len(lines), i + 2)])
        if not any(p.search(window) for p in count_patterns):
            violations.append(f"line {i+1}: {line.strip()[:80]!r}")
    if violations:
        return 0.0, f"percentage without raw count in {len(violations)} line(s); first: {violations[0]}"
    return 1.0, None


def _check_brief_multiple_comparisons(results, brief):
    """Caveats section must note the multiple comparisons issue (testing CVR and ARPU simultaneously)."""
    if brief is None:
        return 0.0, "experiment_brief.md not found"
    m = re.search(
        r"#{1,6}\s*caveats?\b.*?\n(.*?)(?=\n\s*#{1,6}\s|\Z)",
        brief,
        re.IGNORECASE | re.DOTALL,
    )
    if not m:
        return 0.0, "no Caveats section found"
    body = m.group(1).lower()
    # Look for keywords indicating awareness of multiple comparisons
    mc_keywords = [
        "multiple comparison", "bonferroni", "false positive", "type i", "fdr",
        "correction", "multiple test", "two metric", "2 metric", "two metrics",
    ]
    if not any(kw in body for kw in mc_keywords):
        return 0.0, (
            f"Caveats section does not mention multiple comparisons or correction for testing "
            f"multiple metrics simultaneously. Body: {m.group(1).strip()[:200]!r}"
        )
    return 1.0, None


def _check_brief_uncertainty(results, brief):
    """Confidence section must express uncertainty as a range or caveat keyword."""
    if brief is None:
        return 0.0, "experiment_brief.md not found"
    m = re.search(
        r"#{1,6}\s*confidence\b.*?\n(.*?)(?=\n\s*#{1,6}\s|\Z)",
        brief,
        re.IGNORECASE | re.DOTALL,
    )
    if not m:
        return 0.0, "no Confidence section body found"
    body = m.group(1).strip()
    if not body:
        return 0.0, "Confidence section is empty"
    has_range = bool(re.search(r"\d+(\.\d+)?\s*(?:-|to|\u2013|\u2014|\u00b1|\+/-)\s*\d+", body, re.IGNORECASE))
    has_caveat = bool(
        re.search(
            r"\b(range|interval|uncertain(?:ty)?|approximate|roughly|estimate|ci\b|n\s*=|small sample|confidence interval)\b",
            body, re.IGNORECASE,
        )
    )
    if not (has_range or has_caveat):
        return 0.0, f"Confidence section does not express uncertainty: {body[:120]!r}"
    return 1.0, None


# ---- Criterion registry ------------------------------------------------------

CRITERIA = [
    {
        "id": "results-exists",
        "weight": 0.04,
        "description": "results.json exists at the workspace root and parses as valid JSON.",
        "check": _check_results_exists,
    },
    {
        "id": "results-schema",
        "weight": 0.06,
        "description": "results.json contains all required top-level keys (input_rows, valid_users, control_users, treatment_users, overall, by_device) and overall/by_device have the expected sub-structure.",
        "check": _check_results_schema,
    },
    {
        "id": "input-rows",
        "weight": 0.04,
        "description": "input_rows in results.json equals 1180 — the total row count of experiment_log.csv before any exclusion, proving the agent counted raw input first.",
        "check": _check_input_rows,
    },
    {
        "id": "valid-users",
        "weight": 0.04,
        "description": "valid_users equals 1100 after excluding contaminated, out-of-window, and bad-revenue rows — the correct post-cleaning denominator for the experiment.",
        "check": _check_valid_users,
    },
    {
        "id": "user-split-invariant",
        "weight": 0.10,
        "description": "control_users + treatment_users == valid_users (stateful invariant) AND each arm has exactly 550 valid users — this invariant breaks if any exclusion step is applied to one arm only.",
        "check": _check_user_split_invariant,
    },
    {
        "id": "contamination-exclusion",
        "weight": 0.10,
        "description": "All 50 rows belonging to the 25 contaminated users (those appearing in both control and treatment) are fully excluded; including any of these rows inflates treatment conversion rates because the contaminated users disproportionately show converted=True in treatment.",
        "check": _check_contamination_exclusion,
    },
    {
        "id": "overall-cvr",
        "weight": 0.10,
        "description": "Overall CVR for control (~13.6%) and treatment (~17.5%) in results.json.overall are correct — deviations indicate wrong exclusion logic or miscounting converted users.",
        "check": _check_overall_cvr,
    },
    {
        "id": "device-segmentation",
        "weight": 0.16,
        "description": "results.json.by_device contains mobile and desktop segments each with control and treatment CVR values matching the fixture (mobile control ~10.9%, mobile treatment ~17.1%, desktop control ~17.2%, desktop treatment ~17.9%) — this is the pinned segmentation protocol the prompt requires.",
        "check": _check_device_segmentation,
    },
    {
        "id": "device-lift",
        "weight": 0.10,
        "description": "Per-device CVR lift (treatment minus control, absolute pp) is computed and stored in results.json — mobile lift ~+6.2 pp, desktop lift ~+0.75 pp; the large mobile/desktop asymmetry is the key analytical finding.",
        "check": _check_device_lift,
    },
    {
        "id": "brief-exists",
        "weight": 0.03,
        "description": "experiment_brief.md exists at the workspace root and contains non-trivial content.",
        "check": _check_brief_exists,
    },
    {
        "id": "brief-sections",
        "weight": 0.05,
        "description": "experiment_brief.md has all five required markdown sections: Answer, Evidence, Confidence, Caveats, Next Action.",
        "check": _check_brief_sections,
    },
    {
        "id": "brief-counts-with-percentages",
        "weight": 0.05,
        "description": "Every percentage in experiment_brief.md is accompanied by its raw count on the same or adjacent line (e.g. '13.6% (75 of 550)') — enforcing the rule that percentages without underlying counts mislead stakeholders about sample sizes.",
        "check": _check_brief_counts_with_percentages,
    },
    {
        "id": "brief-multiple-comparisons",
        "weight": 0.10,
        "description": "The Caveats section of experiment_brief.md explicitly notes that testing two metrics (CVR and ARPU) simultaneously creates a multiple-comparisons problem, and mentions correction (Bonferroni, FDR) or labels results as exploratory — this is the known failure mode the skill documents.",
        "check": _check_brief_multiple_comparisons,
    },
    {
        "id": "brief-uncertainty",
        "weight": 0.03,
        "description": "The Confidence section expresses uncertainty as a range or uses an explicit caveat keyword (range, interval, approximately, CI, n=) rather than presenting only a point estimate.",
        "check": _check_brief_uncertainty,
    },
]

# Sanity-check at import time
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    results, _ = _load_results(workspace_path)
    brief, _ = _load_brief(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](results, brief)
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

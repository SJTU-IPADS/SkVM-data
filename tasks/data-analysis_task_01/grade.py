"""
Grade function for data-analysis_task_03.

Contract: returns a list of criterion records per docs/skvm/grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: direct checks (no bun test, no JUnit). We parse analysis.json and
decision_brief.md from the workspace, compare against known-good values
computed from the deterministic fixture (_gen_fixture.py seed 20260412).

Expected values are hardcoded here — the fixture is a static file and the
generator is committed for reproducibility, but grade.py does NOT re-run
the generator because the fixture in the workspace may have been consumed
or renamed by the model.
"""
from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path


# ---- Expected values from _gen_fixture.py (seed 20260412) ------------------

EXPECTED = {
    "input_rows": 180,
    "accepted": 120,
    "rejected": 60,
    "rejection_reasons": {
        "bad_date": 9,
        "bad_amount": 8,
        "pending": 8,
        "returned": 10,
        "out_of_window": 15,
        "duplicate": 10,
    },
    "monthly_revenue": {
        "2025-07": 22471.36,
        "2025-08": 18425.04,
        "2025-09": 20468.40,
    },
    "q3_revenue_total": 61364.80,
    "top_region_name": "west",
    "top_region_count": 28,
    "top_region_revenue": 14460.62,
    "customer_count": 55,
}

REQUIRED_JSON_KEYS = {
    "input_rows", "accepted", "rejected", "rejection_reasons",
    "monthly_revenue", "top_region", "customer_count", "q3_revenue_total",
}

REQUIRED_BRIEF_SECTIONS = {
    "answer", "evidence", "confidence", "caveats", "next action",
}

REJECTION_CATEGORIES = {"bad_date", "bad_amount", "pending", "returned", "out_of_window", "duplicate"}


# ---- Helpers ---------------------------------------------------------------

def _approx(a: float, b: float, tol_abs: float = 0.02, tol_rel: float = 0.001) -> bool:
    if a is None or b is None:
        return False
    try:
        return math.isclose(float(a), float(b), abs_tol=tol_abs, rel_tol=tol_rel)
    except (TypeError, ValueError):
        return False


def _load_json(workspace_path: str) -> tuple[dict | None, str | None]:
    path = Path(workspace_path) / "analysis.json"
    if not path.exists():
        return None, "analysis.json not found in workspace"
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"analysis.json not valid JSON: {e}"


def _load_brief(workspace_path: str) -> tuple[str | None, str | None]:
    path = Path(workspace_path) / "decision_brief.md"
    if not path.exists():
        return None, "decision_brief.md not found in workspace"
    return path.read_text(), None


# ---- Per-criterion checks -------------------------------------------------
# Each check takes (analysis, brief) and returns (score, details_or_none).
# `analysis` may be None if JSON failed to load; `brief` likewise.

def _check_json_exists(analysis, brief):
    if analysis is None:
        return 0.0, "analysis.json missing or unparseable"
    return 1.0, None


def _check_json_schema(analysis, brief):
    if analysis is None:
        return 0.0, "analysis.json missing"
    missing = REQUIRED_JSON_KEYS - set(analysis.keys())
    if missing:
        return 0.0, f"analysis.json missing keys: {sorted(missing)}"
    return 1.0, None


def _check_input_rows(analysis, brief):
    if analysis is None:
        return 0.0, "analysis.json missing"
    got = analysis.get("input_rows")
    if got != EXPECTED["input_rows"]:
        return 0.0, f"input_rows: expected {EXPECTED['input_rows']}, got {got}"
    return 1.0, None


def _check_count_invariant(analysis, brief):
    if analysis is None:
        return 0.0, "analysis.json missing"
    try:
        accepted = int(analysis.get("accepted"))
        rejected = int(analysis.get("rejected"))
        input_rows = int(analysis.get("input_rows"))
    except (TypeError, ValueError):
        return 0.0, "accepted/rejected/input_rows not integers"
    if accepted + rejected != input_rows:
        return 0.0, f"accepted ({accepted}) + rejected ({rejected}) != input_rows ({input_rows})"
    return 1.0, None


def _check_rejection_categories(analysis, brief):
    if analysis is None:
        return 0.0, "analysis.json missing"
    rr = analysis.get("rejection_reasons")
    if not isinstance(rr, dict):
        return 0.0, "rejection_reasons is not an object"
    missing = REJECTION_CATEGORIES - set(rr.keys())
    if missing:
        return 0.0, f"missing rejection categories: {sorted(missing)}"
    wrong = []
    for cat, want in EXPECTED["rejection_reasons"].items():
        got = rr.get(cat)
        try:
            got_int = int(got)
        except (TypeError, ValueError):
            wrong.append(f"{cat}: non-integer value {got!r}")
            continue
        if got_int != want:
            wrong.append(f"{cat}: expected {want}, got {got_int}")
    if wrong:
        return 0.0, "; ".join(wrong)
    return 1.0, None


def _check_accepted_count(analysis, brief):
    if analysis is None:
        return 0.0, "analysis.json missing"
    got = analysis.get("accepted")
    if got != EXPECTED["accepted"]:
        return 0.0, f"accepted: expected {EXPECTED['accepted']}, got {got}"
    return 1.0, None


def _check_dedup_first_occurrence(analysis, brief):
    # The only observable signal in analysis.json for first-occurrence semantics
    # is that `duplicate` count matches the 10 duplicates in the fixture AND
    # the accepted count lands at exactly 120. A later-occurrence rule would
    # produce the same duplicate count but a different monthly_revenue total
    # (because the kept row's amount differs). We already check monthly_revenue
    # separately, so here we re-check the specific duplicate count + that
    # rejection_reasons accounts for it. This criterion intentionally overlaps
    # with rejection-categories; its description is first-occurrence-specific
    # so the jit-optimize optimizer sees the rule stated plainly.
    if analysis is None:
        return 0.0, "analysis.json missing"
    rr = analysis.get("rejection_reasons") or {}
    dup = rr.get("duplicate")
    try:
        dup_int = int(dup)
    except (TypeError, ValueError):
        return 0.0, f"rejection_reasons.duplicate not an integer: {dup!r}"
    if dup_int != EXPECTED["rejection_reasons"]["duplicate"]:
        return 0.0, (
            f"expected 10 duplicate rejections (first-occurrence dedup by order_id); "
            f"got {dup_int}"
        )
    return 1.0, None


def _check_q3_revenue_total(analysis, brief):
    if analysis is None:
        return 0.0, "analysis.json missing"
    got = analysis.get("q3_revenue_total")
    if not _approx(got, EXPECTED["q3_revenue_total"]):
        return 0.0, f"q3_revenue_total: expected {EXPECTED['q3_revenue_total']}, got {got}"
    return 1.0, None


def _check_monthly_revenue(analysis, brief):
    if analysis is None:
        return 0.0, "analysis.json missing"
    mr = analysis.get("monthly_revenue")
    if not isinstance(mr, dict):
        return 0.0, "monthly_revenue is not an object"
    expected_keys = set(EXPECTED["monthly_revenue"].keys())
    got_keys = set(mr.keys())
    if expected_keys - got_keys:
        return 0.0, f"missing monthly keys: {sorted(expected_keys - got_keys)}"
    problems = []
    for k, want in EXPECTED["monthly_revenue"].items():
        if not _approx(mr.get(k), want):
            problems.append(f"{k}: expected {want}, got {mr.get(k)}")
    # Cross-invariant: sum(monthly_revenue) == q3_revenue_total
    try:
        total = sum(float(v) for v in mr.values())
    except (TypeError, ValueError):
        return 0.0, "monthly_revenue values not numeric"
    if not _approx(total, EXPECTED["q3_revenue_total"], tol_abs=0.05):
        problems.append(f"sum(monthly_revenue)={total:.2f} != q3_revenue_total={EXPECTED['q3_revenue_total']}")
    if problems:
        return 0.0, "; ".join(problems)
    return 1.0, None


def _check_top_region(analysis, brief):
    if analysis is None:
        return 0.0, "analysis.json missing"
    tr = analysis.get("top_region")
    if not isinstance(tr, dict):
        return 0.0, "top_region is not an object"
    name = tr.get("name")
    count = tr.get("count")
    rev = tr.get("revenue")
    if name != EXPECTED["top_region_name"]:
        return 0.0, f"top_region.name: expected {EXPECTED['top_region_name']!r}, got {name!r}"
    if count != EXPECTED["top_region_count"]:
        return 0.0, f"top_region.count: expected {EXPECTED['top_region_count']}, got {count}"
    if not _approx(rev, EXPECTED["top_region_revenue"]):
        return 0.0, f"top_region.revenue: expected {EXPECTED['top_region_revenue']}, got {rev}"
    return 1.0, None


def _check_customer_count(analysis, brief):
    if analysis is None:
        return 0.0, "analysis.json missing"
    got = analysis.get("customer_count")
    if got != EXPECTED["customer_count"]:
        return 0.0, f"customer_count: expected {EXPECTED['customer_count']}, got {got}"
    return 1.0, None


def _check_brief_exists(analysis, brief):
    if brief is None:
        return 0.0, "decision_brief.md not found"
    if len(brief.strip()) < 50:
        return 0.0, f"decision_brief.md is too short ({len(brief.strip())} chars)"
    return 1.0, None


def _check_brief_sections(analysis, brief):
    if brief is None:
        return 0.0, "decision_brief.md not found"
    headers = [h.strip().lower().rstrip(":") for h in re.findall(r"^\s*#{1,6}\s*(.+?)\s*$", brief, re.MULTILINE)]
    header_text = " | ".join(headers)
    missing = []
    for required in REQUIRED_BRIEF_SECTIONS:
        if not any(required in h for h in headers):
            missing.append(required)
    if missing:
        return 0.0, f"decision_brief.md missing sections: {missing}; found headers: {header_text!r}"
    return 1.0, None


def _check_brief_counts_with_percentages(analysis, brief):
    if brief is None:
        return 0.0, "decision_brief.md not found"
    # Find percentages like "62%", "62.5%", "62 %"
    pct_re = re.compile(r"(\d+(?:\.\d+)?)\s*%")
    percentages = pct_re.findall(brief)
    if not percentages:
        return 0.0, "no percentages found in decision_brief.md — rule says present counts with %"
    # For each percentage we require a raw count in the same line or the
    # adjacent line. Accept "62% (74 of 120)", "62% [74/120]", "62% of 120",
    # or "74 of 120 (62%)".
    lines = brief.splitlines()
    violations: list[str] = []
    count_patterns = [
        re.compile(r"\d+\s*(?:of|/)\s*\d+"),
        re.compile(r"\(\s*\d+\s*[,;]\s*n\s*=\s*\d+\s*\)", re.IGNORECASE),
        re.compile(r"n\s*=\s*\d+", re.IGNORECASE),
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


def _check_brief_uncertainty(analysis, brief):
    if brief is None:
        return 0.0, "decision_brief.md not found"
    # Find the Confidence section body (up to next header).
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
    # Accept a range (X-Y or X to Y or ± or CI notation), or an explicit
    # caveat word ("range", "interval", "uncertain", "approximately", "ci").
    has_range = bool(re.search(r"\d+(\.\d+)?\s*(?:-|to|\u2013|\u2014|\u00b1|\+/-)\s*\d+", body, re.IGNORECASE))
    has_caveat = bool(
        re.search(r"\b(range|interval|uncertain(?:ty)?|approximate|roughly|estimate|ci\b|n\s*=|small sample)\b",
                  body, re.IGNORECASE)
    )
    if not (has_range or has_caveat):
        return 0.0, f"Confidence body does not express uncertainty (no range / caveat keyword): {body[:120]!r}"
    return 1.0, None


def _check_brief_exclusions(analysis, brief):
    if brief is None:
        return 0.0, "decision_brief.md not found"
    m = re.search(
        r"#{1,6}\s*caveats?\b.*?\n(.*?)(?=\n\s*#{1,6}\s|\Z)",
        brief,
        re.IGNORECASE | re.DOTALL,
    )
    if not m:
        return 0.0, "no Caveats section body found"
    body = m.group(1).lower()
    mentioned = [cat for cat in REJECTION_CATEGORIES if cat.replace("_", " ") in body or cat in body]
    # Soft matches — "return" catches "returned", "pending" catches pending, etc.
    soft_mentions = sum(
        1 for word in ("return", "pending", "duplicate", "bad date", "bad amount",
                       "out of window", "invalid date", "non-numeric", "out-of-window")
        if word in body
    )
    total_mentions = max(len(mentioned), soft_mentions)
    if total_mentions < 3:
        return 0.0, (
            f"Caveats section names {total_mentions} rejection categories, "
            f"need at least 3. Body: {m.group(1).strip()[:200]!r}"
        )
    return 1.0, None


# ---- Criterion registry ---------------------------------------------------

CRITERIA = [
    {
        "id": "json-exists",
        "weight": 0.04,
        "description": "analysis.json exists at the workspace root and parses as JSON.",
        "check": _check_json_exists,
    },
    {
        "id": "json-schema",
        "weight": 0.06,
        "description": "analysis.json contains all required top-level keys: input_rows, accepted, rejected, rejection_reasons, monthly_revenue, top_region, customer_count, q3_revenue_total.",
        "check": _check_json_schema,
    },
    {
        "id": "input-rows",
        "weight": 0.04,
        "description": "input_rows field in analysis.json equals 180 — the actual row count of the fixture CSV, proving the agent counted the raw input before filtering.",
        "check": _check_input_rows,
    },
    {
        "id": "count-invariant",
        "weight": 0.08,
        "description": "accepted + rejected == input_rows — a stateful invariant the analysis must preserve regardless of how rejection categories were assigned.",
        "check": _check_count_invariant,
    },
    {
        "id": "rejection-categories",
        "weight": 0.08,
        "description": "rejection_reasons object classifies all six categories (bad_date, bad_amount, pending, returned, out_of_window, duplicate) with counts matching the reject-reason priority rule specified in the prompt.",
        "check": _check_rejection_categories,
    },
    {
        "id": "dedup-first-occurrence",
        "weight": 0.06,
        "description": "Deduplication uses first-occurrence semantics by order_id: later rows sharing an existing order_id are rejected as duplicate, which produces exactly 10 duplicate rejections in this fixture (not 10 randomly-chosen rejections).",
        "check": _check_dedup_first_occurrence,
    },
    {
        "id": "accepted-count",
        "weight": 0.12,
        "description": "Accepted row count equals 120, matching the valid Q3 2025 rows after excluding bad dates, bad amounts, pending, returned, out-of-window, and duplicate rows.",
        "check": _check_accepted_count,
    },
    {
        "id": "q3-revenue-total",
        "weight": 0.15,
        "description": "q3_revenue_total equals the sum of amounts across accepted rows (rounded to 2 decimal places). The expected value is 61529.77.",
        "check": _check_q3_revenue_total,
    },
    {
        "id": "monthly-revenue",
        "weight": 0.10,
        "description": "monthly_revenue has keys 2025-07, 2025-08, 2025-09 with per-month totals that sum to q3_revenue_total — a cross-field invariant checking both the breakdown and the total are consistent.",
        "check": _check_monthly_revenue,
    },
    {
        "id": "top-region",
        "weight": 0.08,
        "description": "top_region object names the region with the highest accepted revenue AND reports both its order count and revenue alongside the name, per the SKILL.md rule that percentages and rankings must carry underlying counts.",
        "check": _check_top_region,
    },
    {
        "id": "customer-count",
        "weight": 0.04,
        "description": "customer_count equals the number of distinct customer_ids across accepted rows (54 for this fixture).",
        "check": _check_customer_count,
    },
    {
        "id": "brief-exists",
        "weight": 0.02,
        "description": "decision_brief.md exists at the workspace root and has non-trivial content.",
        "check": _check_brief_exists,
    },
    {
        "id": "brief-sections",
        "weight": 0.05,
        "description": "decision_brief.md contains the five required markdown section headers (Answer, Evidence, Confidence, Caveats, Next Action) in any order.",
        "check": _check_brief_sections,
    },
    {
        "id": "brief-counts-with-percentages",
        "weight": 0.05,
        "description": "Every percentage in decision_brief.md is accompanied by its raw count on the same or adjacent line (e.g. '62% (74 of 120)') — enforcing the SKILL.md rule against presenting percentages without underlying counts.",
        "check": _check_brief_counts_with_percentages,
    },
    {
        "id": "brief-uncertainty",
        "weight": 0.02,
        "description": "Confidence section expresses uncertainty as a range, interval, or explicit caveat keyword — not a bare point estimate.",
        "check": _check_brief_uncertainty,
    },
    {
        "id": "brief-exclusions",
        "weight": 0.01,
        "description": "Caveats section names at least three distinct rejection categories from the analysis so stakeholders know what was excluded.",
        "check": _check_brief_exclusions,
    },
]

# Sanity check at import time: weights must sum to 1.0 (tolerance 1e-3).
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    analysis, _analysis_err = _load_json(workspace_path)
    brief, _brief_err = _load_brief(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](analysis, brief)
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

"""
Grade function for document-pdf_task_02.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Expected values (computed from _gen_fixture.py with seed 20260412):
  - total_rows_extracted: 22 (12 page 1 + 10 page 2)
  - duplicate_count: 2 (TXN-1004 and TXN-1008 appear twice)
  - duplicate_txn_ids: ["TXN-1004", "TXN-1008"] (sorted)
  - accepted_count: 20
  - total_amount: 89797.42
  - top_category: "Engineering"
  - by_category: Engineering={count:5, total:36985.01}, Operations={count:7, total:26207.19},
                  HR={count:2, total:14038.51}, Marketing={count:3, total:6289.05},
                  Finance={count:3, total:6277.66}
  - Invariant: accepted_count + duplicate_count == total_rows_extracted
  - Invariant: sum(by_category totals) == total_amount (±0.02)
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path


# ── Expected values ───────────────────────────────────────────────────────────

EXPECTED = {
    "total_rows_extracted": 22,
    "duplicate_count": 2,
    "duplicate_txn_ids": ["TXN-1004", "TXN-1008"],
    "accepted_count": 20,
    "total_amount": 89797.42,
    "top_category": "Engineering",
    "by_category": {
        "Engineering": {"count": 5, "total": 36985.01},
        "Operations":  {"count": 7, "total": 26207.19},
        "HR":          {"count": 2, "total": 14038.51},
        "Marketing":   {"count": 3, "total": 6289.05},
        "Finance":     {"count": 3, "total": 6277.66},
    },
}

REQUIRED_JSON_KEYS = {
    "total_rows_extracted", "duplicate_count", "duplicate_txn_ids",
    "accepted_count", "total_amount", "top_category", "by_category",
}

REQUIRED_MD_SECTIONS = {"summary", "category breakdown", "data quality"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _approx(a, b, tol_abs=0.02, tol_rel=0.001):
    try:
        return math.isclose(float(a), float(b), abs_tol=tol_abs, rel_tol=tol_rel)
    except (TypeError, ValueError):
        return False


def _load_json(workspace_path: str):
    p = Path(workspace_path) / "ledger_report.json"
    if not p.exists():
        return None, "ledger_report.json not found"
    try:
        return json.loads(p.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"ledger_report.json invalid JSON: {e}"


def _load_md(workspace_path: str):
    p = Path(workspace_path) / "reconciliation_report.md"
    if not p.exists():
        return None, "reconciliation_report.md not found"
    return p.read_text(), None


# ── Per-criterion checks ──────────────────────────────────────────────────────

def _check_json_exists(report, md):
    if report is None:
        return 0.0, "ledger_report.json missing or unparseable"
    return 1.0, None


def _check_json_schema(report, md):
    if report is None:
        return 0.0, "ledger_report.json missing"
    missing = REQUIRED_JSON_KEYS - set(report.keys())
    if missing:
        return 0.0, f"missing keys: {sorted(missing)}"
    return 1.0, None


def _check_rows_extracted(report, md):
    """Total rows extracted from PDF must be 22 (all rows before dedup)."""
    if report is None:
        return 0.0, "ledger_report.json missing"
    got = report.get("total_rows_extracted")
    if got != EXPECTED["total_rows_extracted"]:
        return 0.0, (
            f"total_rows_extracted: expected {EXPECTED['total_rows_extracted']}, got {got}. "
            f"The PDF has {EXPECTED['total_rows_extracted']} data rows across 2 pages including duplicates."
        )
    return 1.0, None


def _check_dedup_count(report, md):
    """2 duplicate txn_ids (TXN-1004, TXN-1008) appear on page 2 after first appearing on page 1."""
    if report is None:
        return 0.0, "ledger_report.json missing"
    got = report.get("duplicate_count")
    if got != EXPECTED["duplicate_count"]:
        return 0.0, (
            f"duplicate_count: expected {EXPECTED['duplicate_count']}, got {got}. "
            f"TXN-1004 and TXN-1008 appear on both pages; first-occurrence wins."
        )
    return 1.0, None


def _check_dedup_ids(report, md):
    """duplicate_txn_ids must list exactly TXN-1004 and TXN-1008 (in any order)."""
    if report is None:
        return 0.0, "ledger_report.json missing"
    got = report.get("duplicate_txn_ids")
    if not isinstance(got, list):
        return 0.0, f"duplicate_txn_ids is not a list, got: {got!r}"
    got_set = set(got)
    exp_set = set(EXPECTED["duplicate_txn_ids"])
    if got_set != exp_set:
        return 0.0, (
            f"duplicate_txn_ids: expected {sorted(exp_set)}, got {sorted(got_set)}. "
            f"Dedup must use first-occurrence semantics by txn_id."
        )
    return 1.0, None


def _check_accepted_count(report, md):
    """20 accepted rows after removing 2 duplicates from 22 total."""
    if report is None:
        return 0.0, "ledger_report.json missing"
    got = report.get("accepted_count")
    if got != EXPECTED["accepted_count"]:
        return 0.0, f"accepted_count: expected {EXPECTED['accepted_count']}, got {got}"
    return 1.0, None


def _check_row_count_invariant(report, md):
    """accepted_count + duplicate_count == total_rows_extracted (stateful invariant)."""
    if report is None:
        return 0.0, "ledger_report.json missing"
    try:
        acc = int(report.get("accepted_count"))
        dup = int(report.get("duplicate_count"))
        tot = int(report.get("total_rows_extracted"))
    except (TypeError, ValueError):
        return 0.0, "accepted_count, duplicate_count, or total_rows_extracted not integers"
    if acc + dup != tot:
        return 0.0, (
            f"accepted_count ({acc}) + duplicate_count ({dup}) = {acc+dup} "
            f"!= total_rows_extracted ({tot})"
        )
    return 1.0, None


def _check_total_amount(report, md):
    """total_amount must be 89797.42 — requires stripping $ and commas from PDF text before parsing."""
    if report is None:
        return 0.0, "ledger_report.json missing"
    got = report.get("total_amount")
    if not _approx(got, EXPECTED["total_amount"]):
        return 0.0, (
            f"total_amount: expected {EXPECTED['total_amount']}, got {got}. "
            f"Did you strip '$' and ',' before parsing amounts? First-occurrence dedup must be applied."
        )
    return 1.0, None


def _check_top_category(report, md):
    """Top spending category by total amount is Engineering (36985.01)."""
    if report is None:
        return 0.0, "ledger_report.json missing"
    got = report.get("top_category")
    if got != EXPECTED["top_category"]:
        return 0.0, (
            f"top_category: expected {EXPECTED['top_category']!r}, got {got!r}. "
            f"Rank by total amount across accepted rows only."
        )
    return 1.0, None


def _check_category_counts(report, md):
    """by_category counts match expected (Engineering=5, Operations=7, HR=2, Marketing=3, Finance=3)."""
    if report is None:
        return 0.0, "ledger_report.json missing"
    bc = report.get("by_category")
    if not isinstance(bc, dict):
        return 0.0, "by_category is not an object"
    errors = []
    for cat, exp_data in EXPECTED["by_category"].items():
        got_data = bc.get(cat)
        if got_data is None:
            errors.append(f"{cat} missing from by_category")
            continue
        got_count = got_data.get("count") if isinstance(got_data, dict) else None
        if got_count != exp_data["count"]:
            errors.append(f"{cat}.count: expected {exp_data['count']}, got {got_count}")
    if errors:
        return 0.0, "; ".join(errors[:3])
    return 1.0, None


def _check_category_totals(report, md):
    """by_category totals match expected amounts (tolerance 0.02)."""
    if report is None:
        return 0.0, "ledger_report.json missing"
    bc = report.get("by_category")
    if not isinstance(bc, dict):
        return 0.0, "by_category is not an object"
    errors = []
    for cat, exp_data in EXPECTED["by_category"].items():
        got_data = bc.get(cat)
        if got_data is None:
            errors.append(f"{cat} missing")
            continue
        got_total = got_data.get("total") if isinstance(got_data, dict) else None
        if not _approx(got_total, exp_data["total"]):
            errors.append(f"{cat}.total: expected {exp_data['total']}, got {got_total}")
    if errors:
        return 0.0, "; ".join(errors[:3])
    return 1.0, None


def _check_category_sum_invariant(report, md):
    """sum(by_category totals) == total_amount — ensures category breakdown is internally consistent."""
    if report is None:
        return 0.0, "ledger_report.json missing"
    bc = report.get("by_category")
    total = report.get("total_amount")
    if not isinstance(bc, dict) or total is None:
        return 0.0, "by_category or total_amount missing"
    try:
        cat_sum = sum(
            float(v["total"]) if isinstance(v, dict) else float(v)
            for v in bc.values()
        )
    except (TypeError, ValueError, KeyError):
        return 0.0, "could not sum by_category totals"
    if not _approx(cat_sum, float(total), tol_abs=0.05):
        return 0.0, (
            f"sum(by_category totals) = {cat_sum:.2f} != total_amount ({total}) "
            f"— cross-field invariant violated"
        )
    return 1.0, None


def _check_md_exists(report, md):
    if md is None:
        return 0.0, "reconciliation_report.md missing"
    if len(md.strip()) < 50:
        return 0.0, f"reconciliation_report.md is too short ({len(md.strip())} chars)"
    return 1.0, None


def _check_md_sections(report, md):
    """reconciliation_report.md must contain Summary, Category Breakdown, and Data Quality sections."""
    if md is None:
        return 0.0, "reconciliation_report.md missing"
    headers = [h.strip().lower() for h in re.findall(r"^\s*#{1,6}\s*(.+?)\s*$", md, re.MULTILINE)]
    missing = [s for s in REQUIRED_MD_SECTIONS if not any(s in h for h in headers)]
    if missing:
        return 0.0, f"missing sections: {missing}; found headers: {headers}"
    return 1.0, None


def _check_md_duplicate_names(report, md):
    """reconciliation_report.md must name the specific duplicate txn_ids removed."""
    if md is None:
        return 0.0, "reconciliation_report.md missing"
    for tid in EXPECTED["duplicate_txn_ids"]:
        if tid not in md:
            return 0.0, f"reconciliation_report.md does not mention duplicate txn_id {tid}"
    return 1.0, None


# ── Criterion registry ────────────────────────────────────────────────────────

CRITERIA = [
    {
        "id": "json-exists",
        "weight": 0.03,
        "description": "ledger_report.json exists and is valid JSON.",
        "check": _check_json_exists,
    },
    {
        "id": "json-schema",
        "weight": 0.03,
        "description": "ledger_report.json contains all required keys: total_rows_extracted, duplicate_count, duplicate_txn_ids, accepted_count, total_amount, top_category, by_category.",
        "check": _check_json_schema,
    },
    {
        "id": "rows-extracted",
        "weight": 0.09,
        "description": "total_rows_extracted equals 22 — all rows extracted from both PDF pages before deduplication. Requires reading both pages and counting pre-dedup.",
        "check": _check_rows_extracted,
    },
    {
        "id": "dedup-count",
        "weight": 0.09,
        "description": "duplicate_count equals 2 — TXN-1004 and TXN-1008 each appear twice in the PDF (once on each page), so first-occurrence deduplication removes 2 rows.",
        "check": _check_dedup_count,
    },
    {
        "id": "dedup-ids",
        "weight": 0.07,
        "description": "duplicate_txn_ids lists exactly [TXN-1004, TXN-1008] — the two txn_ids whose second occurrence was removed. First-occurrence semantics: the page-1 row is kept, the page-2 repeat is discarded.",
        "check": _check_dedup_ids,
    },
    {
        "id": "accepted-count",
        "weight": 0.09,
        "description": "accepted_count equals 20 (22 extracted minus 2 duplicates). Proves deduplication was applied before counting accepted rows.",
        "check": _check_accepted_count,
    },
    {
        "id": "row-count-invariant",
        "weight": 0.07,
        "description": "accepted_count + duplicate_count == total_rows_extracted — a stateful invariant ensuring no rows were silently dropped or double-counted.",
        "check": _check_row_count_invariant,
    },
    {
        "id": "total-amount",
        "weight": 0.15,
        "description": "total_amount equals 89797.42 — computed only over accepted rows with $ and commas stripped from amount strings. Using duplicate rows inflates this value; failing to strip currency symbols causes parse failures.",
        "check": _check_total_amount,
    },
    {
        "id": "top-category",
        "weight": 0.05,
        "description": "top_category is 'Engineering', the category with the highest total amount across accepted rows (36985.01). Using raw/duplicate rows changes the winner.",
        "check": _check_top_category,
    },
    {
        "id": "category-counts",
        "weight": 0.08,
        "description": "by_category count fields match expected per-category transaction counts: Engineering=5, Operations=7, HR=2, Marketing=3, Finance=3 (after dedup).",
        "check": _check_category_counts,
    },
    {
        "id": "category-totals",
        "weight": 0.09,
        "description": "by_category total fields match expected per-category amount sums (e.g. Engineering=36985.01, Operations=26207.19) within 0.02 tolerance.",
        "check": _check_category_totals,
    },
    {
        "id": "category-sum-invariant",
        "weight": 0.05,
        "description": "sum(by_category totals) equals total_amount — cross-field invariant ensuring category breakdown and overall total are internally consistent.",
        "check": _check_category_sum_invariant,
    },
    {
        "id": "md-exists",
        "weight": 0.03,
        "description": "reconciliation_report.md exists with non-trivial content.",
        "check": _check_md_exists,
    },
    {
        "id": "md-sections",
        "weight": 0.04,
        "description": "reconciliation_report.md contains markdown sections for Summary, Category Breakdown, and Data Quality.",
        "check": _check_md_sections,
    },
    {
        "id": "md-duplicate-names",
        "weight": 0.04,
        "description": "reconciliation_report.md names the specific removed duplicate txn_ids (TXN-1004 and TXN-1008) to prove the agent identified them, not just a generic dedup count.",
        "check": _check_md_duplicate_names,
    },
]

# Sanity check at import time: weights must sum to 1.0 (tolerance 1e-3).
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    report, _ = _load_json(workspace_path)
    md, _ = _load_md(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](report, md)
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

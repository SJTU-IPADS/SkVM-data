"""
Grade function for pdf_task_02.

Tests correct extraction from a multi-page budget report PDF.

Trap 1 (archetype 1 — under-specified step):
  The Engineering section has a SUBTOTAL row covering Personnel costs.
  Agents that sum all Annual values (including the SUBTOTAL) get
  $3,059,000 instead of the correct $2,019,000. The prompt specifies
  to use the DEPARTMENT TOTAL row, not to sum line items — but this
  requires recognising and excluding the SUBTOTAL row.

Trap 2 (archetype 3 — multi-step coordination):
  The Operations budget spans two pages (pages 4 and 5).
  The DEPARTMENT TOTAL appears only on page 5. Agents that read
  only the first table they find on page 4 will miss the total.

Trap 3 (archetype 4 — known-edge-case):
  Page 7 is a company roll-up summary with a GRAND TOTAL row.
  The prompt explicitly says to derive grand_total by summing the
  four department totals — NOT by reading page 7. The values agree,
  but the process matters for the line_item_count and source_pages checks.

Trap 4 (archetype 5 — stateful invariant):
  grand_total must equal the sum of the four department annual_budgets.

Expected values are hardcoded from budget_report.pdf (deterministic fixture).
"""
from __future__ import annotations
import json
import math
from pathlib import Path


# ---- Expected values ---------------------------------------------------------

EXPECTED = {
    "page_count":  7,
    "eng_total":   2019000,
    "mkt_total":   1623000,
    "ops_total":   2266000,
    "hr_total":    1002000,
    "grand_total": 6910000,
    # Line item counts (excludes SUBTOTAL and DEPARTMENT TOTAL rows)
    "eng_line_items": 10,
    "mkt_line_items": 8,
    "ops_line_items": 12,
    "hr_line_items":  6,
    # Operations spans 2 pages
    "ops_source_pages": [4, 5],
    # Engineering has 1 subtotal row
    "eng_subtotal_rows": 1,
}

REQUIRED_TOP_KEYS = {
    "page_count", "departments", "grand_total",
}
REQUIRED_DEPT_KEYS = {
    "Engineering", "Marketing", "Operations", "Human Resources",
}
REQUIRED_DEPT_FIELDS = {
    "annual_budget", "line_item_count", "source_pages",
}


def _approx(a, b, tol=1e-4):
    if a is None or b is None:
        return False
    try:
        return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=1)
    except (TypeError, ValueError):
        return False


def _load(workspace_path):
    p = Path(workspace_path) / "summary.json"
    if not p.exists():
        return None, "summary.json not found"
    try:
        return json.loads(p.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"summary.json not valid JSON: {e}"


# ---- Criterion checks --------------------------------------------------------

def _check_json_exists(r):
    if r is None:
        return 0.0, "summary.json missing or unparseable"
    return 1.0, None


def _check_json_schema(r):
    if r is None:
        return 0.0, "summary.json missing"
    missing_top = REQUIRED_TOP_KEYS - set(r.keys())
    if missing_top:
        return 0.0, f"missing top-level keys: {sorted(missing_top)}"
    depts = r.get("departments") or {}
    missing_depts = REQUIRED_DEPT_KEYS - set(depts.keys())
    if missing_depts:
        return 0.0, f"departments missing keys: {sorted(missing_depts)}"
    for dept in REQUIRED_DEPT_KEYS:
        dept_obj = depts.get(dept) or {}
        missing_fields = REQUIRED_DEPT_FIELDS - set(dept_obj.keys())
        if missing_fields:
            return 0.0, f"departments.{dept!r} missing fields: {sorted(missing_fields)}"
    return 1.0, None


def _check_page_count(r):
    if r is None:
        return 0.0, "summary.json missing"
    got = r.get("page_count")
    if got != EXPECTED["page_count"]:
        return 0.0, f"page_count: expected {EXPECTED['page_count']}, got {got}"
    return 1.0, None


def _check_engineering_budget_no_subtotal(r):
    """
    Engineering annual_budget must be 2,019,000 (DEPARTMENT TOTAL row).
    Agents who sum all Annual values including the SUBTOTAL row get 3,059,000.
    """
    if r is None:
        return 0.0, "summary.json missing"
    depts = r.get("departments") or {}
    eng = depts.get("Engineering") or {}
    got = eng.get("annual_budget")
    if got is None:
        return 0.0, "departments.Engineering.annual_budget missing"
    if not _approx(got, EXPECTED["eng_total"]):
        # Check for common wrong answer (sum-including-subtotal)
        wrong_sum = 3059000  # 2019000 + 1040000 SUBTOTAL
        hint = ""
        if _approx(got, wrong_sum):
            hint = " (this is 2,019,000 + 1,040,000 SUBTOTAL — the SUBTOTAL row must be excluded)"
        return 0.0, f"Engineering annual_budget: expected {EXPECTED['eng_total']:,}, got {got}{hint}"
    return 1.0, None


def _check_marketing_budget(r):
    if r is None:
        return 0.0, "summary.json missing"
    depts = r.get("departments") or {}
    mkt = depts.get("Marketing") or {}
    got = mkt.get("annual_budget")
    if not _approx(got, EXPECTED["mkt_total"]):
        return 0.0, f"Marketing annual_budget: expected {EXPECTED['mkt_total']:,}, got {got}"
    return 1.0, None


def _check_operations_budget_two_pages(r):
    """
    Operations DEPARTMENT TOTAL appears only on page 5 (the second of two pages).
    Agents that read only page 4 find no DEPARTMENT TOTAL and may guess 0 or wrong.
    """
    if r is None:
        return 0.0, "summary.json missing"
    depts = r.get("departments") or {}
    ops = depts.get("Operations") or {}
    got = ops.get("annual_budget")
    if not _approx(got, EXPECTED["ops_total"]):
        return 0.0, (
            f"Operations annual_budget: expected {EXPECTED['ops_total']:,}, got {got}. "
            "The DEPARTMENT TOTAL row for Operations is on page 5 (the budget spans pages 4-5)."
        )
    return 1.0, None


def _check_hr_budget(r):
    if r is None:
        return 0.0, "summary.json missing"
    depts = r.get("departments") or {}
    hr = depts.get("Human Resources") or {}
    got = hr.get("annual_budget")
    if not _approx(got, EXPECTED["hr_total"]):
        return 0.0, f"Human Resources annual_budget: expected {EXPECTED['hr_total']:,}, got {got}"
    return 1.0, None


def _check_grand_total_invariant(r):
    """
    grand_total must equal the sum of the four department annual_budgets.
    This is a stateful invariant — even if all four department budgets are
    correct, agents who read grand_total from page 7 (the roll-up summary)
    instead of computing it may produce a value that passes trivially
    but their line_item_count will be wrong.
    """
    if r is None:
        return 0.0, "summary.json missing"
    depts = r.get("departments") or {}
    grand = r.get("grand_total")
    try:
        computed = sum(
            (depts.get(dept) or {}).get("annual_budget", 0)
            for dept in ["Engineering", "Marketing", "Operations", "Human Resources"]
        )
    except (TypeError, ValueError):
        return 0.0, "could not sum department annual_budgets"
    if not _approx(grand, EXPECTED["grand_total"]):
        return 0.0, f"grand_total: expected {EXPECTED['grand_total']:,}, got {grand}"
    if not _approx(computed, EXPECTED["grand_total"]):
        return 0.0, f"sum of department budgets: expected {EXPECTED['grand_total']:,}, got {computed}"
    if not _approx(grand, computed):
        return 0.0, f"grand_total ({grand}) != sum of department budgets ({computed})"
    return 1.0, None


def _check_engineering_line_item_count(r):
    if r is None:
        return 0.0, "summary.json missing"
    depts = r.get("departments") or {}
    eng = depts.get("Engineering") or {}
    got = eng.get("line_item_count")
    if got != EXPECTED["eng_line_items"]:
        return 0.0, (
            f"Engineering line_item_count: expected {EXPECTED['eng_line_items']}, got {got}. "
            "There are 10 line items in the Engineering budget; the SUBTOTAL row is not a line item."
        )
    return 1.0, None


def _check_operations_line_item_count(r):
    if r is None:
        return 0.0, "summary.json missing"
    depts = r.get("departments") or {}
    ops = depts.get("Operations") or {}
    got = ops.get("line_item_count")
    if got != EXPECTED["ops_line_items"]:
        return 0.0, (
            f"Operations line_item_count: expected {EXPECTED['ops_line_items']}, got {got}. "
            "There are 12 line items total (6 on page 4, 6 on page 5); "
            "the continuation marker and DEPARTMENT TOTAL rows don't count."
        )
    return 1.0, None


def _check_operations_source_pages(r):
    """
    Checks that Operations.source_pages includes both page 4 and page 5,
    confirming the agent recognised that the budget spans two pages.
    """
    if r is None:
        return 0.0, "summary.json missing"
    depts = r.get("departments") or {}
    ops = depts.get("Operations") or {}
    pages = ops.get("source_pages")
    if not isinstance(pages, list):
        return 0.0, f"Operations.source_pages is not a list: {pages!r}"
    pages_set = set(pages)
    if 4 not in pages_set or 5 not in pages_set:
        return 0.0, (
            f"Operations.source_pages should include both 4 and 5, got {sorted(pages_set)}. "
            "The Operations budget spans pages 4 and 5 of the PDF."
        )
    return 1.0, None


def _check_engineering_subtotal_flagged(r):
    """
    Checks that the agent noted the SUBTOTAL row's presence in Engineering
    (subtotal_rows_present should be 1), demonstrating awareness of the trap.
    """
    if r is None:
        return 0.0, "summary.json missing"
    depts = r.get("departments") or {}
    eng = depts.get("Engineering") or {}
    got = eng.get("subtotal_rows_present")
    if got is None:
        return 0.0, "departments.Engineering.subtotal_rows_present missing"
    try:
        if int(got) != EXPECTED["eng_subtotal_rows"]:
            return 0.0, (
                f"Engineering subtotal_rows_present: expected {EXPECTED['eng_subtotal_rows']}, got {got}. "
                "There is 1 SUBTOTAL (Personnel) row in the Engineering table that must not be counted as a line item."
            )
    except (TypeError, ValueError):
        return 0.0, f"subtotal_rows_present is not an integer: {got!r}"
    return 1.0, None


# ---- CRITERIA registry -------------------------------------------------------

CRITERIA = [
    {
        "id": "json-exists",
        "weight": 0.04,
        "description": "summary.json exists at the workspace root and parses as valid JSON.",
        "check": _check_json_exists,
    },
    {
        "id": "json-schema",
        "weight": 0.06,
        "description": "summary.json contains page_count, grand_total, and a departments object with all four departments (Engineering, Marketing, Operations, Human Resources) each carrying annual_budget, line_item_count, source_pages.",
        "check": _check_json_schema,
    },
    {
        "id": "page-count",
        "weight": 0.05,
        "description": "page_count field equals 7 — the PDF has a cover page, 4 department sections (Engineering, Marketing, Operations pages 4-5, HR), and a company roll-up summary on page 7.",
        "check": _check_page_count,
    },
    {
        "id": "engineering-budget-no-subtotal",
        "weight": 0.20,
        "description": "Engineering annual_budget equals 2,019,000 — the DEPARTMENT TOTAL row value. The Engineering table contains a SUBTOTAL (Personnel) row covering the first 5 line items ($1,040,000); agents who sum all Annual values (including that subtotal) arrive at $3,059,000, which is wrong.",
        "check": _check_engineering_budget_no_subtotal,
    },
    {
        "id": "marketing-budget",
        "weight": 0.08,
        "description": "Marketing annual_budget equals 1,623,000, matching the DEPARTMENT TOTAL row on page 3.",
        "check": _check_marketing_budget,
    },
    {
        "id": "operations-budget-two-pages",
        "weight": 0.15,
        "description": "Operations annual_budget equals 2,266,000 — the DEPARTMENT TOTAL row appears only on page 5, since the Operations budget spans pages 4 and 5. Agents that extract only the first table on page 4 find no DEPARTMENT TOTAL and cannot compute the correct figure.",
        "check": _check_operations_budget_two_pages,
    },
    {
        "id": "hr-budget",
        "weight": 0.08,
        "description": "Human Resources annual_budget equals 1,002,000, matching the DEPARTMENT TOTAL row on page 6.",
        "check": _check_hr_budget,
    },
    {
        "id": "grand-total-invariant",
        "weight": 0.12,
        "description": "grand_total equals 6,910,000, which must equal the sum of the four department annual_budgets (2,019,000 + 1,623,000 + 2,266,000 + 1,002,000). The page 7 roll-up also shows this number, but the prompt requires computing it from the department data — the invariant is that grand_total == sum(departments[*].annual_budget).",
        "check": _check_grand_total_invariant,
    },
    {
        "id": "engineering-line-item-count",
        "weight": 0.07,
        "description": "Engineering line_item_count equals 10 — the number of actual budget line items excluding the SUBTOTAL row and the DEPARTMENT TOTAL row.",
        "check": _check_engineering_line_item_count,
    },
    {
        "id": "operations-line-item-count",
        "weight": 0.07,
        "description": "Operations line_item_count equals 12 (6 on page 4 + 6 on page 5), excluding the continuation marker and DEPARTMENT TOTAL rows.",
        "check": _check_operations_line_item_count,
    },
    {
        "id": "operations-source-pages",
        "weight": 0.05,
        "description": "Operations source_pages includes both 4 and 5, confirming the agent correctly identified that the Operations budget spans two PDF pages rather than treating it as a single-page department.",
        "check": _check_operations_source_pages,
    },
    {
        "id": "engineering-subtotal-flagged",
        "weight": 0.03,
        "description": "Engineering subtotal_rows_present equals 1, indicating the agent detected and explicitly tracked the presence of the SUBTOTAL (Personnel) row in the Engineering table.",
        "check": _check_engineering_subtotal_flagged,
    },
]

_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    r, _err = _load(workspace_path)
    records = []
    for spec in CRITERIA:
        score, details = spec["check"](r)
        record = {
            "id":          spec["id"],
            "score":       float(score),
            "weight":      float(spec["weight"]),
            "description": spec["description"],
        }
        if details is not None and score < 1.0:
            record["details"] = details
        records.append(record)
    return records

"""
Grade function for excel-xlsx_task_02.

Checks:
1. commissions.xlsx exists
2. PayrollSummary sheet has correct headers
3. Exactly 5 data rows (one per salesperson) + a Totals row
4. SalesCount correct per person (requires correct date-independent parsing)
5. TotalSales correct per person (requires correct amount parsing: float + "$X,XXX.XX")
6. Commission correct per person (requires correct rate: 8% if >= 1000, 5% otherwise)
7. Totals row uses SUM formulas (not hardcoded)
8. report.json exists with required keys
9. total_transactions == 80
10. total_sales correct
11. total_commission correct
12. quarterly_breakdown has all 4 quarters with correct counts (requires correct date parsing)
13. Cross-invariant: sum of quarterly transaction_count == total_transactions
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

EXPECTED = {
    "total_transactions": 80,
    "total_sales": 217035.74,
    "total_commission": 17091.04,
    "by_salesperson": {
        "Alice Chen":   {"sales_count": 16, "total_sales": 47054.32, "commission": 3728.62},
        "Bob Martinez": {"sales_count": 12, "total_sales": 30917.45, "commission": 2434.05},
        "Carol Singh":  {"sales_count": 15, "total_sales": 39857.94, "commission": 3127.31},
        "David Lee":    {"sales_count": 18, "total_sales": 50556.78, "commission": 4017.62},
        "Eva Turner":   {"sales_count": 19, "total_sales": 48649.25, "commission": 3783.44},
    },
    "quarterly_breakdown": {
        "Q1 2025": {"transaction_count": 20, "sales": 48359.34, "commission": 3774.88},
        "Q2 2025": {"transaction_count": 22, "sales": 58109.21, "commission": 4590.82},
        "Q3 2025": {"transaction_count": 19, "sales": 56626.57, "commission": 4484.33},
        "Q4 2025": {"transaction_count": 19, "sales": 53940.62, "commission": 4241.01},
    },
}

SALESPERSONS = set(EXPECTED["by_salesperson"].keys())
QUARTERS = set(EXPECTED["quarterly_breakdown"].keys())
REQUIRED_JSON_KEYS = {"total_transactions", "total_sales", "total_commission", "quarterly_breakdown", "by_salesperson"}
SUMMARY_HEADERS = {"Salesperson", "SalesCount", "TotalSales", "Commission"}


def _approx(a, b, tol=0.02):
    try:
        return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.001)
    except (TypeError, ValueError):
        return False


def _load_commissions(workspace_path):
    path = Path(workspace_path) / "commissions.xlsx"
    if not path.exists():
        return None, None, "commissions.xlsx not found"
    try:
        import openpyxl
        wb_f = openpyxl.load_workbook(str(path), data_only=False)
        wb_d = openpyxl.load_workbook(str(path), data_only=True)
        return wb_f, wb_d, None
    except Exception as e:
        return None, None, f"commissions.xlsx failed to load: {e}"


def _load_report(workspace_path):
    path = Path(workspace_path) / "report.json"
    if not path.exists():
        return None, "report.json not found"
    try:
        return json.loads(path.read_text()), None
    except Exception as e:
        return None, f"report.json parse error: {e}"


def _get_col_map(ws):
    """Return {header_name: col_index} from row 1."""
    col_map = {}
    for c in range(1, ws.max_column + 1):
        h = ws.cell(row=1, column=c).value
        if h:
            col_map[str(h).strip()] = c
    return col_map


def _check_file_exists(wb_f, wb_d, rep, workspace_path):
    if wb_f is None:
        return 0.0, "commissions.xlsx missing or unreadable"
    return 1.0, None


def _check_schema(wb_f, wb_d, rep, workspace_path):
    if wb_f is None:
        return 0.0, "commissions.xlsx missing"
    if "PayrollSummary" not in wb_f.sheetnames:
        return 0.0, f"PayrollSummary sheet not found; found: {wb_f.sheetnames}"
    ws = wb_f["PayrollSummary"]
    headers = {ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1) if ws.cell(row=1, column=c).value}
    missing = SUMMARY_HEADERS - {str(h).strip() for h in headers}
    if missing:
        return 0.0, f"PayrollSummary missing headers: {sorted(missing)}"
    return 1.0, None


def _check_data_row_count(wb_f, wb_d, rep, workspace_path):
    if wb_f is None:
        return 0.0, "commissions.xlsx missing"
    if "PayrollSummary" not in wb_f.sheetnames:
        return 0.0, "PayrollSummary sheet not found"
    ws = wb_f["PayrollSummary"]
    col_map = _get_col_map(ws)
    sp_col = col_map.get("Salesperson")
    if not sp_col:
        return 0.0, "Salesperson column not found"
    # Count rows where Salesperson is one of the 5 known persons
    sp_rows = 0
    for row in range(2, ws.max_row + 1):
        val = ws.cell(row=row, column=sp_col).value
        if val and str(val).strip() in SALESPERSONS:
            sp_rows += 1
    if sp_rows != 5:
        return 0.0, f"Found {sp_rows} salesperson rows, expected 5"
    return 1.0, None


def _check_sales_count(wb_f, wb_d, rep, workspace_path):
    """SalesCount per salesperson must be correct."""
    if wb_f is None:
        return 0.0, "commissions.xlsx missing"
    if "PayrollSummary" not in wb_f.sheetnames:
        return 0.0, "PayrollSummary sheet not found"
    ws = wb_d["PayrollSummary"]  # data_only to read values
    col_map = _get_col_map(wb_f["PayrollSummary"])
    sp_col = col_map.get("Salesperson")
    sc_col = col_map.get("SalesCount")
    if not sp_col or not sc_col:
        return 0.0, "Required columns not found"
    wrong = []
    for row in range(2, ws.max_row + 1):
        sp_val = ws.cell(row=row, column=sp_col).value
        if sp_val is None or str(sp_val).strip() not in SALESPERSONS:
            continue
        sp = str(sp_val).strip()
        got = ws.cell(row=row, column=sc_col).value
        want = EXPECTED["by_salesperson"][sp]["sales_count"]
        try:
            got_int = int(got)
        except (TypeError, ValueError):
            wrong.append(f"{sp}: non-integer value {got!r}")
            continue
        if got_int != want:
            wrong.append(f"{sp}: expected {want}, got {got_int}")
    if wrong:
        return 0.0, "; ".join(wrong)
    return 1.0, None


def _check_total_sales(wb_f, wb_d, rep, workspace_path):
    """TotalSales per salesperson must be correct (tests amount parsing)."""
    if wb_f is None:
        return 0.0, "commissions.xlsx missing"
    if "PayrollSummary" not in wb_f.sheetnames:
        return 0.0, "PayrollSummary sheet not found"
    ws = wb_d["PayrollSummary"]
    col_map = _get_col_map(wb_f["PayrollSummary"])
    sp_col = col_map.get("Salesperson")
    ts_col = col_map.get("TotalSales")
    if not sp_col or not ts_col:
        return 0.0, "Required columns not found"
    wrong = []
    for row in range(2, ws.max_row + 1):
        sp_val = ws.cell(row=row, column=sp_col).value
        if sp_val is None or str(sp_val).strip() not in SALESPERSONS:
            continue
        sp = str(sp_val).strip()
        got = ws.cell(row=row, column=ts_col).value
        want = EXPECTED["by_salesperson"][sp]["total_sales"]
        if not _approx(got, want):
            wrong.append(f"{sp}: expected {want:.2f}, got {got!r}")
    if wrong:
        return 0.0, "; ".join(wrong[:3])
    return 1.0, None


def _check_commission(wb_f, wb_d, rep, workspace_path):
    """Commission per salesperson must be correct (tests rate application)."""
    if wb_f is None:
        return 0.0, "commissions.xlsx missing"
    if "PayrollSummary" not in wb_f.sheetnames:
        return 0.0, "PayrollSummary sheet not found"
    ws = wb_d["PayrollSummary"]
    col_map = _get_col_map(wb_f["PayrollSummary"])
    sp_col = col_map.get("Salesperson")
    cm_col = col_map.get("Commission")
    if not sp_col or not cm_col:
        return 0.0, "Required columns not found"
    wrong = []
    for row in range(2, ws.max_row + 1):
        sp_val = ws.cell(row=row, column=sp_col).value
        if sp_val is None or str(sp_val).strip() not in SALESPERSONS:
            continue
        sp = str(sp_val).strip()
        got = ws.cell(row=row, column=cm_col).value
        want = EXPECTED["by_salesperson"][sp]["commission"]
        if not _approx(got, want, tol=0.10):
            wrong.append(f"{sp}: expected {want:.2f}, got {got!r}")
    if wrong:
        return 0.0, "; ".join(wrong[:3])
    return 1.0, None


def _check_totals_row_formulas(wb_f, wb_d, rep, workspace_path):
    """Totals row in PayrollSummary must use SUM formulas for numeric columns."""
    if wb_f is None:
        return 0.0, "commissions.xlsx missing"
    if "PayrollSummary" not in wb_f.sheetnames:
        return 0.0, "PayrollSummary sheet not found"
    ws = wb_f["PayrollSummary"]  # data_only=False to read formulas
    col_map = _get_col_map(ws)
    ts_col = col_map.get("TotalSales")
    cm_col = col_map.get("Commission")
    if not ts_col or not cm_col:
        return 0.0, "TotalSales or Commission column not found"
    
    # Find Totals row (look for a row with "Total" in Salesperson column or last data row)
    sp_col = col_map.get("Salesperson")
    totals_row = None
    for row in range(2, ws.max_row + 1):
        sp_val = ws.cell(row=row, column=sp_col).value if sp_col else None
        if sp_val and "total" in str(sp_val).lower():
            totals_row = row
            break
    
    if totals_row is None:
        # Try to find last row with any content
        for row in range(ws.max_row, 1, -1):
            if any(ws.cell(row=row, column=c).value for c in range(1, ws.max_column + 1)):
                totals_row = row
                break
    
    if totals_row is None:
        return 0.0, "Could not find a Totals row in PayrollSummary"
    
    ts_val = ws.cell(row=totals_row, column=ts_col).value
    cm_val = ws.cell(row=totals_row, column=cm_col).value
    
    failures = []
    if not (isinstance(ts_val, str) and ts_val.startswith("=")):
        failures.append(f"TotalSales totals cell is {ts_val!r}, not a formula")
    if not (isinstance(cm_val, str) and cm_val.startswith("=")):
        failures.append(f"Commission totals cell is {cm_val!r}, not a formula")
    
    if failures:
        return 0.0, "; ".join(failures)
    return 1.0, None


def _check_json_exists(wb_f, wb_d, rep, workspace_path):
    if rep is None:
        return 0.0, "report.json missing or unparseable"
    return 1.0, None


def _check_json_schema(wb_f, wb_d, rep, workspace_path):
    if rep is None:
        return 0.0, "report.json missing"
    missing = REQUIRED_JSON_KEYS - set(rep.keys())
    if missing:
        return 0.0, f"report.json missing keys: {sorted(missing)}"
    return 1.0, None


def _check_total_transactions(wb_f, wb_d, rep, workspace_path):
    if rep is None:
        return 0.0, "report.json missing"
    got = rep.get("total_transactions")
    if got != EXPECTED["total_transactions"]:
        return 0.0, f"total_transactions: expected {EXPECTED['total_transactions']}, got {got}"
    return 1.0, None


def _check_json_total_sales(wb_f, wb_d, rep, workspace_path):
    if rep is None:
        return 0.0, "report.json missing"
    got = rep.get("total_sales")
    if not _approx(got, EXPECTED["total_sales"]):
        return 0.0, f"total_sales: expected {EXPECTED['total_sales']:.2f}, got {got}"
    return 1.0, None


def _check_json_total_commission(wb_f, wb_d, rep, workspace_path):
    if rep is None:
        return 0.0, "report.json missing"
    got = rep.get("total_commission")
    if not _approx(got, EXPECTED["total_commission"], tol=0.10):
        return 0.0, f"total_commission: expected {EXPECTED['total_commission']:.2f}, got {got}"
    return 1.0, None


def _check_quarterly_breakdown(wb_f, wb_d, rep, workspace_path):
    """quarterly_breakdown must have all 4 quarters with correct transaction counts."""
    if rep is None:
        return 0.0, "report.json missing"
    qb = rep.get("quarterly_breakdown")
    if not isinstance(qb, dict):
        return 0.0, "quarterly_breakdown is not an object"
    missing_q = QUARTERS - set(qb.keys())
    if missing_q:
        return 0.0, f"quarterly_breakdown missing quarters: {sorted(missing_q)}"
    wrong = []
    for q, exp in EXPECTED["quarterly_breakdown"].items():
        got_q = qb.get(q, {})
        if not isinstance(got_q, dict):
            wrong.append(f"{q}: not an object")
            continue
        got_count = got_q.get("transaction_count")
        if got_count != exp["transaction_count"]:
            wrong.append(f"{q} transaction_count: expected {exp['transaction_count']}, got {got_count}")
    if wrong:
        return 0.0, "; ".join(wrong)
    return 1.0, None


def _check_quarterly_sales(wb_f, wb_d, rep, workspace_path):
    """quarterly_breakdown sales values must be correct (requires correct date parsing)."""
    if rep is None:
        return 0.0, "report.json missing"
    qb = rep.get("quarterly_breakdown")
    if not isinstance(qb, dict):
        return 0.0, "quarterly_breakdown not an object"
    wrong = []
    for q, exp in EXPECTED["quarterly_breakdown"].items():
        got_q = qb.get(q, {})
        if not isinstance(got_q, dict):
            wrong.append(f"{q}: not an object")
            continue
        got_sales = got_q.get("sales")
        if not _approx(got_sales, exp["sales"]):
            wrong.append(f"{q} sales: expected {exp['sales']:.2f}, got {got_sales}")
    if wrong:
        return 0.0, "; ".join(wrong[:3])
    return 1.0, None


def _check_cross_invariant(wb_f, wb_d, rep, workspace_path):
    """Sum of quarterly transaction_count == total_transactions."""
    if rep is None:
        return 0.0, "report.json missing"
    qb = rep.get("quarterly_breakdown")
    total = rep.get("total_transactions")
    if not isinstance(qb, dict) or total is None:
        return 0.0, "quarterly_breakdown or total_transactions missing"
    q_sum = sum(q.get("transaction_count", 0) for q in qb.values() if isinstance(q, dict))
    if q_sum != total:
        return 0.0, f"Sum of quarterly transaction_count ({q_sum}) != total_transactions ({total})"
    return 1.0, None


CRITERIA = [
    {"id": "file-exists",            "weight": 0.02, "description": "commissions.xlsx exists at workspace root and is a valid XLSX file.",                                                                                                                         "check": _check_file_exists},
    {"id": "schema",                 "weight": 0.04, "description": "PayrollSummary sheet in commissions.xlsx has headers Salesperson, SalesCount, TotalSales, Commission.",                                                                                        "check": _check_schema},
    {"id": "data-row-count",         "weight": 0.03, "description": "PayrollSummary contains exactly 5 salesperson data rows, one per salesperson in the fixture.",                                                                                                  "check": _check_data_row_count},
    {"id": "sales-count",            "weight": 0.08, "description": "SalesCount per salesperson matches the fixture counts (Alice=16, Bob=12, Carol=15, David=18, Eva=19) — does not require date parsing but validates the model read all 80 rows.",               "check": _check_sales_count},
    {"id": "total-sales",            "weight": 0.15, "description": "TotalSales per salesperson matches expected sums after parsing mixed-format amounts: plain floats AND strings like '$1,234.56'. Incorrect parsing of string amounts produces wrong totals.",   "check": _check_total_sales},
    {"id": "commission",             "weight": 0.15, "description": "Commission per salesperson correct: 8% for individual transactions where amount >= 1000, 5% otherwise. The threshold applies per-transaction, not to the total.",                              "check": _check_commission},
    {"id": "totals-row-formulas",    "weight": 0.08, "description": "Totals row in PayrollSummary uses Excel SUM formulas for TotalSales and Commission columns — not hardcoded numbers.",                                                                           "check": _check_totals_row_formulas},
    {"id": "json-exists",            "weight": 0.02, "description": "report.json exists at workspace root and parses as JSON.",                                                                                                                                     "check": _check_json_exists},
    {"id": "json-schema",            "weight": 0.02, "description": "report.json has required top-level keys: total_transactions, total_sales, total_commission, quarterly_breakdown, by_salesperson.",                                                              "check": _check_json_schema},
    {"id": "total-transactions",     "weight": 0.05, "description": "report.json.total_transactions equals 80 — the total number of rows in the fixture.",                                                                                                           "check": _check_total_transactions},
    {"id": "json-total-sales",       "weight": 0.08, "description": "report.json.total_sales equals 217035.74 — the sum of all 80 transactions after parsing mixed-format amounts.",                                                                                "check": _check_json_total_sales},
    {"id": "json-total-commission",  "weight": 0.08, "description": "report.json.total_commission equals 17091.04 — the sum of per-transaction commissions using the 8%/5% tiered rate.",                                                                          "check": _check_json_total_commission},
    {"id": "quarterly-breakdown",    "weight": 0.10, "description": "report.json.quarterly_breakdown has Q1-Q4 2025 with correct transaction counts, requiring the model to correctly parse both Excel serial date integers and ISO date strings in SaleDate.",      "check": _check_quarterly_breakdown},
    {"id": "quarterly-sales",        "weight": 0.04, "description": "quarterly_breakdown sales values per quarter correct — cross-validates date parsing and amount parsing working together.",                                                                       "check": _check_quarterly_sales},
    {"id": "cross-invariant",        "weight": 0.06, "description": "Sum of quarterly_breakdown.transaction_count across all quarters equals total_transactions — a cross-field invariant ensuring the quarterly split is exhaustive and non-overlapping.",          "check": _check_cross_invariant},
]

_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"Weights sum to {_w_sum}"


def grade(transcript, workspace_path):
    wb_f, wb_d, err = _load_commissions(workspace_path)
    rep, rep_err = _load_report(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](wb_f, wb_d, rep, workspace_path)
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

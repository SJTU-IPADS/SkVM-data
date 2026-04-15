"""
Grade function for excel-xlsx_task_01.

Contract: returns a list of criterion records per grade-py-protocol.md.

Checks:
1. report.xlsx exists and is valid
2. CategoryTotals sheet has correct headers
3. CategoryTotals has exactly 4 category rows
4. ActiveItems sheet exists with correct headers
5. Only Active items in ActiveItems (count check)
6. ItemCode values in ActiveItems preserved as text strings with leading zeros
7. InventoryValue column in ActiveItems uses Excel formulas (=C*D pattern)
8. TotalInventoryCost in CategoryTotals uses Excel formulas (starts with =)
9. inventory.json exists with required keys
10. json.total_active_items == 58
11. json.total_inventory_cost correct (±0.01)
12. json.by_category has correct per-category item_count
13. Cross-check: sum of CategoryTotals.ItemCount == json.total_active_items
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

# Expected values from fixture (seed 20260412)
EXPECTED = {
    "total_active_items": 58,
    "total_inventory_cost": 2435313.75,
    "by_category": {
        "Apparel":     {"item_count": 15, "total_cost": 643393.29},
        "Electronics": {"item_count": 15, "total_cost": 636581.40},
        "Furniture":   {"item_count": 8,  "total_cost": 369365.07},
        "Outdoors":    {"item_count": 20, "total_cost": 785973.99},
    },
}

REQUIRED_JSON_KEYS = {"total_active_items", "total_inventory_cost", "by_category"}
CATEGORIES = set(EXPECTED["by_category"].keys())

CT_HEADERS = {"Category", "ItemCount", "TotalInventoryCost", "AvgUnitCost"}
AI_HEADERS = {"ItemCode", "Category", "UnitCost", "Quantity", "InventoryValue"}


def _approx(a, b, tol=0.02):
    try:
        return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=0.001)
    except (TypeError, ValueError):
        return False


def _load_report(workspace_path):
    """Load report.xlsx, returns (wb_nodataonly, wb_dataonly, error_str)."""
    path = Path(workspace_path) / "report.xlsx"
    if not path.exists():
        return None, None, "report.xlsx not found"
    try:
        import openpyxl
        wb_f = openpyxl.load_workbook(str(path), data_only=False)
        wb_d = openpyxl.load_workbook(str(path), data_only=True)
        return wb_f, wb_d, None
    except Exception as e:
        return None, None, f"report.xlsx failed to load: {e}"


def _load_json(workspace_path):
    path = Path(workspace_path) / "inventory.json"
    if not path.exists():
        return None, "inventory.json not found"
    try:
        return json.loads(path.read_text()), None
    except Exception as e:
        return None, f"inventory.json parse error: {e}"


def _check_report_exists(wb_f, wb_d, inv, workspace_path):
    if wb_f is None:
        return 0.0, "report.xlsx missing or unreadable"
    return 1.0, None


def _check_category_totals_schema(wb_f, wb_d, inv, workspace_path):
    if wb_f is None:
        return 0.0, "report.xlsx missing"
    if "CategoryTotals" not in wb_f.sheetnames:
        return 0.0, f"CategoryTotals sheet not found; found: {wb_f.sheetnames}"
    ws = wb_f["CategoryTotals"]
    # Read header row
    headers = {ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1) if ws.cell(row=1, column=c).value}
    missing = CT_HEADERS - headers
    if missing:
        return 0.0, f"CategoryTotals missing headers: {sorted(missing)}; found: {sorted(headers)}"
    return 1.0, None


def _check_category_row_count(wb_f, wb_d, inv, workspace_path):
    if wb_f is None:
        return 0.0, "report.xlsx missing"
    if "CategoryTotals" not in wb_f.sheetnames:
        return 0.0, "CategoryTotals sheet not found"
    ws = wb_f["CategoryTotals"]
    # Count non-empty data rows (skip header)
    data_rows = 0
    for row in range(2, ws.max_row + 1):
        cat_val = ws.cell(row=row, column=1).value
        if cat_val is not None and str(cat_val).strip():
            data_rows += 1
    if data_rows != 4:
        return 0.0, f"CategoryTotals has {data_rows} data rows, expected 4 (one per category)"
    return 1.0, None


def _check_active_items_sheet(wb_f, wb_d, inv, workspace_path):
    if wb_f is None:
        return 0.0, "report.xlsx missing"
    if "ActiveItems" not in wb_f.sheetnames:
        return 0.0, f"ActiveItems sheet not found; found: {wb_f.sheetnames}"
    ws = wb_f["ActiveItems"]
    headers = {ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1) if ws.cell(row=1, column=c).value}
    missing = AI_HEADERS - headers
    if missing:
        return 0.0, f"ActiveItems missing headers: {sorted(missing)}; found: {sorted(headers)}"
    return 1.0, None


def _check_active_only_count(wb_f, wb_d, inv, workspace_path):
    """ActiveItems sheet should have exactly 58 data rows (Active items only)."""
    if wb_f is None:
        return 0.0, "report.xlsx missing"
    if "ActiveItems" not in wb_f.sheetnames:
        return 0.0, "ActiveItems sheet not found"
    ws = wb_f["ActiveItems"]
    count = sum(1 for row in range(2, ws.max_row + 1)
                if ws.cell(row=row, column=1).value is not None)
    if count != EXPECTED["total_active_items"]:
        return 0.0, f"ActiveItems has {count} data rows, expected {EXPECTED['total_active_items']} (Active items only)"
    return 1.0, None


def _check_item_code_type(wb_f, wb_d, inv, workspace_path):
    """ItemCode values in ActiveItems must be strings with leading zeros (e.g. '01234')."""
    if wb_f is None:
        return 0.0, "report.xlsx missing"
    if "ActiveItems" not in wb_f.sheetnames:
        return 0.0, "ActiveItems sheet not found"
    ws = wb_f["ActiveItems"]
    # Find ItemCode column
    col_map = {}
    for c in range(1, ws.max_column + 1):
        h = ws.cell(row=1, column=c).value
        if h:
            col_map[h] = c
    ic_col = col_map.get("ItemCode")
    if ic_col is None:
        return 0.0, "ItemCode column not found in ActiveItems"
    
    bad = []
    for row in range(2, ws.max_row + 1):
        val = ws.cell(row=row, column=ic_col).value
        if val is None:
            break
        val_str = str(val)
        # All item codes in fixture start with "0" and are 5 characters
        if not val_str.startswith("0") or len(val_str) != 5:
            bad.append(f"row {row}: {val!r}")
        if len(bad) >= 3:
            break
    if bad:
        return 0.0, (
            f"ItemCode values lost leading zeros: {bad[:3]}. "
            "ItemCodes must be stored as text strings (e.g. '01234'), not integers."
        )
    return 1.0, None


def _check_inventory_value_formulas(wb_f, wb_d, inv, workspace_path):
    """InventoryValue cells in ActiveItems must be Excel formulas (start with =)."""
    if wb_f is None:
        return 0.0, "report.xlsx missing"
    if "ActiveItems" not in wb_f.sheetnames:
        return 0.0, "ActiveItems sheet not found"
    ws = wb_f["ActiveItems"]
    # Find InventoryValue column
    col_map = {}
    for c in range(1, ws.max_column + 1):
        h = ws.cell(row=1, column=c).value
        if h:
            col_map[h] = c
    iv_col = col_map.get("InventoryValue")
    if iv_col is None:
        return 0.0, "InventoryValue column not found in ActiveItems"
    
    not_formula = []
    for row in range(2, ws.max_row + 1):
        val = ws.cell(row=row, column=iv_col).value
        if val is None:
            break
        if not (isinstance(val, str) and val.startswith("=")):
            not_formula.append(f"row {row}: {val!r}")
        if len(not_formula) >= 3:
            break
    
    total_rows = sum(1 for row in range(2, ws.max_row + 1)
                     if ws.cell(row=row, column=1).value is not None)
    if not_formula:
        return 0.0, (
            f"InventoryValue is hardcoded in {len(not_formula)} checked rows "
            f"(e.g. {not_formula[0]}). Must be an Excel formula like =C2*D2."
        )
    if total_rows == 0:
        return 0.0, "No data rows found in ActiveItems"
    return 1.0, None


def _check_total_cost_formulas(wb_f, wb_d, inv, workspace_path):
    """TotalInventoryCost cells in CategoryTotals must be Excel formulas."""
    if wb_f is None:
        return 0.0, "report.xlsx missing"
    if "CategoryTotals" not in wb_f.sheetnames:
        return 0.0, "CategoryTotals sheet not found"
    ws = wb_f["CategoryTotals"]
    # Find TotalInventoryCost column
    col_map = {}
    for c in range(1, ws.max_column + 1):
        h = ws.cell(row=1, column=c).value
        if h:
            col_map[h] = c
    tc_col = col_map.get("TotalInventoryCost")
    if tc_col is None:
        return 0.0, "TotalInventoryCost column not found in CategoryTotals"
    
    not_formula = []
    for row in range(2, ws.max_row + 1):
        val = ws.cell(row=row, column=tc_col).value
        if val is None:
            break
        if not (isinstance(val, str) and val.startswith("=")):
            not_formula.append(f"row {row}: {val!r}")
    
    if not_formula:
        return 0.0, (
            f"TotalInventoryCost is hardcoded in {len(not_formula)} row(s). "
            "Must be an Excel formula (e.g. =SUMIF(...) or =E2+E3+...)."
        )
    return 1.0, None


def _check_json_exists(wb_f, wb_d, inv, workspace_path):
    if inv is None:
        return 0.0, "inventory.json missing or unparseable"
    return 1.0, None


def _check_json_schema(wb_f, wb_d, inv, workspace_path):
    if inv is None:
        return 0.0, "inventory.json missing"
    missing = REQUIRED_JSON_KEYS - set(inv.keys())
    if missing:
        return 0.0, f"inventory.json missing keys: {sorted(missing)}"
    return 1.0, None


def _check_json_total_active(wb_f, wb_d, inv, workspace_path):
    if inv is None:
        return 0.0, "inventory.json missing"
    got = inv.get("total_active_items")
    if got != EXPECTED["total_active_items"]:
        return 0.0, f"total_active_items: expected {EXPECTED['total_active_items']}, got {got}"
    return 1.0, None


def _check_json_total_cost(wb_f, wb_d, inv, workspace_path):
    if inv is None:
        return 0.0, "inventory.json missing"
    got = inv.get("total_inventory_cost")
    if not _approx(got, EXPECTED["total_inventory_cost"]):
        return 0.0, f"total_inventory_cost: expected {EXPECTED['total_inventory_cost']:.2f}, got {got}"
    return 1.0, None


def _check_json_categories(wb_f, wb_d, inv, workspace_path):
    if inv is None:
        return 0.0, "inventory.json missing"
    by_cat = inv.get("by_category")
    if not isinstance(by_cat, dict):
        return 0.0, "by_category is not an object"
    missing_cats = CATEGORIES - set(by_cat.keys())
    if missing_cats:
        return 0.0, f"by_category missing categories: {sorted(missing_cats)}"
    wrong = []
    for cat, exp in EXPECTED["by_category"].items():
        got_cat = by_cat.get(cat, {})
        got_count = got_cat.get("item_count") if isinstance(got_cat, dict) else None
        if got_count != exp["item_count"]:
            wrong.append(f"{cat} item_count: expected {exp['item_count']}, got {got_count}")
    if wrong:
        return 0.0, "; ".join(wrong)
    return 1.0, None


def _check_cross_check(wb_f, wb_d, inv, workspace_path):
    """Sum of CategoryTotals.ItemCount must equal json.total_active_items."""
    if wb_f is None or inv is None:
        return 0.0, "report.xlsx or inventory.json missing"
    if "CategoryTotals" not in wb_f.sheetnames:
        return 0.0, "CategoryTotals sheet not found"
    ws = wb_f["CategoryTotals"]
    # Find ItemCount column
    col_map = {}
    for c in range(1, ws.max_column + 1):
        h = ws.cell(row=1, column=c).value
        if h:
            col_map[h] = c
    ic_col = col_map.get("ItemCount")
    if ic_col is None:
        return 0.0, "ItemCount column not found in CategoryTotals"
    
    total = 0
    for row in range(2, ws.max_row + 1):
        val = ws.cell(row=row, column=ic_col).value
        if val is None:
            continue
        try:
            total += int(val)
        except (TypeError, ValueError):
            return 0.0, f"ItemCount in row {row} is not an integer: {val!r}"
    
    json_total = inv.get("total_active_items")
    if total != json_total:
        return 0.0, (
            f"Sum of CategoryTotals.ItemCount ({total}) != inventory.json.total_active_items ({json_total}). "
            "Cross-sheet invariant violated."
        )
    return 1.0, None


CRITERIA = [
    {"id": "report-exists",             "weight": 0.03, "description": "report.xlsx exists at workspace root and is a valid XLSX file readable by openpyxl.", "check": _check_report_exists},
    {"id": "category-totals-schema",    "weight": 0.05, "description": "CategoryTotals sheet in report.xlsx has headers: Category, ItemCount, TotalInventoryCost, AvgUnitCost.", "check": _check_category_totals_schema},
    {"id": "category-row-count",        "weight": 0.04, "description": "CategoryTotals has exactly 4 data rows — one per category (Electronics, Apparel, Furniture, Outdoors).", "check": _check_category_row_count},
    {"id": "active-items-sheet",        "weight": 0.04, "description": "ActiveItems sheet exists in report.xlsx with headers ItemCode, Category, UnitCost, Quantity, InventoryValue.", "check": _check_active_items_sheet},
    {"id": "active-only-count",         "weight": 0.15, "description": "ActiveItems sheet contains exactly 58 rows — the count of Active items in the fixture (Discontinued items must be excluded).", "check": _check_active_only_count},
    {"id": "item-code-type",            "weight": 0.15, "description": "ItemCode values in ActiveItems are preserved as 5-character text strings with leading zeros (e.g. '01234'), not integers — reflects the SKILL.md rule that leading-zero identifiers must be stored as text.", "check": _check_item_code_type},
    {"id": "inventory-value-formulas",  "weight": 0.12, "description": "InventoryValue cells in ActiveItems are Excel formulas (e.g. =C2*D2), not hardcoded numbers — models must not write computed Python results as literals.", "check": _check_inventory_value_formulas},
    {"id": "total-cost-formulas",       "weight": 0.10, "description": "TotalInventoryCost cells in CategoryTotals are Excel formulas (e.g. =SUMIF(...)), not hardcoded values — per the SKILL.md rule to write formulas rather than hardcode derived results.", "check": _check_total_cost_formulas},
    {"id": "json-exists",               "weight": 0.03, "description": "inventory.json exists at workspace root and parses as JSON.", "check": _check_json_exists},
    {"id": "json-schema",               "weight": 0.03, "description": "inventory.json contains top-level keys: total_active_items, total_inventory_cost, by_category.", "check": _check_json_schema},
    {"id": "json-total-active",         "weight": 0.06, "description": "inventory.json.total_active_items equals 58 — the exact count of Active items in the fixture after excluding Discontinued rows.", "check": _check_json_total_active},
    {"id": "json-total-cost",           "weight": 0.08, "description": "inventory.json.total_inventory_cost equals the sum of UnitCost*Quantity for all Active items (2435313.75 for this fixture).", "check": _check_json_total_cost},
    {"id": "json-categories",           "weight": 0.06, "description": "inventory.json.by_category has correct item_count per category matching only Active items: Apparel=15, Electronics=15, Furniture=8, Outdoors=20.", "check": _check_json_categories},
    {"id": "cross-check",              "weight": 0.06, "description": "Sum of CategoryTotals.ItemCount across all category rows equals inventory.json.total_active_items — a cross-artifact invariant ensuring the workbook and JSON agree on how many items were processed.", "check": _check_cross_check},
]

_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"Weights sum to {_w_sum}"


def grade(transcript, workspace_path):
    wb_f, wb_d, err = _load_report(workspace_path)
    inv, inv_err = _load_json(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](wb_f, wb_d, inv, workspace_path)
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

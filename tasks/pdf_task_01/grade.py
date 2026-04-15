"""
Grade function for pdf_task_01.

Tests correct extraction from a two-column academic PDF.
The main trap: naive page.extract_text() interleaves both columns
by Y-position; proper column-aware extraction reads each column
top-to-bottom before advancing to the next column.

A secondary trap: the body text (Section 6) states the East region
has the highest anomaly rate, but the Appendix A table shows North
at 2.00% vs East at 1.89% — the table is the authoritative source.

Expected values are hardcoded from invoice_analysis.pdf (deterministic fixture).
"""
from __future__ import annotations
import json
import math
import re
from pathlib import Path


# ---- Expected values --------------------------------------------------------

EXPECTED_PAGE_COUNT = 4

# From left-column body (Section 3, page 2 left):
EXPECTED_TOTAL_INVOICES = 14832
EXPECTED_MEAN_ITEMS     = 12.4

# From right-column body (Section 4, page 2 right):
EXPECTED_ACCURACY_OVERALL  = 94.7
EXPECTED_ACCURACY_LOWEST   = 81.3
EXPECTED_ACCURACY_HIGHEST  = 99.1

# From right-column body (Section 5, page 2 right):
EXPECTED_ANOMALY_FLAG_RATE = 1.27
EXPECTED_ANOMALY_PRECISION = 0.912
EXPECTED_ANOMALY_RECALL    = 0.74

# From left-column body (Section 7, page 3 left):
EXPECTED_RAW_MATERIALS_PCT   = 31.4
EXPECTED_OFFICE_SUPPLIES_PCT = 18.7

# From left-column body (Section 8, page 3 left):
EXPECTED_PROCESSING_MANUAL    = 8.3
EXPECTED_PROCESSING_AUTOMATED = 5.4

# From Appendix A table (page 4):
EXPECTED_REGIONS              = {"North", "South", "East", "West"}
EXPECTED_NORTH_INVOICES       = 4120
EXPECTED_NORTH_ANOMALIES      = 1021
EXPECTED_EAST_ANOMALY_RATE    = 1.89
EXPECTED_WEST_ACCURACY        = 95.8
EXPECTED_HIGHEST_ANOMALY_REGION = "North"
EXPECTED_LOWEST_ANOMALY_REGION  = "West"
EXPECTED_TABLE_TOTAL_INVOICES   = 14832
EXPECTED_TABLE_TOTAL_ANOMALIES  = 2718

REQUIRED_TOP_KEYS = {
    "page_count", "data_collection", "classification_accuracy",
    "anomaly_detection", "cost_categories", "processing_time",
    "regional_table", "highest_anomaly_rate_region",
    "lowest_anomaly_rate_region", "table_total_invoices",
}


def _approx(a, b, tol=0.05):
    if a is None or b is None:
        return False
    try:
        return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)
    except (TypeError, ValueError):
        return False


def _load(workspace_path):
    p = Path(workspace_path) / "report.json"
    if not p.exists():
        return None, "report.json not found"
    try:
        return json.loads(p.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"report.json not valid JSON: {e}"


# ---- Criterion checks -------------------------------------------------------

def _check_json_exists(r):
    if r is None:
        return 0.0, "report.json missing or unparseable"
    return 1.0, None


def _check_json_schema(r):
    if r is None:
        return 0.0, "report.json missing"
    missing = REQUIRED_TOP_KEYS - set(r.keys())
    if missing:
        return 0.0, f"missing top-level keys: {sorted(missing)}"
    return 1.0, None


def _check_page_count(r):
    if r is None:
        return 0.0, "report.json missing"
    got = r.get("page_count")
    if got != EXPECTED_PAGE_COUNT:
        return 0.0, f"page_count: expected {EXPECTED_PAGE_COUNT}, got {got}"
    return 1.0, None


def _check_total_invoices_left_col(r):
    if r is None:
        return 0.0, "report.json missing"
    dc = r.get("data_collection") or {}
    got = dc.get("total_invoices")
    if got != EXPECTED_TOTAL_INVOICES:
        return 0.0, (
            f"data_collection.total_invoices: expected {EXPECTED_TOTAL_INVOICES}, got {got}. "
            "This statistic is in Section 3 (Data Collection) in the LEFT column of page 2."
        )
    return 1.0, None


def _check_mean_items_left_col(r):
    if r is None:
        return 0.0, "report.json missing"
    dc = r.get("data_collection") or {}
    got = dc.get("mean_items_per_invoice")
    if not _approx(got, EXPECTED_MEAN_ITEMS, tol=0.01):
        return 0.0, f"data_collection.mean_items_per_invoice: expected {EXPECTED_MEAN_ITEMS}, got {got}"
    return 1.0, None


def _check_accuracy_right_col(r):
    if r is None:
        return 0.0, "report.json missing"
    ca = r.get("classification_accuracy") or {}
    problems = []
    checks = [
        ("overall_pct", EXPECTED_ACCURACY_OVERALL),
        ("lowest_pct",  EXPECTED_ACCURACY_LOWEST),
        ("highest_pct", EXPECTED_ACCURACY_HIGHEST),
    ]
    for key, want in checks:
        got = ca.get(key)
        if not _approx(got, want, tol=0.01):
            problems.append(f"classification_accuracy.{key}: expected {want}, got {got}")
    if problems:
        return 0.0, "; ".join(problems) + " (Section 4 is in the RIGHT column of page 2)"
    return 1.0, None


def _check_anomaly_stats_right_col(r):
    if r is None:
        return 0.0, "report.json missing"
    ad = r.get("anomaly_detection") or {}
    problems = []
    checks = [
        ("flag_rate_pct", EXPECTED_ANOMALY_FLAG_RATE),
        ("precision",     EXPECTED_ANOMALY_PRECISION),
        ("recall",        EXPECTED_ANOMALY_RECALL),
    ]
    for key, want in checks:
        got = ad.get(key)
        if not _approx(got, want, tol=0.01):
            problems.append(f"anomaly_detection.{key}: expected {want}, got {got}")
    if problems:
        return 0.0, "; ".join(problems) + " (Section 5 is in the RIGHT column of page 2)"
    return 1.0, None


def _check_cost_categories_left_col(r):
    if r is None:
        return 0.0, "report.json missing"
    cc = r.get("cost_categories") or {}
    problems = []
    checks = [
        ("raw_materials_pct",   EXPECTED_RAW_MATERIALS_PCT),
        ("office_supplies_pct", EXPECTED_OFFICE_SUPPLIES_PCT),
    ]
    for key, want in checks:
        got = cc.get(key)
        if not _approx(got, want, tol=0.01):
            problems.append(f"cost_categories.{key}: expected {want}, got {got}")
    if problems:
        return 0.0, "; ".join(problems) + " (Section 7 is in the LEFT column of page 3)"
    return 1.0, None


def _check_processing_time_left_col(r):
    if r is None:
        return 0.0, "report.json missing"
    pt = r.get("processing_time") or {}
    problems = []
    checks = [
        ("manual_minutes",    EXPECTED_PROCESSING_MANUAL),
        ("automated_minutes", EXPECTED_PROCESSING_AUTOMATED),
    ]
    for key, want in checks:
        got = pt.get(key)
        if not _approx(got, want, tol=0.01):
            problems.append(f"processing_time.{key}: expected {want}, got {got}")
    if problems:
        return 0.0, "; ".join(problems) + " (Section 8 is in the LEFT column of page 3)"
    return 1.0, None


def _check_regional_table_structure(r):
    if r is None:
        return 0.0, "report.json missing"
    rt = r.get("regional_table")
    if not isinstance(rt, dict):
        return 0.0, "regional_table is not an object"
    missing = EXPECTED_REGIONS - set(rt.keys())
    if missing:
        return 0.0, f"regional_table missing regions: {sorted(missing)}"
    required_fields = {"invoices", "line_items", "anomalies", "anomaly_rate_pct", "accuracy_pct"}
    for region in EXPECTED_REGIONS:
        row = rt.get(region) or {}
        missing_fields = required_fields - set(row.keys())
        if missing_fields:
            return 0.0, f"regional_table.{region} missing fields: {sorted(missing_fields)}"
    return 1.0, None


def _check_regional_table_values(r):
    if r is None:
        return 0.0, "report.json missing"
    rt = r.get("regional_table") or {}
    north = rt.get("North") or {}
    east  = rt.get("East") or {}
    west  = rt.get("West") or {}
    problems = []
    if north.get("invoices") != EXPECTED_NORTH_INVOICES:
        problems.append(f"North invoices: expected {EXPECTED_NORTH_INVOICES}, got {north.get('invoices')}")
    if north.get("anomalies") != EXPECTED_NORTH_ANOMALIES:
        problems.append(f"North anomalies: expected {EXPECTED_NORTH_ANOMALIES}, got {north.get('anomalies')}")
    if not _approx(east.get("anomaly_rate_pct"), EXPECTED_EAST_ANOMALY_RATE, tol=0.01):
        problems.append(f"East anomaly_rate_pct: expected {EXPECTED_EAST_ANOMALY_RATE}, got {east.get('anomaly_rate_pct')}")
    if not _approx(west.get("accuracy_pct"), EXPECTED_WEST_ACCURACY, tol=0.01):
        problems.append(f"West accuracy_pct: expected {EXPECTED_WEST_ACCURACY}, got {west.get('accuracy_pct')}")
    if problems:
        return 0.0, "; ".join(problems)
    return 1.0, None


def _check_highest_anomaly_region(r):
    if r is None:
        return 0.0, "report.json missing"
    got = r.get("highest_anomaly_rate_region")
    if got != EXPECTED_HIGHEST_ANOMALY_REGION:
        return 0.0, (
            f"highest_anomaly_rate_region: expected {EXPECTED_HIGHEST_ANOMALY_REGION!r}, got {got!r}. "
            "The Appendix A table on page 4 shows North at 2.00% and East at 1.89%; "
            "Section 6 in the body text is inconsistent with the table — use the table."
        )
    return 1.0, None


def _check_table_totals_invariant(r):
    if r is None:
        return 0.0, "report.json missing"
    reported_total = r.get("table_total_invoices")
    rt = r.get("regional_table") or {}
    try:
        computed = sum(rt[reg]["invoices"] for reg in ["North", "South", "East", "West"])
    except (KeyError, TypeError):
        return 0.0, "could not sum regional invoices (missing region or invoices field)"
    if reported_total != EXPECTED_TABLE_TOTAL_INVOICES:
        return 0.0, f"table_total_invoices: expected {EXPECTED_TABLE_TOTAL_INVOICES}, got {reported_total}"
    if computed != EXPECTED_TABLE_TOTAL_INVOICES:
        return 0.0, f"sum of regional invoices: expected {EXPECTED_TABLE_TOTAL_INVOICES}, got {computed}"
    return 1.0, None


# ---- CRITERIA registry -------------------------------------------------------

CRITERIA = [
    {
        "id": "json-exists",
        "weight": 0.04,
        "description": "report.json exists at the workspace root and parses as valid JSON.",
        "check": _check_json_exists,
    },
    {
        "id": "json-schema",
        "weight": 0.06,
        "description": "report.json contains all required top-level keys: page_count, data_collection, classification_accuracy, anomaly_detection, cost_categories, processing_time, regional_table, highest_anomaly_rate_region, lowest_anomaly_rate_region, table_total_invoices.",
        "check": _check_json_schema,
    },
    {
        "id": "page-count",
        "weight": 0.05,
        "description": "page_count field equals 4, matching the total pages in invoice_analysis.pdf (title page + 2 body pages + appendix table page).",
        "check": _check_page_count,
    },
    {
        "id": "total-invoices-left-col",
        "weight": 0.10,
        "description": "data_collection.total_invoices equals 14832, extracted from Section 3 (Data Collection) which is in the LEFT column of page 2. Naive full-page text extraction by Y-position interleaves both columns, causing this statistic to be buried between right-column Section 4 and 5 content.",
        "check": _check_total_invoices_left_col,
    },
    {
        "id": "mean-items-left-col",
        "weight": 0.07,
        "description": "data_collection.mean_items_per_invoice equals 12.4, from Section 3 (Data Collection) in the LEFT column of page 2.",
        "check": _check_mean_items_left_col,
    },
    {
        "id": "accuracy-right-col",
        "weight": 0.12,
        "description": "classification_accuracy.overall_pct=94.7, lowest_pct=81.3, highest_pct=99.1 — all from Section 4 (Performance Metrics) in the RIGHT column of page 2. Without bbox-based column splitting, these values appear interleaved with left-column Section 1-3 content.",
        "check": _check_accuracy_right_col,
    },
    {
        "id": "anomaly-right-col",
        "weight": 0.12,
        "description": "anomaly_detection.flag_rate_pct=1.27, precision=0.912, recall=0.74 — from Section 5 (Anomaly Detection) in the RIGHT column of page 2. Incorrect column order causes these to appear mixed with Section 2 (System Architecture) content from the left column.",
        "check": _check_anomaly_stats_right_col,
    },
    {
        "id": "cost-categories-left-col",
        "weight": 0.08,
        "description": "cost_categories.raw_materials_pct=31.4, office_supplies_pct=18.7 — from Section 7 (Cost Category Distribution) in the LEFT column of page 3.",
        "check": _check_cost_categories_left_col,
    },
    {
        "id": "processing-time-left-col",
        "weight": 0.08,
        "description": "processing_time.manual_minutes=8.3, automated_minutes=5.4 — from Section 8 (Processing Time Analysis) in the LEFT column of page 3.",
        "check": _check_processing_time_left_col,
    },
    {
        "id": "regional-table-structure",
        "weight": 0.08,
        "description": "regional_table is a JSON object with exactly 4 region keys (North, South, East, West), each containing invoices, line_items, anomalies, anomaly_rate_pct, accuracy_pct — extracted from the Appendix A table on page 4.",
        "check": _check_regional_table_structure,
    },
    {
        "id": "regional-table-values",
        "weight": 0.10,
        "description": "regional_table values match the Appendix A table: North 4120 invoices/1021 anomalies; East anomaly_rate_pct=1.89; West accuracy_pct=95.8. Body-text regional numbers differ from the table (a deliberate fixture property); the table is authoritative.",
        "check": _check_regional_table_values,
    },
    {
        "id": "highest-anomaly-region",
        "weight": 0.07,
        "description": "highest_anomaly_rate_region equals 'North' per the Appendix A table (North 2.00% > East 1.89%). Section 6 in the body text incorrectly states East has the highest rate — agents who read the narrative instead of computing from the table will get this wrong.",
        "check": _check_highest_anomaly_region,
    },
    {
        "id": "table-totals-invariant",
        "weight": 0.03,
        "description": "table_total_invoices (14832) equals the sum of regional invoice counts from regional_table — a cross-field invariant confirming the agent's table extraction is internally consistent.",
        "check": _check_table_totals_invariant,
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

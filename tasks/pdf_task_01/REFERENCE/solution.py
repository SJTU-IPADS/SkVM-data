"""
Reference solution for pdf_task_01.

Reads invoice_analysis.pdf from cwd and produces report.json.
Uses pdfplumber with bbox-based two-column extraction for body pages.
The PDF has a two-column layout on pages 2-3; correct extraction reads
the full left column first, then the full right column (not interleaved).
"""
import json
import re
from pathlib import Path
import pdfplumber

PDF_PATH = "invoice_analysis.pdf"


def col_text(page, x_split):
    h = page.height
    w = page.width
    left  = page.within_bbox((0, 0, x_split, h)).extract_text() or ""
    right = page.within_bbox((x_split, 0, w, h)).extract_text() or ""
    return left, right


def num(text, pattern):
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        return None
    raw = m.group(1).replace(",", "")
    try:
        return float(raw) if "." in raw else int(raw)
    except ValueError:
        return None


with pdfplumber.open(PDF_PATH) as pdf:
    page_count = len(pdf.pages)
    X = 306  # mid-point of 612pt letter page

    left2, right2 = col_text(pdf.pages[1], X)
    left3, right3 = col_text(pdf.pages[2], X)
    body_left  = left2 + "\n" + left3
    body_right = right2 + "\n" + right3

    # From left column body:
    total_invoices_in_text   = num(body_left, r"([\d,]+) invoices were")
    mean_items               = num(body_left, r"mean of (\d+\.\d+) items per invoice")
    raw_materials_pct        = num(body_left, r"raw materials,\naccounting for (\d+\.\d+)%")
    office_supplies_pct      = num(body_left, r"[Oo]ffice supplies\nrepresented (\d+\.\d+)%")
    processing_manual_min    = num(body_left, r"decreased from (\d+\.\d+)\nminutes \(manual baseline\)")
    processing_auto_min      = num(body_left, r"to (\d+\.\d+) minutes \(automated\npipeline\)")
    processing_reduction_pct = num(body_left, r"reduction of (\d+\.\d+)%")

    # From right column body:
    accuracy_overall_pct     = num(body_right, r"(\d+\.\d+)% item-level accuracy")
    accuracy_lowest_pct      = num(body_right, r"miscellaneous services at (\d+\.\d+)%")
    accuracy_highest_pct     = num(body_right, r"utility charges at (\d+\.\d+)%")
    anomaly_flag_rate_pct    = num(body_right, r"flag rate of\n(\d+\.\d+)%")
    anomaly_precision        = num(body_right, r"precision of (\d+\.\d+)")
    anomaly_recall           = num(body_right, r"Recall\nwas estimated at (\d+\.\d+)")

    # Table on page 4:
    tables = pdf.pages[3].extract_tables()
    tbl = tables[0]

    def clean_int(s):
        return int(re.sub(r"[,\s]", "", s))

    def clean_pct(s):
        return float(s.replace("%", "").strip())

    regions = {}
    for row in tbl[1:]:
        if row[0] and row[0].lower() != "total":
            name = row[0].strip()
            regions[name] = {
                "invoices": clean_int(row[1]),
                "line_items": clean_int(row[2]),
                "anomalies": clean_int(row[3]),
                "anomaly_rate_pct": clean_pct(row[4]),
                "accuracy_pct": clean_pct(row[5]),
            }

    total_invoices_table  = sum(r["invoices"] for r in regions.values())
    total_anomalies_table = sum(r["anomalies"] for r in regions.values())
    highest_anomaly_region = max(regions, key=lambda r: regions[r]["anomaly_rate_pct"])
    lowest_anomaly_region  = min(regions, key=lambda r: regions[r]["anomaly_rate_pct"])

report = {
    "page_count": page_count,
    "data_collection": {
        "total_invoices": total_invoices_in_text,
        "mean_items_per_invoice": mean_items,
    },
    "classification_accuracy": {
        "overall_pct": accuracy_overall_pct,
        "lowest_pct": accuracy_lowest_pct,
        "highest_pct": accuracy_highest_pct,
    },
    "anomaly_detection": {
        "flag_rate_pct": anomaly_flag_rate_pct,
        "precision": anomaly_precision,
        "recall": anomaly_recall,
    },
    "cost_categories": {
        "raw_materials_pct": raw_materials_pct,
        "office_supplies_pct": office_supplies_pct,
    },
    "processing_time": {
        "manual_minutes": processing_manual_min,
        "automated_minutes": processing_auto_min,
        "reduction_pct": processing_reduction_pct,
    },
    "regional_table": regions,
    "highest_anomaly_rate_region": highest_anomaly_region,
    "lowest_anomaly_rate_region": lowest_anomaly_region,
    "table_total_invoices": total_invoices_table,
    "table_total_anomalies": total_anomalies_table,
}

Path("report.json").write_text(json.dumps(report, indent=2))
print("Written: report.json")

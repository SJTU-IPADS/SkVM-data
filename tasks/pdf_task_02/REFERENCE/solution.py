"""
Reference solution for pdf_task_02.

Reads budget_report.pdf from cwd and produces summary.json.

Key challenges:
1. Engineering page has a SUBTOTAL row that must be EXCLUDED from department total
   computation (only use the DEPARTMENT TOTAL row, not sum of line items).
2. Operations budget spans pages 4 and 5; the DEPARTMENT TOTAL is on page 5.
3. The company roll-up on page 7 must NOT be used for extraction.
4. grand_total in the output must equal the sum of the four department totals.
"""
import json
import re
from pathlib import Path
import pdfplumber

PDF_PATH = "budget_report.pdf"


def parse_amount(s):
    """Parse '$1,234,000' -> 1234000."""
    if not s:
        return None
    clean = re.sub(r"[$,\s]", "", s)
    try:
        return int(clean)
    except ValueError:
        return None


def extract_dept_total_from_table(tbl):
    """
    Extract the DEPARTMENT TOTAL from a table.
    The DEPARTMENT TOTAL row is the last row with 'DEPARTMENT TOTAL' in column 0.
    Returns (annual_total, line_item_count) where line_item_count excludes
    SUBTOTAL and DEPARTMENT TOTAL rows.
    """
    dept_total = None
    line_item_count = 0
    for row in tbl[1:]:  # skip header
        cat = (row[0] or "").strip()
        if cat.startswith("DEPARTMENT TOTAL"):
            dept_total = parse_amount(row[5])  # Annual column (index 5)
        elif cat.startswith("SUBTOTAL") or cat.startswith("(Continued"):
            pass  # skip subtotals and continuation markers
        elif cat:
            line_item_count += 1
    return dept_total, line_item_count


with pdfplumber.open(PDF_PATH) as pdf:
    page_count = len(pdf.pages)

    # Page 2: Engineering (has SUBTOTAL row — use DEPARTMENT TOTAL, not sum of line items)
    eng_tbl = pdf.pages[1].extract_tables()[0]
    eng_total, eng_line_items = extract_dept_total_from_table(eng_tbl)

    # Count SUBTOTAL rows in Engineering (trap marker)
    eng_subtotal_rows = sum(
        1 for row in eng_tbl[1:]
        if (row[0] or "").strip().startswith("SUBTOTAL")
    )

    # Page 3: Marketing
    mkt_tbl = pdf.pages[2].extract_tables()[0]
    mkt_total, mkt_line_items = extract_dept_total_from_table(mkt_tbl)

    # Pages 4-5: Operations (DEPARTMENT TOTAL is on page 5)
    # Page 4 has a "(Continued on next page)" row, no DEPARTMENT TOTAL
    ops_tbl_p4 = pdf.pages[3].extract_tables()[0]
    ops_tbl_p5 = pdf.pages[4].extract_tables()[0]

    # Count line items across both pages
    ops_line_items_p4 = sum(
        1 for row in ops_tbl_p4[1:]
        if (row[0] or "").strip()
        and not (row[0] or "").strip().startswith(("DEPARTMENT", "SUBTOTAL", "("))
    )
    ops_total, ops_line_items_p5 = extract_dept_total_from_table(ops_tbl_p5)
    ops_line_items = ops_line_items_p4 + ops_line_items_p5

    # Page 6: Human Resources
    hr_tbl = pdf.pages[5].extract_tables()[0]
    hr_total, hr_line_items = extract_dept_total_from_table(hr_tbl)

    # Grand total (compute from department totals, do NOT read from page 7)
    grand_total = eng_total + mkt_total + ops_total + hr_total

    summary = {
        "page_count": page_count,
        "departments": {
            "Engineering": {
                "annual_budget": eng_total,
                "line_item_count": eng_line_items,
                "source_pages": [2],
                "subtotal_rows_present": eng_subtotal_rows,
            },
            "Marketing": {
                "annual_budget": mkt_total,
                "line_item_count": mkt_line_items,
                "source_pages": [3],
                "subtotal_rows_present": 0,
            },
            "Operations": {
                "annual_budget": ops_total,
                "line_item_count": ops_line_items,
                "source_pages": [4, 5],
                "subtotal_rows_present": 0,
            },
            "Human Resources": {
                "annual_budget": hr_total,
                "line_item_count": hr_line_items,
                "source_pages": [6],
                "subtotal_rows_present": 0,
            },
        },
        "grand_total": grand_total,
    }

Path("summary.json").write_text(json.dumps(summary, indent=2))
print("Written: summary.json")
print(json.dumps(summary, indent=2))

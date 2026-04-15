"""
_gen_fixture.py for document-pdf_task_02.

Generates ledger.pdf — a 2-page PDF with financial transaction tables.
Run from the fixtures/ directory:
    cd fixtures && python3 _gen_fixture.py

random.seed(20260412) ensures deterministic output.

The generated ledger.pdf is committed as a static fixture.
This script is kept for reproducibility but is NOT re-executed at task time.

Design:
  - Page 1: Q3 2025 transactions (12 rows, txn_ids TXN-1001 to TXN-1012)
  - Page 2: Q4 2025 transactions (10 rows, txn_ids TXN-2001 to TXN-2010)
  - Injected duplicates: TXN-1004 and TXN-1008 appear on page 2 with different amounts
  - One row (TXN-2005) has an empty description field
  - Amounts formatted as $X,XXX.XX (require $ and comma stripping before parsing)
"""
from __future__ import annotations

import random
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas

random.seed(20260412)

CATEGORIES = ["Operations", "Marketing", "Engineering", "Finance", "HR"]
DESCRIPTIONS = [
    "Cloud infrastructure invoice",
    "Software license renewal",
    "Team offsite expenses",
    "External consultant fee",
    "Office supplies",
    "Marketing campaign spend",
    "Recruitment agency fee",
    "Hardware procurement",
    "Legal advisory services",
    "Training programme",
    "Travel & accommodation",
    "Vendor payment",
    "Contractor invoice",
    "Subscription renewal",
    "Equipment maintenance",
]


def make_amount(category: str) -> float:
    ranges = {
        "Operations":  (500, 8000),
        "Marketing":   (200, 5000),
        "Engineering": (1000, 15000),
        "Finance":     (300, 3000),
        "HR":          (500, 12000),
    }
    lo, hi = ranges[category]
    return round(random.uniform(lo, hi), 2)


def make_date(page: int) -> str:
    if page == 1:
        month = random.choice(["07", "08", "09"])
    else:
        month = random.choice(["10", "11", "12"])
    day = random.randint(1, 28)
    return f"2025-{month}-{day:02d}"


def gen_rows(page: int, start_id: int, count: int) -> list[dict]:
    rows = []
    for i in range(count):
        txn_id = f"TXN-{start_id + i:04d}"
        cat = random.choice(CATEGORIES)
        rows.append({
            "txn_id": txn_id,
            "date": make_date(page),
            "description": random.choice(DESCRIPTIONS),
            "amount": make_amount(cat),
            "category": cat,
        })
    return rows


def format_amount(amt: float) -> str:
    return f"${amt:,.2f}"


def draw_table(c, rows: list[dict], title: str, top_y: float, page_w: float, page_h: float) -> None:
    lm = 20 * mm
    rm = page_w - 20 * mm
    table_w = rm - lm

    col_widths = [0.14, 0.14, 0.36, 0.18, 0.18]
    col_xs = [lm]
    for frac in col_widths[:-1]:
        col_xs.append(col_xs[-1] + frac * table_w)

    headers = ["Txn ID", "Date", "Description", "Amount", "Category"]
    row_h = 7 * mm
    header_h = 8 * mm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(lm, top_y, title)
    y = top_y - 6 * mm

    c.setFillColorRGB(0.2, 0.2, 0.6)
    c.rect(lm, y - header_h + 2 * mm, table_w, header_h, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 9)
    for hdr, cx in zip(headers, col_xs):
        c.drawString(cx + 1 * mm, y - header_h + 4 * mm, hdr)

    y -= header_h
    c.setFillColorRGB(0, 0, 0)

    for ri, row in enumerate(rows):
        bg = 0.95 if ri % 2 == 0 else 1.0
        c.setFillColorRGB(bg, bg, bg)
        c.rect(lm, y - row_h + 2 * mm, table_w, row_h, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 8)
        vals = [
            row["txn_id"],
            row["date"],
            row["description"],
            format_amount(row["amount"]),
            row["category"],
        ]
        for val, cx in zip(vals, col_xs):
            if len(val) > 32:
                val = val[:29] + "..."
            c.drawString(cx + 1 * mm, y - row_h + 4 * mm, val)
        y -= row_h

    total_h = header_h + row_h * len(rows)
    c.rect(lm, top_y - 6 * mm - total_h, table_w, total_h, fill=0, stroke=1)


def main() -> None:
    page1_rows = gen_rows(1, 1001, 12)
    page2_rows = gen_rows(2, 2001, 10)

    # Inject duplicates: rows 2 and 6 on page 2 reuse txn_ids from page 1
    dupe_ids = [page1_rows[3]["txn_id"], page1_rows[7]["txn_id"]]
    page2_rows[2]["txn_id"] = dupe_ids[0]
    page2_rows[6]["txn_id"] = dupe_ids[1]
    page2_rows[2]["amount"] = round(page2_rows[2]["amount"] * 1.5, 2)
    page2_rows[6]["amount"] = round(page2_rows[6]["amount"] * 2.0, 2)

    # One row with empty description (pdfplumber edge case)
    page2_rows[4]["description"] = ""

    c = pdfcanvas.Canvas("ledger.pdf", pagesize=A4)
    w, h = A4

    # Page 1
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, h - 18 * mm, "Acme Technologies — Q3 2025 Ledger (Jul\u2013Sep)")
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, h - 26 * mm, "Prepared by Finance Team | Confidential")
    c.line(20 * mm, h - 29 * mm, w - 20 * mm, h - 29 * mm)
    draw_table(c, page1_rows, "Q3 2025 Transactions", h - 38 * mm, w, h)
    c.setFont("Helvetica", 8)
    c.drawString(20 * mm, 12 * mm, "Page 1 of 2 \u2014 Acme Technologies Ledger Report")
    c.showPage()

    # Page 2
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, h - 18 * mm, "Acme Technologies — Q4 2025 Ledger (Oct\u2013Dec)")
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, h - 26 * mm, "Prepared by Finance Team | Confidential")
    c.line(20 * mm, h - 29 * mm, w - 20 * mm, h - 29 * mm)
    draw_table(c, page2_rows, "Q4 2025 Transactions", h - 38 * mm, w, h)
    c.setFont("Helvetica", 8)
    c.drawString(20 * mm, 12 * mm, "Page 2 of 2 \u2014 Acme Technologies Ledger Report")
    c.showPage()

    c.save()
    print(f"ledger.pdf written")
    print(f"Duplicate txn_ids injected: {dupe_ids}")
    print(f"Empty description row: {page2_rows[4]['txn_id']}")


if __name__ == "__main__":
    main()

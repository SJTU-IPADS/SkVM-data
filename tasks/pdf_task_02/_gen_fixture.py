"""
_gen_fixture.py for pdf_task_02

Generates a deterministic multi-page budget report PDF:
- Page 1: Cover page
- Page 2: Engineering department budget table (10 line items + SUBTOTAL row)
- Page 3: Marketing department budget table (8 line items)
- Pages 4-5: Operations department budget table (12 line items spanning 2 pages)
- Page 6: HR department budget table (6 line items)
- Page 7: Summary / totals page (DON'T use for extraction — it's a roll-up)

Each department table has: Category, Q1, Q2, Q3, Q4, Annual columns
Annual = Q1+Q2+Q3+Q4 for each line item
SUBTOTAL rows appear at section breaks within Engineering (trap: don't double-count)
The "Annual" values for non-subtotal rows are what should be summed.

Seed: 20260412
"""
import random
random.seed(20260412)

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table as RLTable, TableStyle

W, H = letter

def make_budget_rows(categories, seed_offset):
    """Generate quarterly budget values for a list of categories."""
    rng = random.Random(20260412 + seed_offset)
    rows = []
    for cat in categories:
        q1 = rng.randint(10, 80) * 1000
        q2 = rng.randint(10, 80) * 1000
        q3 = rng.randint(10, 80) * 1000
        q4 = rng.randint(10, 80) * 1000
        annual = q1 + q2 + q3 + q4
        rows.append((cat, q1, q2, q3, q4, annual))
    return rows

def fmt(n):
    return f"${n:,}"

def draw_dept_table(c, page_num, dept_name, rows, include_subtotal=None, y_start=None, note=None):
    """Draw a department budget table on the current canvas page."""
    margin = 0.75 * inch

    if y_start is None:
        y_start = H - 1.2 * inch

    # Department header
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#1F3864"))
    c.drawString(margin, y_start, f"{dept_name} Department — 2026 Budget")
    c.setFillColor(colors.black)

    y_start -= 0.1 * inch

    # Build table data
    header = ["Category", "Q1", "Q2", "Q3", "Q4", "Annual"]
    tbl_data = [header]
    for row in rows:
        cat, q1, q2, q3, q4, annual = row
        tbl_data.append([cat, fmt(q1), fmt(q2), fmt(q3), fmt(q4), fmt(annual)])

    if include_subtotal:
        # Add a SUBTOTAL row mid-table (after first half of rows)
        mid = len(rows) // 2
        sub_annual = sum(r[5] for r in rows[:mid])
        sub_q1 = sum(r[1] for r in rows[:mid])
        sub_q2 = sum(r[2] for r in rows[:mid])
        sub_q3 = sum(r[3] for r in rows[:mid])
        sub_q4 = sum(r[4] for r in rows[:mid])
        subtotal_row = ["SUBTOTAL (Personnel)", fmt(sub_q1), fmt(sub_q2), fmt(sub_q3), fmt(sub_q4), fmt(sub_annual)]
        tbl_data.insert(mid + 1, subtotal_row)  # +1 for header

    # Total row
    total_annual = sum(r[5] for r in rows)
    total_q1 = sum(r[1] for r in rows)
    total_q2 = sum(r[2] for r in rows)
    total_q3 = sum(r[3] for r in rows)
    total_q4 = sum(r[4] for r in rows)
    tbl_data.append(["DEPARTMENT TOTAL", fmt(total_q1), fmt(total_q2), fmt(total_q3), fmt(total_q4), fmt(total_annual)])

    col_widths = [2.3*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch]
    table = RLTable(tbl_data, colWidths=col_widths)

    # Style: header = dark blue, subtotal = light yellow, total = dark blue
    style = [
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F3864")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
        ("ALIGN", (1,0), (-1,-1), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        # Total row
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#1F3864")),
        ("TEXTCOLOR", (0,-1), (-1,-1), colors.white),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        # Alternating rows
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [colors.white, colors.HexColor("#E8EDF5")]),
    ]

    # If there's a subtotal row, highlight it
    if include_subtotal:
        mid_idx = len(rows)//2 + 1  # position in tbl_data (after header, after mid rows)
        style.append(("BACKGROUND", (0, mid_idx), (-1, mid_idx), colors.HexColor("#FFF2CC")))
        style.append(("FONTNAME", (0, mid_idx), (-1, mid_idx), "Helvetica-Bold"))

    table.setStyle(TableStyle(style))

    avail_w = W - 2 * margin
    table.wrapOn(c, avail_w, H)
    tw, th = table.wrap(0, 0)

    table.drawOn(c, margin, y_start - th)

    if note:
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin, y_start - th - 0.15*inch, note)
        c.setFillColor(colors.black)

    # Page number
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(W/2, 0.4*inch, f"Page {page_num}")
    c.setFillColor(colors.black)

    return total_annual, y_start - th  # return total and bottom y position


OUTPUT = "budget_report.pdf"
c = canvas.Canvas(OUTPUT, pagesize=letter)

# ---- Page 1: Cover ----
c.setFont("Helvetica-Bold", 22)
c.setFillColor(colors.HexColor("#1F3864"))
c.drawCentredString(W/2, H*0.72, "Meridian Technologies Inc.")
c.setFont("Helvetica-Bold", 16)
c.drawCentredString(W/2, H*0.65, "Annual Department Budget Report — FY 2026")
c.setFillColor(colors.black)
c.setFont("Helvetica", 12)
c.drawCentredString(W/2, H*0.58, "Prepared by the Finance Committee | April 2026")
c.setFont("Helvetica", 10)
lines = [
    "This report summarizes the approved annual budget allocations for each department.",
    "Budget figures are presented by quarter (Q1-Q4) and annual total.",
    "Subtotal rows are included within the Engineering section for personnel vs. non-personnel costs.",
    "The DEPARTMENT TOTAL row in each section reflects the full departmental allocation",
    "and is the authoritative figure for roll-up calculations.",
    "",
    "Departments covered: Engineering, Marketing, Operations, Human Resources",
]
y = H*0.50
for line in lines:
    c.drawCentredString(W/2, y, line)
    y -= 16

c.setFont("Helvetica", 8)
c.setFillColor(colors.grey)
c.drawCentredString(W/2, 0.4*inch, "Page 1")
c.setFillColor(colors.black)
c.showPage()

# ---- Page 2: Engineering (with SUBTOTAL row as a trap) ----
eng_cats = [
    "Software Engineering Salaries",
    "Platform Engineering Salaries",
    "DevOps Salaries",
    "QA Salaries",
    "Engineering Management",
    "Cloud Infrastructure",
    "Software Licenses",
    "Hardware & Equipment",
    "Training & Conferences",
    "Contractor Costs",
]
eng_rows = make_budget_rows(eng_cats, seed_offset=1)
eng_total, _ = draw_dept_table(
    c, 2, "Engineering", eng_rows,
    include_subtotal=True,
    note="Note: SUBTOTAL row covers Personnel costs only (first 5 line items). Do not include in department total computation."
)
c.showPage()

# ---- Page 3: Marketing ----
mkt_cats = [
    "Marketing Salaries",
    "Digital Advertising",
    "Events & Sponsorships",
    "Content Production",
    "Market Research",
    "Brand & Creative",
    "PR & Communications",
    "Marketing Technology",
]
mkt_rows = make_budget_rows(mkt_cats, seed_offset=2)
mkt_total, _ = draw_dept_table(c, 3, "Marketing", mkt_rows)
c.showPage()

# ---- Pages 4-5: Operations (spans 2 pages) ----
ops_cats_p1 = [
    "Operations Salaries",
    "Facilities & Rent",
    "Office Supplies",
    "Utilities",
    "Security Services",
    "Logistics & Shipping",
]
ops_cats_p2 = [
    "Maintenance & Repairs",
    "Insurance",
    "Legal & Compliance",
    "Procurement",
    "Vendor Management",
    "Operations Contingency",
]
ops_rows_p1 = make_budget_rows(ops_cats_p1, seed_offset=3)
ops_rows_p2 = make_budget_rows(ops_cats_p2, seed_offset=4)
ops_rows_all = ops_rows_p1 + ops_rows_p2
ops_total = sum(r[5] for r in ops_rows_all)

# Page 4: first half of operations
margin = 0.75 * inch
c.setFont("Helvetica-Bold", 14)
c.setFillColor(colors.HexColor("#1F3864"))
c.drawString(margin, H - 1.2*inch, "Operations Department — 2026 Budget (Page 1 of 2)")
c.setFillColor(colors.black)

header = ["Category", "Q1", "Q2", "Q3", "Q4", "Annual"]
tbl_data_p4 = [header]
for row in ops_rows_p1:
    cat, q1, q2, q3, q4, annual = row
    tbl_data_p4.append([cat, fmt(q1), fmt(q2), fmt(q3), fmt(q4), fmt(annual)])
# No total row here — continues on next page
tbl_data_p4.append(["(Continued on next page)", "", "", "", "", ""])

col_widths = [2.3*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch]
tbl_p4 = RLTable(tbl_data_p4, colWidths=col_widths)
tbl_p4.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F3864")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
    ("ALIGN", (1,0), (-1,-1), "RIGHT"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("ROWBACKGROUNDS", (0,1), (-1,-2), [colors.white, colors.HexColor("#E8EDF5")]),
    ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Oblique"),
    ("TEXTCOLOR", (0,-1), (-1,-1), colors.grey),
    ("ALIGN", (0,-1), (0,-1), "CENTER"),
]))
tbl_p4.wrapOn(c, W - 2*margin, H)
tw, th = tbl_p4.wrap(0, 0)
tbl_p4.drawOn(c, margin, H - 1.5*inch - th)
c.setFont("Helvetica", 8)
c.setFillColor(colors.grey)
c.drawCentredString(W/2, 0.4*inch, "Page 4")
c.setFillColor(colors.black)
c.showPage()

# Page 5: second half of operations + total
c.setFont("Helvetica-Bold", 14)
c.setFillColor(colors.HexColor("#1F3864"))
c.drawString(margin, H - 1.2*inch, "Operations Department — 2026 Budget (Page 2 of 2)")
c.setFillColor(colors.black)

ops_total_q1 = sum(r[1] for r in ops_rows_all)
ops_total_q2 = sum(r[2] for r in ops_rows_all)
ops_total_q3 = sum(r[3] for r in ops_rows_all)
ops_total_q4 = sum(r[4] for r in ops_rows_all)

tbl_data_p5 = [header]
for row in ops_rows_p2:
    cat, q1, q2, q3, q4, annual = row
    tbl_data_p5.append([cat, fmt(q1), fmt(q2), fmt(q3), fmt(q4), fmt(annual)])
tbl_data_p5.append([
    "DEPARTMENT TOTAL",
    fmt(ops_total_q1), fmt(ops_total_q2), fmt(ops_total_q3), fmt(ops_total_q4),
    fmt(ops_total)
])

tbl_p5 = RLTable(tbl_data_p5, colWidths=col_widths)
tbl_p5.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F3864")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
    ("ALIGN", (1,0), (-1,-1), "RIGHT"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("ROWBACKGROUNDS", (0,1), (-1,-2), [colors.white, colors.HexColor("#E8EDF5")]),
    ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#1F3864")),
    ("TEXTCOLOR", (0,-1), (-1,-1), colors.white),
    ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
]))
tbl_p5.wrapOn(c, W - 2*margin, H)
tw, th = tbl_p5.wrap(0, 0)
tbl_p5.drawOn(c, margin, H - 1.5*inch - th)
c.setFont("Helvetica-Oblique", 7)
c.setFillColor(colors.grey)
c.drawString(margin, H - 1.5*inch - th - 0.15*inch,
    "Note: Page 4 shows the first 6 line items of the Operations budget; this page shows the remaining 6.")
c.setFillColor(colors.black)
c.setFont("Helvetica", 8)
c.setFillColor(colors.grey)
c.drawCentredString(W/2, 0.4*inch, "Page 5")
c.setFillColor(colors.black)
c.showPage()

# ---- Page 6: HR ----
hr_cats = [
    "HR Salaries",
    "Recruiting & Hiring",
    "Benefits Administration",
    "Employee Training",
    "HRIS Software",
    "HR Contingency",
]
hr_rows = make_budget_rows(hr_cats, seed_offset=5)
hr_total, _ = draw_dept_table(c, 6, "Human Resources", hr_rows)
c.showPage()

# ---- Page 7: Company roll-up summary (DO NOT extract from here) ----
c.setFont("Helvetica-Bold", 16)
c.setFillColor(colors.HexColor("#1F3864"))
c.drawCentredString(W/2, H - 1.2*inch, "Company-Wide Budget Roll-Up — FY 2026")
c.setFillColor(colors.black)
c.setFont("Helvetica", 10)
c.drawCentredString(W/2, H - 1.6*inch, "This page is a management summary. Do not use for departmental extraction.")

grand_total = eng_total + mkt_total + ops_total + hr_total

rollup_data = [
    ["Department", "Annual Budget"],
    ["Engineering", fmt(eng_total)],
    ["Marketing", fmt(mkt_total)],
    ["Operations", fmt(ops_total)],
    ["Human Resources", fmt(hr_total)],
    ["GRAND TOTAL", fmt(grand_total)],
]
tbl_ru = RLTable(rollup_data, colWidths=[3*inch, 2*inch])
tbl_ru.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1F3864")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 11),
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("ALIGN", (1,0), (-1,-1), "RIGHT"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#1F3864")),
    ("TEXTCOLOR", (0,-1), (-1,-1), colors.white),
    ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
]))
tbl_ru.wrapOn(c, W, H)
tw, th = tbl_ru.wrap(0, 0)
tbl_ru.drawOn(c, (W-5*inch)/2, H - 2.5*inch - th)

c.setFont("Helvetica", 8)
c.setFillColor(colors.grey)
c.drawCentredString(W/2, 0.4*inch, "Page 7")
c.setFillColor(colors.black)
c.showPage()

c.save()
print(f"Written: {OUTPUT}")
print(f"Engineering total: {eng_total:,}")
print(f"Marketing total:   {mkt_total:,}")
print(f"Operations total:  {ops_total:,}")
print(f"HR total:          {hr_total:,}")
print(f"Grand total:       {grand_total:,}")

import pypdf
r = pypdf.PdfReader(OUTPUT)
print(f"Page count: {len(r.pages)}")

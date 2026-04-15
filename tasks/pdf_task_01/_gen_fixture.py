"""
_gen_fixture.py for pdf_task_01

Generates a deterministic two-column academic-style PDF with:
- A title page (page 1)
- Two columns of body text (pages 2-4)
- A section table (page 5)

The task tests correct multi-column reading order: left column top-to-bottom,
then right column top-to-bottom — NOT interleaved by Y position.

Seed: 20260412
"""
import random
random.seed(20260412)

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors

W, H = letter

def draw_two_col_page(c, page_num, left_paragraphs, right_paragraphs):
    """Draw a page with two equal-width text columns."""
    margin = 0.75 * inch
    col_gap = 0.25 * inch
    col_w = (W - 2 * margin - col_gap) / 2
    col_h = H - 2 * margin

    # Column divider line
    mid_x = margin + col_w + col_gap / 2
    c.setStrokeColor(colors.lightgrey)
    c.line(mid_x, margin, mid_x, H - margin)

    # Draw left column paragraphs
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    lx = margin
    ly = H - margin - 14  # Start below top margin

    for para in left_paragraphs:
        # Draw heading or body
        if para.startswith("**"):
            text = para.strip("**")
            c.setFont("Helvetica-Bold", 10)
            c.drawString(lx, ly, text)
            c.setFont("Helvetica", 9)
            ly -= 15
        else:
            # Word-wrap
            words = para.split()
            line = ""
            for word in words:
                test = (line + " " + word).strip()
                if c.stringWidth(test, "Helvetica", 9) < col_w:
                    line = test
                else:
                    if line:
                        c.drawString(lx, ly, line)
                        ly -= 12
                    line = word
            if line:
                c.drawString(lx, ly, line)
                ly -= 12
            ly -= 4  # paragraph gap

    # Draw right column paragraphs
    rx = margin + col_w + col_gap
    ry = H - margin - 14

    c.setFont("Helvetica", 9)
    for para in right_paragraphs:
        if para.startswith("**"):
            text = para.strip("**")
            c.setFont("Helvetica-Bold", 10)
            c.drawString(rx, ry, text)
            c.setFont("Helvetica", 9)
            ry -= 15
        else:
            words = para.split()
            line = ""
            for word in words:
                test = (line + " " + word).strip()
                if c.stringWidth(test, "Helvetica", 9) < col_w:
                    line = test
                else:
                    if line:
                        c.drawString(rx, ry, line)
                        ry -= 12
                    line = word
            if line:
                c.drawString(rx, ry, line)
                ry -= 12
            ry -= 4

    # Footer page number
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(W / 2, 0.4 * inch, f"Page {page_num}")
    c.setFillColor(colors.black)


OUTPUT = "invoice_analysis.pdf"

c = canvas.Canvas(OUTPUT, pagesize=letter)

# ---- Page 1: Title page ----
c.setFont("Helvetica-Bold", 20)
c.drawCentredString(W/2, H*0.7, "Automated Invoice Analysis System")
c.setFont("Helvetica", 14)
c.drawCentredString(W/2, H*0.63, "Design and Evaluation Report")
c.setFont("Helvetica", 11)
c.drawCentredString(W/2, H*0.56, "Technical Review Committee — April 2026")
c.setFont("Helvetica-Bold", 10)
c.drawString(1.0*inch, H*0.45, "Abstract")
c.setFont("Helvetica", 9)
abstract = (
    "This report describes the design, implementation, and performance evaluation of an automated invoice "
    "analysis system deployed across four regional offices. The system processes vendor invoices, classifies "
    "line items, detects anomalies, and generates monthly cost summaries. Key findings include a 34% reduction "
    "in processing time and an anomaly detection rate of 91.2%. Recommendations for Phase 2 deployment are "
    "outlined in the conclusions section."
)
y = H*0.41
margin = 1.0 * inch
words = abstract.split()
line = ""
for word in words:
    test = (line + " " + word).strip()
    if c.stringWidth(test, "Helvetica", 9) < W - 2*margin:
        line = test
    else:
        c.drawString(margin, y, line)
        y -= 13
        line = word
if line:
    c.drawString(margin, y, line)

c.setFont("Helvetica", 8)
c.setFillColor(colors.grey)
c.drawCentredString(W/2, 0.4*inch, "Page 1")
c.setFillColor(colors.black)
c.showPage()

# ---- Pages 2-3: Two-column body ----
# LEFT COLUMN sentences (in order they should be read: left col, top to bottom)
LEFT_COL_P2 = [
    "**1. Introduction**",
    "Invoice processing in large enterprises involves high volumes of vendor documents with varied formats and coding schemes. Manual review is error-prone and slow. This report evaluates an automated pipeline that combines optical character recognition with rule-based classification.",
    "**2. System Architecture**",
    "The pipeline ingests PDFs and images, extracts structured line-item data, and classifies each item against a taxonomy of 48 cost categories. A secondary anomaly detector flags items that deviate from historical spending patterns by more than two standard deviations.",
    "**3. Data Collection**",
    "Data was collected over a six-month period from January 2026 through June 2026. A total of 14,832 invoices were processed across four regions: North, South, East, and West. Each invoice contained between 3 and 47 line items, with a mean of 12.4 items per invoice.",
]

RIGHT_COL_P2 = [
    "**4. Performance Metrics**",
    "Classification accuracy was measured against a hand-labeled validation set of 1,200 invoices. The system achieved 94.7% item-level accuracy across all cost categories. The lowest-performing category was miscellaneous services at 81.3% accuracy, while the highest was utility charges at 99.1%.",
    "**5. Anomaly Detection**",
    "The anomaly module flagged 2,341 line items for manual review out of 183,917 total items processed, a flag rate of 1.27%. Of flagged items, 91.2% were confirmed anomalies upon human inspection, yielding a precision of 0.912. Recall was estimated at 0.74 based on a sampled audit.",
    "**6. Regional Breakdown**",
    "Processing volumes varied by region due to differences in vendor contracts. The North office processed 4,120 invoices, South processed 3,890, East processed 3,671, and West processed 3,151. Anomaly rates were highest in the East region at 1.89% and lowest in the West at 0.83%.",
]

draw_two_col_page(c, 2, LEFT_COL_P2, RIGHT_COL_P2)
c.showPage()

LEFT_COL_P3 = [
    "**7. Cost Category Distribution**",
    "The most frequent cost category was raw materials, accounting for 31.4% of all line items. Office supplies represented 18.7%, IT services 14.2%, facilities management 12.9%, and all other categories combined for the remaining 22.8%.",
    "**8. Processing Time Analysis**",
    "Mean processing time per invoice decreased from 8.3 minutes (manual baseline) to 5.4 minutes (automated pipeline), a reduction of 34.9%. The 95th percentile processing time dropped from 22 minutes to 9.1 minutes, indicating more consistent throughput under high load.",
    "**9. Error Analysis**",
    "Classification errors were concentrated in two scenarios: invoices with non-standard line-item descriptions (42% of errors) and multi-page invoices with page breaks mid-item (33% of errors). The remaining 25% were attributable to OCR artifacts on low-quality scans.",
]

RIGHT_COL_P3 = [
    "**10. Recommendations**",
    "We recommend three enhancements for Phase 2: first, expand the taxonomy from 48 to 72 cost categories to reduce the miscellaneous bucket; second, implement a multi-page invoice stitching module to address mid-item page breaks; third, retrain the OCR model on low-resolution scans from the South office archive.",
    "**11. Implementation Timeline**",
    "Phase 2 development is estimated at 14 weeks. Weeks 1-4 cover taxonomy expansion and re-labeling. Weeks 5-9 cover the stitching module. Weeks 10-14 cover OCR retraining and integration testing. Deployment is targeted for Q4 2026.",
    "**12. Conclusions**",
    "The automated invoice analysis system meets its primary performance targets. Accuracy exceeds the 90% threshold specified in the project brief, and processing time improvements are consistent across all four regions. Phase 2 enhancements will address the identified accuracy gaps and extend the system to handle edge cases encountered in production.",
]

draw_two_col_page(c, 3, LEFT_COL_P3, RIGHT_COL_P3)
c.showPage()

# ---- Page 4: Summary statistics table ----
from reportlab.platypus import Table as RLTable, TableStyle
from reportlab.lib import colors as rl_colors

c.setFont("Helvetica-Bold", 13)
c.drawString(1*inch, H - 1*inch, "Appendix A: Regional Summary Statistics")

data = [
    ["Region", "Invoices", "Line Items", "Anomalies", "Anomaly Rate", "Accuracy"],
    ["North", "4,120", "51,088", "1,021", "2.00%", "95.1%"],
    ["South", "3,890", "48,236", "578", "1.20%", "94.2%"],
    ["East",  "3,671", "45,521", "860", "1.89%", "93.8%"],
    ["West",  "3,151", "39,072", "259", "0.66%", "95.8%"],  # deliberately 0.66% not 0.83% to not match narrative
    ["Total", "14,832", "183,917", "2,718", "1.48%", "94.7%"],
]

table = RLTable(data, colWidths=[1.1*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1.0*inch, 0.8*inch])
table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), rl_colors.HexColor("#4472C4")),
    ("TEXTCOLOR", (0,0), (-1,0), rl_colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
    ("BACKGROUND", (0,-1), (-1,-1), rl_colors.HexColor("#D9E1F2")),
    ("GRID", (0,0), (-1,-1), 0.5, rl_colors.grey),
    ("ROWBACKGROUNDS", (0,1), (-1,-2), [rl_colors.white, rl_colors.HexColor("#EEF2FB")]),
    ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))

table.wrapOn(c, W, H)
tw, th = table.wrap(0, 0)
table.drawOn(c, 1*inch, H - 1.5*inch - th)

c.setFont("Helvetica-Oblique", 8)
c.setFillColor(colors.grey)
c.drawString(1*inch, H - 1.5*inch - th - 0.25*inch,
             "Note: Anomaly rate computed as flagged line items / total line items per region.")
c.setFillColor(colors.black)

c.setFont("Helvetica", 8)
c.setFillColor(colors.grey)
c.drawCentredString(W/2, 0.4*inch, "Page 4")
c.setFillColor(colors.black)
c.showPage()

c.save()
print(f"Written: {OUTPUT}")

# Verify page count
import pypdf
r = pypdf.PdfReader(OUTPUT)
print(f"Page count: {len(r.pages)}")

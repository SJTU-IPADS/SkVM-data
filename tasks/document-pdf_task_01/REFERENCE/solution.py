"""
Reference solution for document-pdf_task_01.

Reads report_spec.json from cwd and produces:
  - report.pdf  (A4, title page + TOC + body sections with footers and bookmarks)
  - report_manifest.json

Page layout:
  - Page 1: Title page (no footer)
  - Page 2: Table of Contents (footer: Page 2 of M)
  - Pages 3..N+2: One page per section (footer: Page K of M)

Footer format: "Page K of M" centered at bottom.
Bookmarks: one PDF outline entry per body section (canvas.addOutlineEntry).
TOC: one line per section with right-aligned page number and dot leaders.
"""
from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas


def build(output_path: str, spec: dict, total_pages: int, section_start_pages: list[int]) -> None:
    """Build the PDF with known total_pages and section_start_pages."""
    company: str = spec["company"]
    title: str = spec["title"]
    date_str: str = spec["date"]
    sections: list[dict] = spec["sections"]

    c = pdfcanvas.Canvas(output_path, pagesize=A4)
    w, h = A4
    page_num = 0

    def finish_page(is_title: bool = False) -> None:
        nonlocal page_num
        page_num += 1
        if not is_title:
            c.setFont("Helvetica", 9)
            c.drawCentredString(w / 2, 12 * mm, f"Page {page_num} of {total_pages}")
        c.showPage()

    # ── Page 1: Title ──────────────────────────────────────────────────────
    c.bookmarkPage("title_page")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(w / 2, h * 0.60, title)
    c.setFont("Helvetica", 16)
    c.drawCentredString(w / 2, h * 0.52, company)
    c.setFont("Helvetica", 13)
    c.drawCentredString(w / 2, h * 0.46, date_str)
    finish_page(is_title=True)

    # ── Page 2: TOC ────────────────────────────────────────────────────────
    c.bookmarkPage("toc_page")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(25 * mm, h - 28 * mm, "Table of Contents")
    c.line(25 * mm, h - 32 * mm, w - 25 * mm, h - 32 * mm)

    toc_y = h - 44 * mm
    for i, sec in enumerate(sections):
        sec_title: str = sec["title"]
        page_ref = section_start_pages[i]
        c.setFont("Helvetica", 11)
        c.drawString(25 * mm, toc_y, sec_title)
        entry_w = c.stringWidth(sec_title, "Helvetica", 11)
        dots_start = 25 * mm + entry_w + 3 * mm
        page_str = str(page_ref)
        page_str_w = c.stringWidth(page_str, "Helvetica", 11)
        dots_end = w - 25 * mm - page_str_w - 4 * mm
        dot_ch_w = c.stringWidth(".", "Helvetica", 11)
        n_dots = max(0, int((dots_end - dots_start) / dot_ch_w))
        c.drawString(dots_start, toc_y, "." * n_dots)
        c.drawRightString(w - 25 * mm, toc_y, page_str)
        toc_y -= 8 * mm

    finish_page(is_title=False)

    # ── Body sections ──────────────────────────────────────────────────────
    for sec in sections:
        sec_title = sec["title"]
        sec_content: list[str] = sec["content"]

        bookmark_key = sec_title.replace(" ", "_")
        c.bookmarkPage(bookmark_key)
        c.addOutlineEntry(sec_title, bookmark_key, level=0, closed=False)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(25 * mm, h - 28 * mm, sec_title)
        c.line(25 * mm, h - 32 * mm, w - 25 * mm, h - 32 * mm)

        y = h - 44 * mm
        c.setFont("Helvetica", 11)
        line_height = 6 * mm
        para_gap = 4 * mm
        max_width = w - 50 * mm

        for para_text in sec_content:
            words = para_text.split()
            line_buf = ""
            for word in words:
                candidate = (line_buf + " " + word).strip()
                if c.stringWidth(candidate, "Helvetica", 11) > max_width:
                    c.drawString(25 * mm, y, line_buf)
                    y -= line_height
                    line_buf = word
                else:
                    line_buf = candidate
            if line_buf:
                c.drawString(25 * mm, y, line_buf)
                y -= line_height
            y -= para_gap

        finish_page(is_title=False)

    c.save()


def main() -> None:
    spec = json.loads(Path("report_spec.json").read_text())
    sections = spec["sections"]
    n_sections = len(sections)

    # Page layout: 1 title + 1 TOC + n_sections body = 2 + n_sections total
    total_pages = 2 + n_sections
    # Sections start at page 3 (0-indexed: pages 2, 3, 4, ...)
    section_start_pages = [3 + i for i in range(n_sections)]

    output = "report.pdf"
    build(output, spec, total_pages, section_start_pages)

    # Verify with pypdf
    from pypdf import PdfReader
    reader = PdfReader(output)
    actual_page_count = len(reader.pages)

    manifest = {
        "page_count": actual_page_count,
        "page_size": "A4",
        "toc_entry_count": n_sections,
        "section_count": n_sections,
        "sections": [
            {"title": sections[i]["title"], "page_number": section_start_pages[i]}
            for i in range(n_sections)
        ],
    }

    Path("report_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"report.pdf: {actual_page_count} pages, A4")
    print(f"manifest written")


if __name__ == "__main__":
    main()

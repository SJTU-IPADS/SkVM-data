"""
Grade function for document-pdf_task_01.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Expected values from report_spec.json (5 sections, deterministic layout):
  - page_count: 7 (1 title + 1 TOC + 5 sections)
  - page_size: A4 (595.28 x 841.89 points, tolerance ±2)
  - toc_entry_count: 5
  - section_count: 5
  - sections: listed in spec order, pages 3-7
  - Footer "Page N of M" on pages 2-7 (not title page)
  - PDF bookmarks: 5 outline entries (one per section)
"""
from __future__ import annotations

import json
import re
from pathlib import Path


# ── Expected values ──────────────────────────────────────────────────────────

EXPECTED_SECTION_COUNT = 5
EXPECTED_PAGE_COUNT = 7          # 1 title + 1 TOC + 5 sections
A4_WIDTH_PT = 595.28
A4_HEIGHT_PT = 841.89
A4_TOL = 2.0                    # points tolerance for A4 size check

EXPECTED_SECTIONS = [
    {"title": "Executive Summary",     "page_number": 3},
    {"title": "Revenue Analysis",      "page_number": 4},
    {"title": "Cost Management",       "page_number": 5},
    {"title": "Risk Management",       "page_number": 6},
    {"title": "Outlook",               "page_number": 7},
]

EXPECTED_SECTION_TITLES = [s["title"] for s in EXPECTED_SECTIONS]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _load_pdf(workspace_path: str):
    """Return (PdfReader, error_str). error_str is None on success."""
    pdf_path = Path(workspace_path) / "report.pdf"
    if not pdf_path.exists():
        return None, "report.pdf not found in workspace"
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        return reader, None
    except Exception as e:
        return None, f"report.pdf could not be read: {e}"


def _load_manifest(workspace_path: str):
    """Return (dict, error_str)."""
    mf_path = Path(workspace_path) / "report_manifest.json"
    if not mf_path.exists():
        return None, "report_manifest.json not found in workspace"
    try:
        return json.loads(mf_path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"report_manifest.json is not valid JSON: {e}"


# ── Per-criterion checks ─────────────────────────────────────────────────────

def _check_pdf_exists(reader, manifest):
    if reader is None:
        return 0.0, "report.pdf missing or unparseable"
    return 1.0, None


def _check_manifest_exists(reader, manifest):
    if manifest is None:
        return 0.0, "report_manifest.json missing or unparseable"
    return 1.0, None


def _check_manifest_schema(reader, manifest):
    if manifest is None:
        return 0.0, "report_manifest.json missing"
    required = {"page_count", "page_size", "toc_entry_count", "section_count", "sections"}
    missing = required - set(manifest.keys())
    if missing:
        return 0.0, f"report_manifest.json missing keys: {sorted(missing)}"
    return 1.0, None


def _check_page_size_a4(reader, manifest):
    """A4 = 595.28 x 841.89 points. Common default is Letter (612 x 792)."""
    if reader is None:
        return 0.0, "report.pdf missing"
    try:
        page = reader.pages[0]
        pw = float(page.mediabox.width)
        ph = float(page.mediabox.height)
    except Exception as e:
        return 0.0, f"could not read page dimensions: {e}"
    # Accept portrait or landscape orientation
    a4_match = (
        (abs(pw - A4_WIDTH_PT) <= A4_TOL and abs(ph - A4_HEIGHT_PT) <= A4_TOL) or
        (abs(pw - A4_HEIGHT_PT) <= A4_TOL and abs(ph - A4_WIDTH_PT) <= A4_TOL)
    )
    if not a4_match:
        return 0.0, (
            f"page size is {pw:.1f}x{ph:.1f} pts — expected A4 (~{A4_WIDTH_PT}x{A4_HEIGHT_PT}). "
            f"reportlab defaults to Letter (612x792); use pagesize=A4 from reportlab.lib.pagesizes."
        )
    if manifest and manifest.get("page_size") != "A4":
        return 0.5, (
            f"PDF is A4 but report_manifest.json page_size is {manifest.get('page_size')!r}, expected 'A4'"
        )
    return 1.0, None


def _check_page_count(reader, manifest):
    """Exactly 7 pages: 1 title + 1 TOC + 5 body sections."""
    if reader is None:
        return 0.0, "report.pdf missing"
    got = len(reader.pages)
    if got != EXPECTED_PAGE_COUNT:
        return 0.0, (
            f"page_count is {got}, expected {EXPECTED_PAGE_COUNT} "
            f"(1 title + 1 TOC + {EXPECTED_SECTION_COUNT} body sections)"
        )
    return 1.0, None


def _check_manifest_page_count(reader, manifest):
    if manifest is None:
        return 0.0, "report_manifest.json missing"
    got = manifest.get("page_count")
    if got != EXPECTED_PAGE_COUNT:
        return 0.0, f"manifest page_count is {got}, expected {EXPECTED_PAGE_COUNT}"
    return 1.0, None


def _check_toc_section_invariant(reader, manifest):
    """toc_entry_count == section_count (stateful invariant)."""
    if manifest is None:
        return 0.0, "report_manifest.json missing"
    toc = manifest.get("toc_entry_count")
    sec = manifest.get("section_count")
    if toc is None or sec is None:
        return 0.0, "toc_entry_count or section_count missing from manifest"
    if toc != EXPECTED_SECTION_COUNT:
        return 0.0, f"toc_entry_count is {toc}, expected {EXPECTED_SECTION_COUNT}"
    if sec != EXPECTED_SECTION_COUNT:
        return 0.0, f"section_count is {sec}, expected {EXPECTED_SECTION_COUNT}"
    if toc != sec:
        return 0.0, f"toc_entry_count ({toc}) != section_count ({sec}) — invariant violation"
    return 1.0, None


def _check_section_list(reader, manifest):
    """sections list has correct titles in spec order with correct page numbers."""
    if manifest is None:
        return 0.0, "report_manifest.json missing"
    sections = manifest.get("sections")
    if not isinstance(sections, list):
        return 0.0, "manifest.sections is not a list"
    if len(sections) != EXPECTED_SECTION_COUNT:
        return 0.0, f"manifest.sections has {len(sections)} entries, expected {EXPECTED_SECTION_COUNT}"
    errors = []
    for i, (got, exp) in enumerate(zip(sections, EXPECTED_SECTIONS)):
        if not isinstance(got, dict):
            errors.append(f"sections[{i}] is not an object")
            continue
        if got.get("title") != exp["title"]:
            errors.append(f"sections[{i}].title: expected {exp['title']!r}, got {got.get('title')!r}")
        if got.get("page_number") != exp["page_number"]:
            errors.append(
                f"sections[{i}].page_number: expected {exp['page_number']}, "
                f"got {got.get('page_number')!r}"
            )
    if errors:
        return 0.0, "; ".join(errors[:3])
    return 1.0, None


def _check_pdf_bookmarks(reader, manifest):
    """PDF should have outline entries (bookmarks) for each body section."""
    if reader is None:
        return 0.0, "report.pdf missing"
    try:
        outlines = reader.outline
    except Exception:
        outlines = []

    def _flatten(items):
        result = []
        for item in items:
            if isinstance(item, list):
                result.extend(_flatten(item))
            elif hasattr(item, "title"):
                result.append(item.title)
        return result

    outline_titles = _flatten(outlines)
    found = 0
    for exp_title in EXPECTED_SECTION_TITLES:
        if any(exp_title.lower() in t.lower() for t in outline_titles):
            found += 1

    if found == 0:
        return 0.0, (
            f"PDF has no outline entries matching section titles. "
            f"Found outlines: {outline_titles[:5]}"
        )
    if found < EXPECTED_SECTION_COUNT:
        return 0.5, (
            f"PDF has outline entries for {found}/{EXPECTED_SECTION_COUNT} sections. "
            f"Found: {outline_titles}"
        )
    return 1.0, None


def _check_footer_on_body_pages(reader, manifest):
    """Pages 2-7 (TOC + sections) must contain 'Page N of 7' footer text.
    Page 1 (title) must NOT contain a footer.
    Checks via text extraction on pages 2, 3, and 7."""
    if reader is None:
        return 0.0, "report.pdf missing"
    if len(reader.pages) < EXPECTED_PAGE_COUNT:
        return 0.0, f"PDF has fewer than {EXPECTED_PAGE_COUNT} pages"

    errors = []
    footer_pattern = re.compile(r"[Pp]age\s+\d+\s+of\s+\d+")

    # Check that footer appears on page 2 (TOC page), page 3 (first section), last page
    for pg_idx in [1, 2, EXPECTED_PAGE_COUNT - 1]:
        try:
            text = reader.pages[pg_idx].extract_text() or ""
        except Exception as e:
            errors.append(f"could not extract text from page {pg_idx+1}: {e}")
            continue
        if not footer_pattern.search(text):
            errors.append(f"page {pg_idx+1} missing 'Page N of M' footer; extracted: {text[-100:]!r}")

    if errors:
        return 0.0, "; ".join(errors[:2])

    # Also verify title page (page 1) does NOT have footer
    try:
        title_text = reader.pages[0].extract_text() or ""
        if footer_pattern.search(title_text):
            return 0.5, "title page (page 1) contains a footer — should be footer-free"
    except Exception:
        pass

    return 1.0, None


def _check_section_content_present(reader, manifest):
    """Each section's title should appear in the PDF text on its expected page."""
    if reader is None:
        return 0.0, "report.pdf missing"
    if len(reader.pages) < EXPECTED_PAGE_COUNT:
        return 0.0, "not enough pages"
    missing = []
    for exp in EXPECTED_SECTIONS:
        pg_idx = exp["page_number"] - 1  # 0-indexed
        try:
            text = reader.pages[pg_idx].extract_text() or ""
        except Exception:
            text = ""
        if exp["title"].lower() not in text.lower():
            missing.append(f"page {exp['page_number']} missing header {exp['title']!r}")
    if missing:
        return 0.0, "; ".join(missing[:3])
    return 1.0, None


def _check_toc_page_exists(reader, manifest):
    """TOC page (page 2) should contain 'Table of Contents' text and section titles."""
    if reader is None:
        return 0.0, "report.pdf missing"
    if len(reader.pages) < 2:
        return 0.0, "PDF has fewer than 2 pages"
    try:
        toc_text = reader.pages[1].extract_text() or ""
    except Exception as e:
        return 0.0, f"could not extract TOC page text: {e}"
    toc_text_lower = toc_text.lower()
    if "table of contents" not in toc_text_lower and "contents" not in toc_text_lower:
        return 0.0, f"page 2 does not appear to be a TOC page; extracted: {toc_text[:200]!r}"
    # Check at least 3 of 5 section titles appear in TOC
    found = sum(1 for t in EXPECTED_SECTION_TITLES if t.lower() in toc_text_lower)
    if found < 3:
        return 0.5, (
            f"TOC page contains only {found}/{EXPECTED_SECTION_COUNT} section titles; "
            f"extracted: {toc_text[:300]!r}"
        )
    return 1.0, None


# ── Criterion registry ────────────────────────────────────────────────────────

CRITERIA = [
    {
        "id": "pdf-exists",
        "weight": 0.04,
        "description": "report.pdf exists in the workspace and is a valid, readable PDF.",
        "check": _check_pdf_exists,
    },
    {
        "id": "manifest-exists",
        "weight": 0.04,
        "description": "report_manifest.json exists in the workspace and is valid JSON.",
        "check": _check_manifest_exists,
    },
    {
        "id": "manifest-schema",
        "weight": 0.04,
        "description": "report_manifest.json contains all required top-level keys: page_count, page_size, toc_entry_count, section_count, sections.",
        "check": _check_manifest_schema,
    },
    {
        "id": "page-size-a4",
        "weight": 0.20,
        "description": "Every page is A4 size (595.28 x 841.89 points). reportlab's default is US Letter (612x792 pts); the task spec explicitly requires A4, making this a common-default-wrong trap.",
        "check": _check_page_size_a4,
    },
    {
        "id": "page-count-correct",
        "weight": 0.12,
        "description": "PDF has exactly 7 pages: 1 title page + 1 TOC page + 5 body section pages. Getting this right requires coordinating all three document elements.",
        "check": _check_page_count,
    },
    {
        "id": "manifest-page-count",
        "weight": 0.05,
        "description": "report_manifest.json page_count field equals 7, matching the actual PDF page count.",
        "check": _check_manifest_page_count,
    },
    {
        "id": "toc-section-invariant",
        "weight": 0.12,
        "description": "toc_entry_count equals section_count in the manifest (stateful invariant): the TOC must contain exactly one entry per body section, no more and no fewer.",
        "check": _check_toc_section_invariant,
    },
    {
        "id": "section-list-correct",
        "weight": 0.12,
        "description": "manifest.sections lists all 5 sections in spec order with correct titles and page numbers (Executive Summary on page 3, Revenue Analysis on 4, etc.).",
        "check": _check_section_list,
    },
    {
        "id": "pdf-bookmarks",
        "weight": 0.10,
        "description": "PDF outline (bookmarks) contains one entry per body section, enabling document navigation — requires addOutlineEntry() in reportlab's canvas API.",
        "check": _check_pdf_bookmarks,
    },
    {
        "id": "footer-on-body-pages",
        "weight": 0.10,
        "description": "Pages 2-7 carry a 'Page N of 7' footer centered at the bottom; the title page (page 1) has no footer. Requires knowing total page count before rendering, which is a multi-step coordination challenge.",
        "check": _check_footer_on_body_pages,
    },
    {
        "id": "section-content-present",
        "weight": 0.04,
        "description": "Each section's title text appears on its expected page in the PDF, confirming content was placed correctly.",
        "check": _check_section_content_present,
    },
    {
        "id": "toc-page-exists",
        "weight": 0.03,
        "description": "Page 2 is the Table of Contents page, containing 'Table of Contents' header and at least 3 of the 5 section titles with page references.",
        "check": _check_toc_page_exists,
    },
]

# Sanity-check weights at import time: must sum to 1.0 (tolerance 1e-3).
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    reader, _reader_err = _load_pdf(workspace_path)
    manifest, _manifest_err = _load_manifest(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](reader, manifest)
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

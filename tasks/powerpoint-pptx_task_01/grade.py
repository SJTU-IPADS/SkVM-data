"""
Grade function for powerpoint-pptx_task_01.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: read product_deck.pptx and deck_manifest.json from the workspace,
verify them against the pinned spec in deck_spec.json (which is also in the workspace).

Archetypes tested:
  1 (under-specified): layout names and placeholder indices must match the spec exactly.
  4 (known-edge-case): EMU position of the table must match the spec to the EMU.
  5 (stateful invariant): slide count, shape type codes, and notes presence must be consistent.
"""
from __future__ import annotations
import json
import os
from pathlib import Path

# ---- Expected values (from deck_spec.json fixture, known at author time) -----

EXPECTED_SLIDE_COUNT = 5

# Per-slide expectations derived from deck_spec.json
EXPECTED_SLIDES = [
    {
        "slide_index": 0,
        "layout": "Title Slide",
        "title": "Meridian Analytics Platform",
        "subtitle": "Product Overview — Q1 2026",
        "has_table": False,
        "has_notes": True,
        "notes_fragment": "Welcome attendees",
    },
    {
        "slide_index": 1,
        "layout": "Title and Content",
        "title": "Executive Summary",
        "bullets": [
            "Real-time dashboards for 500+ data sources",
            "Sub-second query latency at 10 TB scale",
            "SOC-2 Type II certified",
        ],
        "has_table": False,
        "has_notes": True,
        "notes_fragment": "latency",
    },
    {
        "slide_index": 2,
        "layout": "Title Only",
        "title": "Pricing Tiers",
        "has_table": True,
        "table_rows": 4,
        "table_cols": 4,
        "table_header": ["Tier", "Monthly Price", "Data Volume", "Seats"],
        "table_cell_2_1": "Growth",   # row 2, col 1 (0-indexed)
        "table_pos": {
            "left_emu": 457200,
            "top_emu": 1371600,
            "width_emu": 8229600,
            "height_emu": 2286000,
        },
        "has_notes": False,
    },
    {
        "slide_index": 3,
        "layout": "Title and Content",
        "title": "Roadmap Highlights",
        "bullets": [
            "Q2 2026: Native Snowflake connector",
            "Q3 2026: AI-assisted anomaly detection",
            "Q4 2026: Self-serve embedding API",
        ],
        "has_table": False,
        "has_notes": True,
        "notes_fragment": "anomaly",
    },
    {
        "slide_index": 4,
        "layout": "Title Slide",
        "title": "Thank You",
        "subtitle": "questions@meridian.io",
        "has_table": False,
        "has_notes": False,
    },
]

# MSO shape type codes
MSO_PLACEHOLDER = 14
MSO_TABLE = 19


# ---- Helpers -----------------------------------------------------------------

def _load_pptx(workspace_path: str):
    pptx_path = Path(workspace_path) / "product_deck.pptx"
    if not pptx_path.exists():
        return None, "product_deck.pptx not found in workspace"
    try:
        from pptx import Presentation
        return Presentation(str(pptx_path)), None
    except Exception as e:
        return None, f"product_deck.pptx failed to open: {e}"


def _load_manifest(workspace_path: str):
    path = Path(workspace_path) / "deck_manifest.json"
    if not path.exists():
        return None, "deck_manifest.json not found"
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"deck_manifest.json is not valid JSON: {e}"


def _get_slides(prs):
    """Return list of slide objects."""
    if prs is None:
        return []
    return list(prs.slides)


def _ph_map(slide):
    """Return {idx: placeholder} map for a slide."""
    return {ph.placeholder_format.idx: ph for ph in slide.placeholders}


def _get_table(slide):
    """Return first TABLE shape on a slide, or None."""
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    for shape in slide.shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.TABLE:
            return shape
    return None


# ---- Criterion checks --------------------------------------------------------

def _check_pptx_exists(prs, manifest, slides):
    if prs is None:
        return 0.0, "product_deck.pptx missing or corrupted"
    return 1.0, None


def _check_manifest_exists(prs, manifest, slides):
    if manifest is None:
        return 0.0, "deck_manifest.json missing or corrupted"
    return 1.0, None


def _check_slide_count(prs, manifest, slides):
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    n = len(slides)
    if n != EXPECTED_SLIDE_COUNT:
        return 0.0, f"expected {EXPECTED_SLIDE_COUNT} slides, got {n}"
    return 1.0, None


def _check_layout_names(prs, manifest, slides):
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    if len(slides) < EXPECTED_SLIDE_COUNT:
        return 0.0, f"only {len(slides)} slides, cannot check all layouts"
    errors = []
    for exp in EXPECTED_SLIDES:
        i = exp["slide_index"]
        got = slides[i].slide_layout.name
        want = exp["layout"]
        if got != want:
            errors.append(f"slide {i}: layout={got!r}, want {want!r}")
    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, None


def _check_title_text(prs, manifest, slides):
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    if len(slides) < EXPECTED_SLIDE_COUNT:
        return 0.0, f"only {len(slides)} slides"
    errors = []
    for exp in EXPECTED_SLIDES:
        i = exp["slide_index"]
        ph_m = _ph_map(slides[i])
        ph = ph_m.get(0)
        if ph is None:
            errors.append(f"slide {i}: no title placeholder (idx=0)")
            continue
        got = ph.text.strip()
        want = exp["title"]
        if got != want:
            errors.append(f"slide {i}: title={got!r}, want {want!r}")
    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, None


def _check_subtitle_text(prs, manifest, slides):
    """Check subtitle on slides 0 and 4 (Title Slide layout)."""
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    if len(slides) < EXPECTED_SLIDE_COUNT:
        return 0.0, f"only {len(slides)} slides"
    errors = []
    for exp in EXPECTED_SLIDES:
        if "subtitle" not in exp:
            continue
        i = exp["slide_index"]
        ph_m = _ph_map(slides[i])
        ph = ph_m.get(1)
        if ph is None:
            errors.append(f"slide {i}: no subtitle placeholder (idx=1)")
            continue
        got = ph.text.strip()
        want = exp["subtitle"]
        # Allow partial match for subtitle
        if want not in got:
            errors.append(f"slide {i}: subtitle={got!r}, want fragment {want!r}")
    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, None


def _check_bullet_content(prs, manifest, slides):
    """Check bullet text on slides 1 and 3."""
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    if len(slides) < EXPECTED_SLIDE_COUNT:
        return 0.0, f"only {len(slides)} slides"
    errors = []
    for exp in EXPECTED_SLIDES:
        if "bullets" not in exp:
            continue
        i = exp["slide_index"]
        ph_m = _ph_map(slides[i])
        ph = ph_m.get(1)
        if ph is None:
            errors.append(f"slide {i}: no content placeholder (idx=1)")
            continue
        full_text = ph.text
        for bullet in exp["bullets"]:
            if bullet not in full_text:
                errors.append(f"slide {i}: missing bullet {bullet!r}")
    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, None


def _check_table_shape_type(prs, manifest, slides):
    """Slide 2 must have a TABLE shape (type code 19), not a placeholder containing a table."""
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    if len(slides) < 3:
        return 0.0, "fewer than 3 slides"
    slide2 = slides[2]
    tbl_shape = _get_table(slide2)
    if tbl_shape is None:
        shape_types = [int(s.shape_type) for s in slide2.shapes]
        return 0.0, f"slide 2: no TABLE shape found; shape_types={shape_types}"
    return 1.0, None


def _check_table_dimensions(prs, manifest, slides):
    """Table on slide 2 must be 4 rows × 4 cols per the spec."""
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    if len(slides) < 3:
        return 0.0, "fewer than 3 slides"
    tbl_shape = _get_table(slides[2])
    if tbl_shape is None:
        return 0.0, "slide 2: no TABLE shape"
    tbl = tbl_shape.table
    got_rows = len(tbl.rows)
    got_cols = len(tbl.columns)
    exp = EXPECTED_SLIDES[2]
    if got_rows != exp["table_rows"] or got_cols != exp["table_cols"]:
        return 0.0, f"table: expected {exp['table_rows']}×{exp['table_cols']}, got {got_rows}×{got_cols}"
    return 1.0, None


def _check_table_header_row(prs, manifest, slides):
    """Table header row must exactly match the spec column names."""
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    if len(slides) < 3:
        return 0.0, "fewer than 3 slides"
    tbl_shape = _get_table(slides[2])
    if tbl_shape is None:
        return 0.0, "slide 2: no TABLE shape"
    tbl = tbl_shape.table
    if len(tbl.rows) < 1:
        return 0.0, "table has no rows"
    expected_header = EXPECTED_SLIDES[2]["table_header"]
    got_header = [tbl.cell(0, c).text.strip() for c in range(min(len(expected_header), len(tbl.columns)))]
    if got_header != expected_header:
        return 0.0, f"table header: expected {expected_header}, got {got_header}"
    return 1.0, None


def _check_table_data_content(prs, manifest, slides):
    """Spot-check table data rows for correct values."""
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    if len(slides) < 3:
        return 0.0, "fewer than 3 slides"
    tbl_shape = _get_table(slides[2])
    if tbl_shape is None:
        return 0.0, "slide 2: no TABLE shape"
    tbl = tbl_shape.table
    # Check row 2 (Growth tier), col 0
    exp_tiers = [
        ("Starter", 1, 0), ("$299", 1, 1), ("100 GB", 1, 2),
        ("Growth", 2, 0), ("$899", 2, 1), ("1 TB", 2, 2),
        ("Enterprise", 3, 0), ("Custom", 3, 1), ("Unlimited", 3, 2),
    ]
    errors = []
    for val, r, c in exp_tiers:
        if r >= len(tbl.rows) or c >= len(tbl.columns):
            errors.append(f"table too small for row {r} col {c}")
            continue
        got = tbl.cell(r, c).text.strip()
        if got != val:
            errors.append(f"cell({r},{c}): expected {val!r}, got {got!r}")
    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, None


def _check_table_emu_position(prs, manifest, slides):
    """Table position on slide 2 must match the EMU coordinates in the spec exactly.
    This tests that the agent used Emu() or integer EMU values, not Inches() guesses."""
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    if len(slides) < 3:
        return 0.0, "fewer than 3 slides"
    tbl_shape = _get_table(slides[2])
    if tbl_shape is None:
        return 0.0, "slide 2: no TABLE shape"
    pos = EXPECTED_SLIDES[2]["table_pos"]
    errors = []
    for attr, key in [("left", "left_emu"), ("top", "top_emu"), ("width", "width_emu"), ("height", "height_emu")]:
        got = getattr(tbl_shape, attr)
        want = pos[key]
        if abs(got - want) > 914:  # tolerance: 1pt (914 EMU)
            errors.append(f"{attr}: expected {want} EMU, got {got} EMU (diff {abs(got-want)})")
    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, None


def _check_notes_present(prs, manifest, slides):
    """Slides 0, 1, 3 must have non-empty speaker notes; slides 2, 4 must not (per spec)."""
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    if len(slides) < EXPECTED_SLIDE_COUNT:
        return 0.0, f"only {len(slides)} slides"
    errors = []
    for exp in EXPECTED_SLIDES:
        i = exp["slide_index"]
        slide = slides[i]
        notes_text = ""
        if slide.has_notes_slide:
            notes_text = slide.notes_slide.notes_text_frame.text.strip()
        should_have = exp["has_notes"]
        has = bool(notes_text)
        if should_have and not has:
            errors.append(f"slide {i}: expected speaker notes, found none")
        elif not should_have and has:
            errors.append(f"slide {i}: expected no notes, found: {notes_text[:40]!r}")
    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, None


def _check_notes_content(prs, manifest, slides):
    """Speaker notes on slides 0, 1, 3 must contain the expected text fragments."""
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    if len(slides) < EXPECTED_SLIDE_COUNT:
        return 0.0, f"only {len(slides)} slides"
    errors = []
    for exp in EXPECTED_SLIDES:
        if not exp.get("notes_fragment"):
            continue
        i = exp["slide_index"]
        slide = slides[i]
        notes_text = ""
        if slide.has_notes_slide:
            notes_text = slide.notes_slide.notes_text_frame.text
        if exp["notes_fragment"] not in notes_text:
            errors.append(f"slide {i}: notes missing fragment {exp['notes_fragment']!r}; got {notes_text[:60]!r}")
    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, None


def _check_manifest_slide_count(prs, manifest, slides):
    """deck_manifest.json must report slide_count == 5."""
    if manifest is None:
        return 0.0, "deck_manifest.json missing"
    got = manifest.get("slide_count")
    if got != EXPECTED_SLIDE_COUNT:
        return 0.0, f"manifest.slide_count: expected {EXPECTED_SLIDE_COUNT}, got {got}"
    return 1.0, None


def _check_manifest_deck_title(prs, manifest, slides):
    """deck_manifest.json must report the correct deck_title."""
    if manifest is None:
        return 0.0, "deck_manifest.json missing"
    got = manifest.get("deck_title", "")
    want = "Meridian Analytics Platform"
    if got.strip() != want:
        return 0.0, f"manifest.deck_title: expected {want!r}, got {got!r}"
    return 1.0, None


def _check_manifest_emu_dimensions(prs, manifest, slides):
    """deck_manifest.json must report slide EMU dimensions matching the default 4:3 template."""
    if manifest is None:
        return 0.0, "deck_manifest.json missing"
    errors = []
    for key, want in [("slide_width_emu", 9144000), ("slide_height_emu", 6858000)]:
        got = manifest.get(key)
        if got != want:
            errors.append(f"manifest.{key}: expected {want}, got {got}")
    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, None


def _check_shape_type_invariant(prs, manifest, slides):
    """Every text-bearing shape must report shape_type PLACEHOLDER (14); no raw TEXT_BOX (17) shapes
    should appear instead of placeholders where the spec calls for a placeholder.
    The table on slide 2 must be shape_type TABLE (19), not PLACEHOLDER."""
    if prs is None:
        return 0.0, "product_deck.pptx missing"
    if len(slides) < EXPECTED_SLIDE_COUNT:
        return 0.0, f"only {len(slides)} slides"
    errors = []
    for exp in EXPECTED_SLIDES:
        i = exp["slide_index"]
        slide = slides[i]
        types = {int(s.shape_type) for s in slide.shapes}
        # All content-carrying shapes that are not tables should be PLACEHOLDER
        non_table_types = types - {MSO_TABLE}
        if MSO_PLACEHOLDER not in non_table_types and len(slide.shapes) > 0:
            has_table_only = (types == {MSO_TABLE})
            if not has_table_only:
                errors.append(f"slide {i}: expected PLACEHOLDER shapes (14), got types {sorted(types)}")
        # Slide 2 must have a TABLE shape
        if exp["has_table"] and MSO_TABLE not in types:
            errors.append(f"slide {i}: expected TABLE shape (19), not found in types {sorted(types)}")
    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, None


# ---- Criterion registry -------------------------------------------------------

CRITERIA = [
    {
        "id": "pptx-exists",
        "weight": 0.03,
        "description": "product_deck.pptx exists at the workspace root and opens without error using python-pptx.",
        "check": _check_pptx_exists,
    },
    {
        "id": "manifest-exists",
        "weight": 0.02,
        "description": "deck_manifest.json exists at the workspace root and is valid JSON.",
        "check": _check_manifest_exists,
    },
    {
        "id": "slide-count",
        "weight": 0.06,
        "description": "product_deck.pptx contains exactly 5 slides, matching the slide count in deck_spec.json.",
        "check": _check_slide_count,
    },
    {
        "id": "layout-names",
        "weight": 0.10,
        "description": "Each slide uses the exact layout named in deck_spec.json ('Title Slide', 'Title and Content', 'Title Only') — layout names are not portable and must be matched by name, not by index.",
        "check": _check_layout_names,
    },
    {
        "id": "title-text",
        "weight": 0.10,
        "description": "Each slide's title placeholder (idx=0) contains the exact title string from the spec.",
        "check": _check_title_text,
    },
    {
        "id": "subtitle-text",
        "weight": 0.07,
        "description": "Slides 0 and 4 use the 'Title Slide' layout; their subtitle placeholder (idx=1) must contain the subtitle strings from the spec. Using a text box instead of the placeholder silently puts content in the wrong layer.",
        "check": _check_subtitle_text,
    },
    {
        "id": "bullet-content",
        "weight": 0.07,
        "description": "Slides 1 and 3 use 'Title and Content' layout; their content placeholder (idx=1) must contain all three bullet strings from the spec.",
        "check": _check_bullet_content,
    },
    {
        "id": "table-shape-type",
        "weight": 0.07,
        "description": "Slide 2 must have a TABLE shape (MSO shape type 19), not a placeholder. Using add_table() on the slide directly is the correct approach; trying to add a table inside a content placeholder produces a different shape type.",
        "check": _check_table_shape_type,
    },
    {
        "id": "table-dimensions",
        "weight": 0.05,
        "description": "The table on slide 2 must be exactly 4 rows × 4 columns, matching the Pricing Tiers spec (header + 3 data rows, four columns Tier/Monthly Price/Data Volume/Seats).",
        "check": _check_table_dimensions,
    },
    {
        "id": "table-header-row",
        "weight": 0.07,
        "description": "Table header row on slide 2 must exactly match ['Tier', 'Monthly Price', 'Data Volume', 'Seats'] — column names must be identical to the spec, not paraphrased.",
        "check": _check_table_header_row,
    },
    {
        "id": "table-data-content",
        "weight": 0.07,
        "description": "Table data rows (1–3) on slide 2 must exactly match the pricing tier values: Starter/$299/100 GB, Growth/$899/1 TB, Enterprise/Custom/Unlimited.",
        "check": _check_table_data_content,
    },
    {
        "id": "table-emu-position",
        "weight": 0.08,
        "description": "Table position on slide 2 must match the EMU coordinates in the spec (left=457200, top=1371600, width=8229600, height=2286000). Using Inches() approximations or ignoring the spec coordinates fails this check.",
        "check": _check_table_emu_position,
    },
    {
        "id": "notes-present",
        "weight": 0.05,
        "description": "Slides 0, 1, and 3 must have non-empty speaker notes as required by the spec; slides 2 and 4 must have no notes.",
        "check": _check_notes_present,
    },
    {
        "id": "notes-content",
        "weight": 0.04,
        "description": "Speaker notes on slides 0, 1, and 3 must contain the required text fragments from the spec (e.g. 'Welcome attendees', 'latency', 'anomaly').",
        "check": _check_notes_content,
    },
    {
        "id": "manifest-slide-count",
        "weight": 0.03,
        "description": "deck_manifest.json.slide_count must equal 5 — an invariant cross-checking that the manifest accurately reflects the saved PPTX.",
        "check": _check_manifest_slide_count,
    },
    {
        "id": "manifest-deck-title",
        "weight": 0.02,
        "description": "deck_manifest.json.deck_title must equal 'Meridian Analytics Platform' exactly.",
        "check": _check_manifest_deck_title,
    },
    {
        "id": "manifest-emu-dimensions",
        "weight": 0.03,
        "description": "deck_manifest.json must report slide_width_emu=9144000 and slide_height_emu=6858000 (default 4:3 template), proving the agent read back the actual dimensions rather than hard-coding them.",
        "check": _check_manifest_emu_dimensions,
    },
    {
        "id": "shape-type-invariant",
        "weight": 0.04,
        "description": "All text-bearing shapes must be PLACEHOLDER type (14) not TEXT_BOX (17); the table on slide 2 must be TABLE type (19) — a stateful invariant that text boxes silently placed outside the placeholder hierarchy violate.",
        "check": _check_shape_type_invariant,
    },
]

_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    prs, prs_err = _load_pptx(workspace_path)
    manifest, man_err = _load_manifest(workspace_path)
    slides = _get_slides(prs)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](prs, manifest, slides)
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

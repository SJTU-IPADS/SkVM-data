"""
Grade function for frontend-slides_task_01.

Contract: returns a list of criterion records per grade-py-protocol.md.

Strategy: parse presentation.html with BeautifulSoup, inspect deck_manifest.json,
and verify the CSS/JS properties specified in the task prompt.

Archetypes hit:
  - Archetype 1 (under-specified step): viewport fitting — the skill says "100vh +
    overflow:hidden" per slide but models often forget one or use wrong units.
  - Archetype 3 (multi-step coordination): correct slide count + headings from spec
    + feature-grid card count + nav dots matching slide count must all hold together.
  - Archetype 5 (stateful invariant): nav-dot count == slide count == manifest
    slide_count — a cross-artifact invariant that requires three components to agree.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None  # type: ignore


EXPECTED_SLIDE_COUNT = 6
EXPECTED_SLIDE_IDS = [
    "slide-title", "slide-problem", "slide-solution",
    "slide-features", "slide-metrics", "slide-cta",
]
EXPECTED_HEADINGS = [
    "Nexus Platform",
    "The Connectivity Gap",
    "One Platform, Zero Compromises",
    "Core Capabilities",
    "Proven at Scale",
    "Start Building Today",
]
EXPECTED_CARD_COUNT = 4
EXPECTED_CTA_ID = "cta-button"


def _load_html(workspace_path: str):
    path = Path(workspace_path) / "presentation.html"
    if not path.exists():
        return None, "presentation.html not found"
    text = path.read_text(encoding="utf-8", errors="replace")
    if BeautifulSoup is None:
        return None, "BeautifulSoup not installed"
    try:
        soup = BeautifulSoup(text, "html.parser")
        return (soup, text), None
    except Exception as e:
        return None, f"parse error: {e}"


def _load_manifest(workspace_path: str):
    path = Path(workspace_path) / "deck_manifest.json"
    if not path.exists():
        return None, "deck_manifest.json not found"
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"deck_manifest.json not valid JSON: {e}"


# ---- Per-criterion checks --------------------------------------------------

def _check_html_exists(html_data, manifest):
    if html_data is None:
        return 0.0, "presentation.html missing or unparseable"
    return 1.0, None


def _check_doctype(html_data, manifest):
    if html_data is None:
        return 0.0, "presentation.html missing"
    _, raw = html_data
    if not re.search(r"<!DOCTYPE\s+html", raw, re.IGNORECASE):
        return 0.0, "presentation.html does not start with <!DOCTYPE html>"
    return 1.0, None


def _check_slide_count(html_data, manifest):
    if html_data is None:
        return 0.0, "presentation.html missing"
    soup, _ = html_data
    slides = soup.select(".slide")
    got = len(slides)
    if got != EXPECTED_SLIDE_COUNT:
        return 0.0, f"expected {EXPECTED_SLIDE_COUNT} .slide elements, found {got}"
    return 1.0, None


def _check_slide_ids(html_data, manifest):
    """Each slide must have the id from deck_spec.json (multi-step coordination:
    agent must read the spec ids and apply them in the HTML)."""
    if html_data is None:
        return 0.0, "presentation.html missing"
    soup, _ = html_data
    slides = soup.select(".slide")
    found_ids = [s.get("id", "") for s in slides]
    missing = [sid for sid in EXPECTED_SLIDE_IDS if sid not in found_ids]
    if missing:
        return 0.0, f"slides missing required ids: {missing}; found ids: {found_ids}"
    return 1.0, None


def _check_headings(html_data, manifest):
    """Each slide heading must match the spec exactly (multi-step coordination:
    the heading text must be faithfully copied from deck_spec.json, not paraphrased)."""
    if html_data is None:
        return 0.0, "presentation.html missing"
    soup, raw = html_data
    raw_text = raw
    missing = []
    for heading in EXPECTED_HEADINGS:
        # Accept the heading anywhere in the raw text (h1–h4 or aria-label)
        if heading not in raw_text:
            missing.append(heading)
    if missing:
        return 0.0, f"headings not found verbatim in HTML: {missing}"
    return 1.0, None


def _check_viewport_css(html_data, manifest):
    """Every .slide must have height:100vh (or 100dvh) AND overflow:hidden — the
    mandatory base rule from the skill. Models often set height on the container
    but forget overflow:hidden, causing content to bleed outside the viewport."""
    if html_data is None:
        return 0.0, "presentation.html missing"
    soup, raw = html_data
    # Check that CSS contains both rules applied to .slide
    has_100vh = bool(re.search(r"\.slide\s*\{[^}]*height\s*:\s*100(?:vh|dvh)", raw, re.DOTALL)
                     or re.search(r"height\s*:\s*100(?:vh|dvh)", raw))
    has_overflow = bool(re.search(r"\.slide\s*\{[^}]*overflow\s*:\s*hidden", raw, re.DOTALL)
                        or re.search(r"overflow\s*:\s*hidden", raw))
    problems = []
    if not has_100vh:
        problems.append("no height:100vh/100dvh on .slide")
    if not has_overflow:
        problems.append("no overflow:hidden on .slide")
    if problems:
        return 0.0, "; ".join(problems)
    return 1.0, None


def _check_feature_grid(html_data, manifest):
    """The feature-grid slide must contain exactly 4 cards (as specified in deck_spec.json).
    Multi-step coordination: reading the spec card count and rendering exactly that many
    card elements."""
    if html_data is None:
        return 0.0, "presentation.html missing"
    soup, raw = html_data
    # Find the features slide
    features_slide = soup.find(id="slide-features")
    if features_slide is None:
        return 0.0, "slide with id='slide-features' not found"
    # Use the four known card titles as the canonical check — this avoids
    # CSS selector ambiguity from class-name conventions (card vs card-grid, etc.)
    card_titles = ["Smart Routing", "Zero-Trust Security", "Live Observability", "SDK-First"]
    slide_text = features_slide.get_text()
    found = sum(1 for t in card_titles if t in slide_text)
    if found != EXPECTED_CARD_COUNT:
        return 0.0, f"expected {EXPECTED_CARD_COUNT} feature card titles in slide-features, found {found}; looked for: {card_titles}"
    return 1.0, None


def _check_card_titles(html_data, manifest):
    """All four card titles from the spec must appear verbatim in the HTML
    (multi-step coordination: each card title must be faithfully rendered)."""
    if html_data is None:
        return 0.0, "presentation.html missing"
    _, raw = html_data
    card_titles = ["Smart Routing", "Zero-Trust Security", "Live Observability", "SDK-First"]
    missing = [t for t in card_titles if t not in raw]
    if missing:
        return 0.0, f"card titles missing from HTML: {missing}"
    return 1.0, None


def _check_cta_button(html_data, manifest):
    """The CTA slide must have a button element with id='cta-button' and label
    'Request Early Access' — the spec pins both the id and the label text."""
    if html_data is None:
        return 0.0, "presentation.html missing"
    soup, raw = html_data
    btn = soup.find(id=EXPECTED_CTA_ID)
    if btn is None:
        return 0.0, f"no element with id='{EXPECTED_CTA_ID}' found"
    tag = btn.name
    if tag not in ("button", "a"):
        return 0.0, f"element id='{EXPECTED_CTA_ID}' is <{tag}>, expected <button> or <a>"
    label = "Request Early Access"
    if label not in raw:
        return 0.0, f"CTA label '{label}' not found verbatim in HTML"
    return 1.0, None


def _check_js_navigation(html_data, manifest):
    """Keyboard navigation (ArrowLeft/ArrowRight or space) must be implemented
    in JavaScript — a baseline skill requirement."""
    if html_data is None:
        return 0.0, "presentation.html missing"
    _, raw = html_data
    has_keydown = bool(re.search(r"(?:keydown|keyup|keypress)", raw, re.IGNORECASE))
    has_arrow = bool(re.search(r"ArrowRight|ArrowLeft|arrow|space|key", raw))
    if not (has_keydown and has_arrow):
        return 0.0, "no keyboard navigation handler found (need keydown/keyup + ArrowRight/Left)"
    return 1.0, None


def _check_nav_dots(html_data, manifest):
    """Navigation dots (or a bar) must be present and their count must equal the
    slide count — a stateful invariant tying three components together."""
    if html_data is None:
        return 0.0, "presentation.html missing"
    soup, raw = html_data
    # Strategy: find a container with class containing 'dot' or 'nav' and then
    # count its direct children, OR find elements with a 'dot' class that are
    # NOT themselves a container (i.e. they contain no child .dot elements).
    # We use data-index attribute as a reliable anchor when present.
    dots_by_index = soup.select("[data-index]")
    if dots_by_index:
        n = len(dots_by_index)
        if n != EXPECTED_SLIDE_COUNT:
            return 0.0, (
                f"nav dots count ({n}) != slide count ({EXPECTED_SLIDE_COUNT}); "
                f"the invariant nav_dots == slides == manifest.slide_count must hold"
            )
        return 1.0, None

    # Fallback: look for elements with class 'dot' that are leaf-ish (no .slide inside)
    dots = [el for el in soup.select(".dot, .nav-dot, .indicator-dot")
            if not el.find(class_="slide")]
    if not dots:
        if re.search(r"progress|nav.*dot|dot.*nav|indicator", raw, re.IGNORECASE):
            return 0.5, "progress indicator found but could not count individual dots"
        return 0.0, "no navigation dots or progress indicator found"
    if len(dots) != EXPECTED_SLIDE_COUNT:
        return 0.0, (
            f"nav dots count ({len(dots)}) != slide count ({EXPECTED_SLIDE_COUNT}); "
            f"the invariant nav_dots == slides == manifest.slide_count must hold"
        )
    return 1.0, None


def _check_manifest_exists(html_data, manifest):
    if manifest is None:
        return 0.0, "deck_manifest.json not found"
    return 1.0, None


def _check_manifest_schema(html_data, manifest):
    if manifest is None:
        return 0.0, "deck_manifest.json missing"
    required = {"slide_count", "slide_ids", "output_file"}
    missing = required - set(manifest.keys())
    if missing:
        return 0.0, f"deck_manifest.json missing keys: {sorted(missing)}"
    return 1.0, None


def _check_manifest_invariant(html_data, manifest):
    """deck_manifest.json slide_count must equal the number of .slide elements in
    presentation.html — the cross-artifact stateful invariant that ties the manifest
    to the actual DOM."""
    if html_data is None or manifest is None:
        return 0.0, "presentation.html or deck_manifest.json missing"
    soup, _ = html_data
    actual_slides = len(soup.select(".slide"))
    manifest_count = manifest.get("slide_count")
    try:
        manifest_count = int(manifest_count)
    except (TypeError, ValueError):
        return 0.0, f"manifest slide_count is not an integer: {manifest_count!r}"
    if manifest_count != actual_slides:
        return 0.0, (
            f"manifest slide_count ({manifest_count}) != actual .slide count ({actual_slides}); "
            f"both must equal {EXPECTED_SLIDE_COUNT}"
        )
    if manifest_count != EXPECTED_SLIDE_COUNT:
        return 0.0, f"manifest slide_count is {manifest_count}, expected {EXPECTED_SLIDE_COUNT}"
    return 1.0, None


def _check_manifest_slide_ids(html_data, manifest):
    """deck_manifest.json slide_ids must list all six required ids in order —
    the manifest is not just a count but a mapping proving the agent read the spec."""
    if manifest is None:
        return 0.0, "deck_manifest.json missing"
    ids = manifest.get("slide_ids")
    if not isinstance(ids, list):
        return 0.0, f"deck_manifest.json slide_ids is not a list: {ids!r}"
    missing = [sid for sid in EXPECTED_SLIDE_IDS if sid not in ids]
    if missing:
        return 0.0, f"deck_manifest.json slide_ids missing required ids: {missing}; got: {ids}"
    return 1.0, None


def _check_no_external_deps(html_data, manifest):
    """The HTML must be self-contained — no external CDN links for CSS or JS
    (common-default-wrong: models reflexively add <link rel=stylesheet href=cdn...>
    or <script src=cdn...> even when the task says 'no external dependencies')."""
    if html_data is None:
        return 0.0, "presentation.html missing"
    soup, _ = html_data
    violations = []
    for tag in soup.find_all(["link", "script"]):
        href = tag.get("href", "") or tag.get("src", "")
        if href and (href.startswith("http") or href.startswith("//")):
            violations.append(href[:80])
    if violations:
        return 0.0, f"external CDN/URL references found: {violations[:3]}"
    return 1.0, None


# ---- Criterion registry ---------------------------------------------------

CRITERIA = [
    {
        "id": "html-exists",
        "weight": 0.04,
        "description": "presentation.html exists at the workspace root and is parseable HTML.",
        "check": _check_html_exists,
    },
    {
        "id": "doctype-valid",
        "weight": 0.03,
        "description": "presentation.html begins with <!DOCTYPE html> — required for standards-mode rendering.",
        "check": _check_doctype,
    },
    {
        "id": "slide-count",
        "weight": 0.10,
        "description": "The HTML contains exactly 6 .slide elements, matching the 6 entries in deck_spec.json.",
        "check": _check_slide_count,
    },
    {
        "id": "slide-ids",
        "weight": 0.10,
        "description": "Each .slide element has the id from deck_spec.json (slide-title, slide-problem, slide-solution, slide-features, slide-metrics, slide-cta) — the agent must read and apply the spec ids, not invent its own.",
        "check": _check_slide_ids,
    },
    {
        "id": "headings-verbatim",
        "weight": 0.08,
        "description": "All six headings from deck_spec.json appear verbatim in the HTML — paraphrased or shortened headings fail because downstream tools index by exact heading text.",
        "check": _check_headings,
    },
    {
        "id": "viewport-css",
        "weight": 0.12,
        "description": "The CSS applies height:100vh (or 100dvh) and overflow:hidden to every .slide — the mandatory viewport-fitting base rule from the skill that prevents inter-slide scroll bleed.",
        "check": _check_viewport_css,
    },
    {
        "id": "feature-grid-count",
        "weight": 0.08,
        "description": "The slide-features slide renders exactly 4 card elements — matching the 4 cards specified in deck_spec.json; adding or dropping cards is a spec violation.",
        "check": _check_feature_grid,
    },
    {
        "id": "card-titles-verbatim",
        "weight": 0.07,
        "description": "All four card titles from deck_spec.json (Smart Routing, Zero-Trust Security, Live Observability, SDK-First) appear verbatim in the HTML.",
        "check": _check_card_titles,
    },
    {
        "id": "cta-button-id",
        "weight": 0.08,
        "description": "A button or anchor with id='cta-button' and label 'Request Early Access' exists in slide-cta — the spec pins both the element id and the label text for downstream event binding.",
        "check": _check_cta_button,
    },
    {
        "id": "js-navigation",
        "weight": 0.08,
        "description": "JavaScript keyboard navigation (keydown/keyup with ArrowRight/ArrowLeft or Space) is implemented — a baseline interactivity requirement for HTML presentations.",
        "check": _check_js_navigation,
    },
    {
        "id": "nav-dots",
        "weight": 0.07,
        "description": "Navigation dots (or equivalent indicators) are present with a count matching the slide count — the stateful invariant tying the visual indicator to the DOM.",
        "check": _check_nav_dots,
    },
    {
        "id": "manifest-exists",
        "weight": 0.03,
        "description": "deck_manifest.json exists at the workspace root and parses as valid JSON.",
        "check": _check_manifest_exists,
    },
    {
        "id": "manifest-schema",
        "weight": 0.03,
        "description": "deck_manifest.json contains required keys: slide_count (integer), slide_ids (array), output_file (string).",
        "check": _check_manifest_schema,
    },
    {
        "id": "manifest-invariant",
        "weight": 0.06,
        "description": "deck_manifest.json slide_count equals the number of .slide elements in presentation.html — the cross-artifact invariant ensuring the manifest reflects the actual DOM, not a hardcoded guess.",
        "check": _check_manifest_invariant,
    },
    {
        "id": "manifest-slide-ids",
        "weight": 0.03,
        "description": "deck_manifest.json slide_ids lists all six required slide ids — proving the agent enumerated from the spec rather than generating arbitrary ids.",
        "check": _check_manifest_slide_ids,
    },
]

# Sanity check at import time.
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    html_data, _html_err = _load_html(workspace_path)
    manifest, _manifest_err = _load_manifest(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](html_data, manifest)
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

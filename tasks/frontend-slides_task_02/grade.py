"""
Grade function for frontend-slides_task_02.

Contract: returns a list of criterion records per grade-py-protocol.md.

Strategy: parse talk.html with BeautifulSoup, inspect talk_manifest.json,
and verify CSS/JS properties specified in the task prompt.

Archetypes hit:
  - Archetype 2 (common-default-wrong): no external CDN dependencies — models
    reflexively insert Google Fonts or framework CDN links even when banned.
  - Archetype 3 (multi-step coordination): speaker notes as HTML comments in each
    slide + slide counter text + mouse-wheel navigation must all coexist.
  - Archetype 4 (known-edge-case): dark background verification — the skill
    specifies a dark background but models often use dark-ish colors that don't
    actually meet the threshold; we check CSS background-color values.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup, Comment
except ImportError:
    BeautifulSoup = None  # type: ignore
    Comment = None  # type: ignore


EXPECTED_SLIDE_COUNT = 6
EXPECTED_SLIDE_IDS = [
    "slide-cover", "slide-agenda", "slide-today",
    "slide-failures", "slide-breakthrough", "slide-cta",
]
EXPECTED_HEADINGS = [
    "The Future of AI Agents",
    "What We Will Cover",
    "Where Agents Are Today",
    "The Three Failure Modes",
    "The Coordination Breakthrough",
    "What You Should Build Next",
]
# Speaker notes as they appear in the fixture (trimmed)
EXPECTED_NOTES_FRAGMENTS = [
    "autonomous agents will replace 30%",
    "Keep this slide under 30 seconds",
    "Cite the HellaSwag",
    "GitHub Copilot incident",
    "This is the thesis slide",
    "concrete, time-bounded",
]
REQUIRED_MANIFEST_KEYS = {"slide_count", "slide_ids", "has_speaker_notes", "output_file"}


def _load_html(workspace_path: str):
    path = Path(workspace_path) / "talk.html"
    if not path.exists():
        return None, "talk.html not found"
    text = path.read_text(encoding="utf-8", errors="replace")
    if BeautifulSoup is None:
        return None, "BeautifulSoup not installed"
    try:
        soup = BeautifulSoup(text, "html.parser")
        return (soup, text), None
    except Exception as e:
        return None, f"parse error: {e}"


def _load_manifest(workspace_path: str):
    path = Path(workspace_path) / "talk_manifest.json"
    if not path.exists():
        return None, "talk_manifest.json not found"
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"talk_manifest.json not valid JSON: {e}"


# ---- Helpers ---------------------------------------------------------------

def _is_dark_color(css_value: str) -> bool:
    """Return True if the CSS color string is definitively dark (all RGB channels <= 60)."""
    css_value = css_value.strip().lower()
    # hex #rrggbb
    m = re.match(r"#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$", css_value)
    if m:
        r, g, b = int(m.group(1), 16), int(m.group(2), 16), int(m.group(3), 16)
        return r <= 60 and g <= 60 and b <= 60
    # hex #rgb
    m = re.match(r"#([0-9a-f])([0-9a-f])([0-9a-f])$", css_value)
    if m:
        r = int(m.group(1) * 2, 16)
        g = int(m.group(2) * 2, 16)
        b = int(m.group(3) * 2, 16)
        return r <= 60 and g <= 60 and b <= 60
    # rgb(r, g, b)
    m = re.match(r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", css_value)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return r <= 60 and g <= 60 and b <= 60
    return False


def _extract_bg_colors(raw: str) -> list[str]:
    """Extract all background-color values from inline CSS."""
    return re.findall(r"background(?:-color)?\s*:\s*([^;}\n]+)", raw, re.IGNORECASE)


# ---- Per-criterion checks --------------------------------------------------

def _check_html_exists(html_data, manifest):
    if html_data is None:
        return 0.0, "talk.html missing or unparseable"
    return 1.0, None


def _check_doctype(html_data, manifest):
    if html_data is None:
        return 0.0, "talk.html missing"
    _, raw = html_data
    if not re.search(r"<!DOCTYPE\s+html", raw, re.IGNORECASE):
        return 0.0, "talk.html does not start with <!DOCTYPE html>"
    return 1.0, None


def _check_no_external_deps(html_data, manifest):
    """No external CDN links for CSS or JS — a common-default-wrong trap where models
    instinctively add Google Fonts or Reveal.js CDN even when the task bans them."""
    if html_data is None:
        return 0.0, "talk.html missing"
    soup, _ = html_data
    violations = []
    for tag in soup.find_all(["link", "script"]):
        href = tag.get("href", "") or tag.get("src", "")
        if href and (href.startswith("http") or href.startswith("//")):
            violations.append(href[:80])
    if violations:
        return 0.0, f"external CDN/URL references found (banned — all assets must be inline): {violations[:3]}"
    return 1.0, None


def _check_slide_count(html_data, manifest):
    if html_data is None:
        return 0.0, "talk.html missing"
    soup, _ = html_data
    slides = soup.select(".slide")
    got = len(slides)
    if got != EXPECTED_SLIDE_COUNT:
        return 0.0, f"expected {EXPECTED_SLIDE_COUNT} .slide elements, found {got}"
    return 1.0, None


def _check_slide_ids(html_data, manifest):
    """Each slide must carry the id from talk_outline.json — multi-step coordination:
    the agent must read the outline ids and apply them in the HTML."""
    if html_data is None:
        return 0.0, "talk.html missing"
    soup, _ = html_data
    slides = soup.select(".slide")
    found_ids = [s.get("id", "") for s in slides]
    missing = [sid for sid in EXPECTED_SLIDE_IDS if sid not in found_ids]
    if missing:
        return 0.0, f"slides missing required ids: {missing}; found ids: {found_ids}"
    return 1.0, None


def _check_headings_verbatim(html_data, manifest):
    """All six headings from the outline must appear verbatim in the HTML —
    multi-step coordination: faithful transcription across all slides."""
    if html_data is None:
        return 0.0, "talk.html missing"
    _, raw = html_data
    missing = [h for h in EXPECTED_HEADINGS if h not in raw]
    if missing:
        return 0.0, f"headings not found verbatim in HTML: {missing}"
    return 1.0, None


def _check_dark_background(html_data, manifest):
    """The CSS background color of the presentation (body, html, or .slide) must be
    a genuinely dark color with all RGB channels <= 60 — the skill's dark-theme
    rule. Models often use '#1a1a2e' (channels 26/26/46 — OK) or '#333' (51 — OK)
    but sometimes use '#404040' (64 — fails the <=60 threshold)."""
    if html_data is None:
        return 0.0, "talk.html missing"
    _, raw = html_data
    bg_values = _extract_bg_colors(raw)
    if not bg_values:
        return 0.0, "no background-color or background found in CSS"
    # Accept if at least one dark background is applied (body, html, or .slide)
    dark_found = [v.strip() for v in bg_values if _is_dark_color(v.strip())]
    if not dark_found:
        sample = [v.strip()[:30] for v in bg_values[:4]]
        return 0.0, (
            f"no dark background color found (all RGB channels must be <= 60); "
            f"sampled values: {sample}"
        )
    return 1.0, None


def _check_viewport_css(html_data, manifest):
    """Every .slide must have height:100vh (or 100dvh) AND overflow:hidden —
    the mandatory viewport lock from the skill."""
    if html_data is None:
        return 0.0, "talk.html missing"
    _, raw = html_data
    has_100vh = bool(re.search(r"height\s*:\s*100(?:vh|dvh)", raw))
    has_overflow = bool(re.search(r"overflow\s*:\s*hidden", raw))
    problems = []
    if not has_100vh:
        problems.append("no height:100vh/100dvh on .slide")
    if not has_overflow:
        problems.append("no overflow:hidden on .slide")
    if problems:
        return 0.0, "; ".join(problems)
    return 1.0, None


def _check_speaker_notes(html_data, manifest):
    """Each slide must embed its speaker note as an HTML comment inside the slide
    element. Multi-step coordination: the agent must read all six notes from
    talk_outline.json and inject them at the right place in the DOM."""
    if html_data is None:
        return 0.0, "talk.html missing"
    soup, raw = html_data
    # Check for the note fragments as HTML comments anywhere in the file
    missing = []
    for fragment in EXPECTED_NOTES_FRAGMENTS:
        # The fragment must appear inside an HTML comment <!-- ... -->
        pattern = re.compile(r"<!--.*?" + re.escape(fragment) + r".*?-->", re.DOTALL)
        if not pattern.search(raw):
            missing.append(fragment[:40])
    if missing:
        return 0.0, (
            f"{len(missing)} speaker note(s) missing as HTML comments: {missing}; "
            f"each speaker_note from talk_outline.json must be embedded as <!-- ... --> inside its slide"
        )
    return 1.0, None


def _check_slide_counter(html_data, manifest):
    """A visible slide counter of the form 'N / 6' or 'N of 6' must exist —
    multi-step coordination: the counter must reflect the total correctly."""
    if html_data is None:
        return 0.0, "talk.html missing"
    _, raw = html_data
    # Look for "X / 6" or "X of 6" or a template like "1/6" in JS/HTML
    counter_re = re.compile(r"\d\s*/\s*6|\d\s+of\s+6|of\s+\{\{?\s*total|currentSlide.*?total", re.IGNORECASE)
    # Also accept a static indicator referencing "6" total
    has_counter = bool(counter_re.search(raw))
    if not has_counter:
        # Softer check: any pattern matching "slide-counter" or "counter" element with "6"
        has_element = bool(re.search(r"(?:counter|slide.?num|slide.?count)", raw, re.IGNORECASE))
        has_six = "6" in raw
        if not (has_element and has_six):
            return 0.0, "no slide counter of the form 'N / 6' found — implement a visible counter showing current slide out of total"
        return 0.5, "counter element present but 'N / 6' pattern not clearly detectable"
    return 1.0, None


def _check_wheel_navigation(html_data, manifest):
    """Mouse-wheel navigation must be implemented in JavaScript — a multi-step
    coordination requirement layered on top of keyboard navigation."""
    if html_data is None:
        return 0.0, "talk.html missing"
    _, raw = html_data
    has_wheel = bool(re.search(r"wheel|scroll\b", raw, re.IGNORECASE))
    has_listener = bool(re.search(r"addEventListener", raw))
    if not (has_wheel and has_listener):
        return 0.0, "no wheel/scroll event listener found — mouse-wheel navigation is required alongside keyboard navigation"
    return 1.0, None


def _check_keyboard_navigation(html_data, manifest):
    """Keyboard navigation (ArrowRight/ArrowLeft) must be implemented."""
    if html_data is None:
        return 0.0, "talk.html missing"
    _, raw = html_data
    has_keydown = bool(re.search(r"keydown|keyup", raw, re.IGNORECASE))
    has_arrow = bool(re.search(r"ArrowRight|ArrowLeft|arrow", raw))
    if not (has_keydown and has_arrow):
        return 0.0, "no keyboard navigation handler found (need keydown/keyup + ArrowRight/Left)"
    return 1.0, None


def _check_manifest_exists(html_data, manifest):
    if manifest is None:
        return 0.0, "talk_manifest.json not found"
    return 1.0, None


def _check_manifest_schema(html_data, manifest):
    if manifest is None:
        return 0.0, "talk_manifest.json missing"
    missing = REQUIRED_MANIFEST_KEYS - set(manifest.keys())
    if missing:
        return 0.0, f"talk_manifest.json missing keys: {sorted(missing)}"
    return 1.0, None


def _check_manifest_slide_count_invariant(html_data, manifest):
    """talk_manifest.json slide_count must equal the number of .slide elements —
    the cross-artifact stateful invariant."""
    if html_data is None or manifest is None:
        return 0.0, "talk.html or talk_manifest.json missing"
    soup, _ = html_data
    actual = len(soup.select(".slide"))
    declared = manifest.get("slide_count")
    try:
        declared = int(declared)
    except (TypeError, ValueError):
        return 0.0, f"talk_manifest.json slide_count is not an integer: {declared!r}"
    if declared != actual:
        return 0.0, f"manifest slide_count ({declared}) != DOM .slide count ({actual})"
    if declared != EXPECTED_SLIDE_COUNT:
        return 0.0, f"manifest slide_count is {declared}, expected {EXPECTED_SLIDE_COUNT}"
    return 1.0, None


def _check_manifest_notes_flag(html_data, manifest):
    """talk_manifest.json has_speaker_notes must be true — the manifest must
    honestly report that speaker notes are present."""
    if manifest is None:
        return 0.0, "talk_manifest.json missing"
    flag = manifest.get("has_speaker_notes")
    if flag is not True:
        return 0.0, f"talk_manifest.json has_speaker_notes should be true, got {flag!r}"
    return 1.0, None


# ---- Criterion registry ---------------------------------------------------

CRITERIA = [
    {
        "id": "html-exists",
        "weight": 0.03,
        "description": "talk.html exists at the workspace root and is parseable HTML.",
        "check": _check_html_exists,
    },
    {
        "id": "doctype-valid",
        "weight": 0.02,
        "description": "talk.html begins with <!DOCTYPE html> — required for standards-mode rendering.",
        "check": _check_doctype,
    },
    {
        "id": "no-external-deps",
        "weight": 0.10,
        "description": "talk.html contains no external CDN links (<link href=http...> or <script src=http...>) — the task bans external dependencies and models commonly add Google Fonts or framework CDN links by reflex.",
        "check": _check_no_external_deps,
    },
    {
        "id": "slide-count",
        "weight": 0.07,
        "description": "talk.html contains exactly 6 .slide elements matching the 6 entries in talk_outline.json.",
        "check": _check_slide_count,
    },
    {
        "id": "slide-ids",
        "weight": 0.07,
        "description": "Each .slide carries the id from talk_outline.json (slide-cover, slide-agenda, slide-today, slide-failures, slide-breakthrough, slide-cta) — the agent must read and apply the spec ids.",
        "check": _check_slide_ids,
    },
    {
        "id": "headings-verbatim",
        "weight": 0.06,
        "description": "All six headings from talk_outline.json appear verbatim in talk.html — paraphrased or shortened headings break the spec contract.",
        "check": _check_headings_verbatim,
    },
    {
        "id": "dark-background",
        "weight": 0.10,
        "description": "The CSS background color of the presentation is genuinely dark — all RGB channels <= 60. The skill specifies dark mode but models often choose dark-ish grays (e.g. #606060 = 96/96/96) that fail this threshold.",
        "check": _check_dark_background,
    },
    {
        "id": "viewport-css",
        "weight": 0.07,
        "description": "CSS applies height:100vh (or 100dvh) and overflow:hidden to .slide — the mandatory viewport-fitting rule that prevents inter-slide content bleed.",
        "check": _check_viewport_css,
    },
    {
        "id": "speaker-notes",
        "weight": 0.15,
        "description": "All six speaker notes from talk_outline.json are embedded as HTML comments (<!-- ... -->) inside their respective slides. Multi-step coordination: the agent must read every note and inject it at the correct DOM location.",
        "check": _check_speaker_notes,
    },
    {
        "id": "slide-counter",
        "weight": 0.08,
        "description": "A visible slide counter showing 'N / 6' (current slide out of total) is implemented — multi-step coordination: the counter must reference the correct total and update with navigation.",
        "check": _check_slide_counter,
    },
    {
        "id": "wheel-navigation",
        "weight": 0.08,
        "description": "Mouse-wheel navigation is implemented with a 'wheel' or 'scroll' event listener — a layered requirement on top of keyboard navigation that models often omit.",
        "check": _check_wheel_navigation,
    },
    {
        "id": "keyboard-navigation",
        "weight": 0.05,
        "description": "Keyboard navigation via ArrowRight/ArrowLeft is implemented with a keydown/keyup listener.",
        "check": _check_keyboard_navigation,
    },
    {
        "id": "manifest-exists",
        "weight": 0.03,
        "description": "talk_manifest.json exists and parses as valid JSON.",
        "check": _check_manifest_exists,
    },
    {
        "id": "manifest-schema",
        "weight": 0.03,
        "description": "talk_manifest.json contains required keys: slide_count, slide_ids, has_speaker_notes, output_file.",
        "check": _check_manifest_schema,
    },
    {
        "id": "manifest-slide-count-invariant",
        "weight": 0.04,
        "description": "talk_manifest.json slide_count equals the actual number of .slide elements in talk.html — the cross-artifact invariant proving the manifest was computed from the DOM, not hardcoded.",
        "check": _check_manifest_slide_count_invariant,
    },
    {
        "id": "manifest-notes-flag",
        "weight": 0.02,
        "description": "talk_manifest.json has_speaker_notes is true — the manifest must honestly report the speaker-notes feature that was requested.",
        "check": _check_manifest_notes_flag,
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

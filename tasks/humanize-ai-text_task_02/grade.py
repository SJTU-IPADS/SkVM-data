"""
Grade function for humanize-ai-text_task_02.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: direct checks on clean.md and changes.json.

The task requires the agent to:
  1. Rewrite article.md -> clean.md, removing all filler transition phrases.
  2. Produce changes.json with total_removed, counts_by_category, and a
     list of changes entries.

Archetypes hit:
  2. Common-default-wrong — models default to keeping "Additionally,",
     "Furthermore,", "Moreover," even when asked to humanize text, because
     these transitions feel natural to AI output.
  3. Multi-step coordination — the agent must both rewrite AND produce a
     structured JSON report whose counts match the actual rewrite.
  5. Stateful invariant — changes.json total_removed must equal the number of
     banned-phrase instances actually removed from the rewrite; section
     structure must be preserved.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Fixture properties (computed offline from fixtures/article.md)
# ---------------------------------------------------------------------------
ORIGINAL_WORD_COUNT = 412   # words in article.md
ORIGINAL_HEADERS = {
    "the role of renewable energy in modern infrastructure",
    "solar power",
    "wind power",
    "storage and the grid",
    "policy context",
}

# Banned phrases that must not appear in clean.md
BANNED_FILLERS = [
    "it's important to note",
    "it is important to note",
    "it's worth noting",
    "it is worth noting",
    "additionally,",
    "furthermore,",
    "moreover,",
    "in addition to",
    "it is crucial to understand",
    "it goes without saying",
    "in order to",
    "due to the fact that",
]

# Specific ChatGPT-default transitions (common-default-wrong trap)
CHATGPT_TRANSITIONS = [
    "additionally,",
    "furthermore,",
    "moreover,",
]

# Required top-level keys in changes.json
REQUIRED_JSON_KEYS = {"total_removed", "counts_by_category", "changes"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_clean(workspace_path: str):
    path = Path(workspace_path) / "clean.md"
    if not path.exists():
        return None, "clean.md not found in workspace"
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text.strip()) < 100:
        return None, f"clean.md is too short ({len(text.strip())} chars)"
    return text, None


def _load_changes(workspace_path: str):
    path = Path(workspace_path) / "changes.json"
    if not path.exists():
        return None, "changes.json not found in workspace"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return None, f"changes.json is not valid JSON: {e}"
    return data, None


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _extract_headers(text: str) -> list[str]:
    return [h.strip().lower() for h in re.findall(r"^#{1,6}\s+(.+)$", text, re.MULTILINE)]


# ---------------------------------------------------------------------------
# Per-criterion checks
# ---------------------------------------------------------------------------

def _check_clean_exists(clean, changes, err_c, err_j):
    if clean is None:
        return 0.0, err_c or "clean.md missing"
    return 1.0, None


def _check_headers_preserved(clean, changes, err_c, err_j):
    if clean is None:
        return 0.0, "clean.md missing"
    found = set(_extract_headers(clean))
    missing = ORIGINAL_HEADERS - found
    if missing:
        return 0.0, f"section headers removed from clean.md: {sorted(missing)}"
    return 1.0, None


def _check_word_count_ratio(clean, changes, err_c, err_j):
    if clean is None:
        return 0.0, "clean.md missing"
    out_wc = _word_count(clean)
    ratio = out_wc / ORIGINAL_WORD_COUNT
    if not (0.70 <= ratio <= 1.10):
        return 0.0, (
            f"word count ratio {ratio:.2f} outside [0.70, 1.10]: "
            f"clean.md has {out_wc} words vs original {ORIGINAL_WORD_COUNT}"
        )
    return 1.0, None


def _check_no_filler_phrases(clean, changes, err_c, err_j):
    """All banned filler phrases must be gone from clean.md."""
    if clean is None:
        return 0.0, "clean.md missing"
    found = [f for f in BANNED_FILLERS if f.lower() in clean.lower()]
    if found:
        return 0.0, f"banned filler phrases still present in clean.md: {found}"
    return 1.0, None


def _check_no_chatgpt_transitions(clean, changes, err_c, err_j):
    """Specifically 'Additionally,', 'Furthermore,', 'Moreover,' — the canonical
    ChatGPT transition phrases that models most commonly retain even when humanizing.
    This is a dedicated criterion because it is the highest-frequency failure mode."""
    if clean is None:
        return 0.0, "clean.md missing"
    found = [t for t in CHATGPT_TRANSITIONS if t.lower() in clean.lower()]
    if found:
        return 0.0, (
            f"ChatGPT-default sentence-starting transitions still present in clean.md: {found}. "
            "These are the most common AI transition markers and must be completely removed."
        )
    return 1.0, None


def _check_changes_exists(clean, changes, err_c, err_j):
    if changes is None:
        return 0.0, err_j or "changes.json missing"
    return 1.0, None


def _check_changes_schema(clean, changes, err_c, err_j):
    if changes is None:
        return 0.0, "changes.json missing"
    missing = REQUIRED_JSON_KEYS - set(changes.keys())
    if missing:
        return 0.0, f"changes.json missing required keys: {sorted(missing)}"
    if not isinstance(changes.get("changes"), list):
        return 0.0, "changes.json 'changes' field must be a list"
    if not isinstance(changes.get("counts_by_category"), dict):
        return 0.0, "changes.json 'counts_by_category' must be an object"
    return 1.0, None


def _check_total_removed_reasonable(clean, changes, err_c, err_j):
    """total_removed must be between 8 and 15 — the fixture has 11 instances and
    the reference removes all of them. Accepting 8–15 tolerates minor phrase
    interpretation differences without accepting a wildly wrong count."""
    if changes is None:
        return 0.0, "changes.json missing"
    total = changes.get("total_removed")
    try:
        total = int(total)
    except (TypeError, ValueError):
        return 0.0, f"total_removed is not an integer: {total!r}"
    if not (8 <= total <= 15):
        return 0.0, (
            f"total_removed={total} is outside the acceptable range [8, 15]. "
            "The fixture contains 11 banned-phrase instances; the model should remove all or most."
        )
    return 1.0, None


def _check_counts_by_category_coverage(clean, changes, err_c, err_j):
    """counts_by_category must account for at least 2 distinct categories of
    filler removal, showing the agent distinguished types."""
    if changes is None:
        return 0.0, "changes.json missing"
    cbc = changes.get("counts_by_category", {})
    if not isinstance(cbc, dict):
        return 0.0, "counts_by_category is not a dict"
    if len(cbc) < 2:
        return 0.0, (
            f"counts_by_category has only {len(cbc)} category (need at least 2). "
            "The fixture has filler-hedge, chatgpt-transition, verbose-phrase, and filler-cliche groups."
        )
    return 1.0, None


def _check_changes_list_nonempty(clean, changes, err_c, err_j):
    """changes list must be non-empty and each entry must have at least 'phrase' and 'category'."""
    if changes is None:
        return 0.0, "changes.json missing"
    ch = changes.get("changes", [])
    if not ch:
        return 0.0, "changes list is empty"
    bad = []
    for i, entry in enumerate(ch[:5]):  # spot-check first 5
        if not isinstance(entry, dict):
            bad.append(f"entry {i} is not a dict")
        elif "phrase" not in entry:
            bad.append(f"entry {i} missing 'phrase' key")
    if bad:
        return 0.0, f"malformed changes entries: {bad}"
    return 1.0, None


def _check_total_matches_list(clean, changes, err_c, err_j):
    """Stateful invariant: total_removed must equal len(changes). A common failure
    is when the model reports a count in the JSON that does not match its actual list."""
    if changes is None:
        return 0.0, "changes.json missing"
    total = changes.get("total_removed")
    ch = changes.get("changes", [])
    try:
        total_int = int(total)
    except (TypeError, ValueError):
        return 0.0, f"total_removed not an integer: {total!r}"
    list_len = len(ch) if isinstance(ch, list) else 0
    if total_int != list_len:
        return 0.0, (
            f"total_removed={total_int} does not match len(changes)={list_len}. "
            "The count field must equal the actual number of entries in the changes list."
        )
    return 1.0, None


# ---------------------------------------------------------------------------
# CRITERIA list (weights must sum to 1.0)
# ---------------------------------------------------------------------------

CRITERIA = [
    {
        "id": "clean-exists",
        "weight": 0.05,
        "description": "clean.md exists at the workspace root with substantive content (at least 100 characters).",
        "check": _check_clean_exists,
    },
    {
        "id": "headers-preserved",
        "weight": 0.08,
        "description": (
            "All 5 section headers from article.md are preserved verbatim in clean.md "
            "(case-insensitive match): 'The Role of Renewable Energy in Modern Infrastructure', "
            "'Solar Power', 'Wind Power', 'Storage and the Grid', 'Policy Context'. "
            "Rewriting must not remove or rename sections."
        ),
        "check": _check_headers_preserved,
    },
    {
        "id": "word-count-ratio",
        "weight": 0.07,
        "description": (
            "The word count of clean.md is between 70% and 110% of the original 412 words (288–453). "
            "Removing filler phrases produces a modest reduction; values outside this band indicate "
            "either a gutted rewrite or bloated additions."
        ),
        "check": _check_word_count_ratio,
    },
    {
        "id": "no-filler-phrases",
        "weight": 0.20,
        "description": (
            "None of the 11 banned filler phrases appear in clean.md: "
            "'it's important to note', 'it is worth noting', 'additionally,', 'furthermore,', "
            "'moreover,', 'in addition to', 'it is crucial to understand', "
            "'it goes without saying', 'in order to', 'due to the fact that'. "
            "Every instance from the original must be removed or rewritten."
        ),
        "check": _check_no_filler_phrases,
    },
    {
        "id": "no-chatgpt-transitions",
        "weight": 0.15,
        "description": (
            "The three canonical ChatGPT sentence-starting transitions are absent from clean.md: "
            "'Additionally,', 'Furthermore,', 'Moreover,'. These are the most common AI-default "
            "transitions and are the primary common-default-wrong trap in this task — models "
            "frequently retain them even when told to humanize."
        ),
        "check": _check_no_chatgpt_transitions,
    },
    {
        "id": "changes-exists",
        "weight": 0.05,
        "description": "changes.json exists at the workspace root and parses as valid JSON.",
        "check": _check_changes_exists,
    },
    {
        "id": "changes-schema",
        "weight": 0.07,
        "description": (
            "changes.json has the required top-level keys: total_removed (integer), "
            "counts_by_category (object), and changes (list). Each entry in the changes "
            "list must be an object with at least a 'phrase' key."
        ),
        "check": _check_changes_schema,
    },
    {
        "id": "total-removed-reasonable",
        "weight": 0.10,
        "description": (
            "changes.json total_removed is between 8 and 15. The fixture contains 11 banned-phrase "
            "instances; the model should identify and remove all or most of them. "
            "A count outside this range indicates systematic under- or over-counting."
        ),
        "check": _check_total_removed_reasonable,
    },
    {
        "id": "counts-by-category-coverage",
        "weight": 0.08,
        "description": (
            "counts_by_category in changes.json lists at least 2 distinct categories, "
            "showing the agent distinguished between phrase types (e.g. filler-hedge vs "
            "chatgpt-transition vs verbose-phrase). A single-category report indicates "
            "the agent did not coordinate the multi-step detection and classification."
        ),
        "check": _check_counts_by_category_coverage,
    },
    {
        "id": "changes-list-nonempty",
        "weight": 0.05,
        "description": (
            "The changes list in changes.json is non-empty and each entry is a dict "
            "with at least a 'phrase' key documenting which filler phrase was removed."
        ),
        "check": _check_changes_list_nonempty,
    },
    {
        "id": "total-matches-list",
        "weight": 0.10,
        "description": (
            "Stateful invariant: total_removed must equal the length of the changes list. "
            "A mismatch means the agent reported a count that does not match its own evidence — "
            "a multi-step coordination failure where the summary and the detail diverge."
        ),
        "check": _check_total_matches_list,
    },
]

# Sanity check at import time
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    clean, err_c = _load_clean(workspace_path)
    changes, err_j = _load_changes(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](clean, changes, err_c, err_j)
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

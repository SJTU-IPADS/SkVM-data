"""
Grade function for humanizer_task_02.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: direct checks on clean.md and audit.json in the workspace.

The task requires the agent to:
  1. Rewrite article.md -> clean.md, removing all AI filler phrases and vocabulary.
  2. Produce audit.json with total_replacements, by_category breakdown, and
     an items list where each entry names the phrase and its category.

Archetypes hit:
  2. Common-default-wrong — models keep ChatGPT transitions (Additionally, Furthermore,
     Moreover) and AI vocabulary (tapestry, serves as a testament, cornerstone, landscape)
     even when humanizing structured markdown content.
  3. Multi-step coordination — the agent must rewrite AND produce an audit JSON whose
     counts are derived from the actual changes made, not estimated.
  5. Stateful invariant — audit.json total_replacements must equal len(items); section
     headers must be preserved exactly in clean.md.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Fixture properties (computed offline from fixtures/article.md)
# ---------------------------------------------------------------------------
ORIGINAL_WORD_COUNT = 316   # words in article.md
ORIGINAL_HEADERS = {
    "the rise of saas in enterprise technology",
    "overview",
    "adoption patterns",
    "integration challenges",
    "vendor management",
    "conclusion",
}

# Banned AI vocabulary -- must not appear in clean.md (case-insensitive word boundary)
BANNED_VOCAB = [
    "cornerstone",
    "tapestry",
    "landscape",
    "pivotal",
    "multifaceted",
    "groundbreaking",
    "undoubtedly",
    "delve",
    "delving",
    "foster",
    "fostering",
    "leverage",
]

# Banned filler / hedging phrases -- must not appear in clean.md (case-insensitive substring)
BANNED_FILLERS = [
    "it's worth noting",
    "it is worth noting",
    "it's important to note",
    "it is important to note",
    "it is crucial to understand",
    "it goes without saying",
    "nothing short of",
    "serves as a testament",
    "in order to",
    "due to the fact that",
]

# ChatGPT-default sentence-starting transitions -- dedicated list (highest failure mode)
CHATGPT_TRANSITIONS = [
    "additionally,",
    "furthermore,",
    "moreover,",
]

BANNED_CHATBOT = [
    "i hope",
    "feel free",
    "as an ai",
]

# Required keys in audit.json
REQUIRED_AUDIT_KEYS = {"total_replacements", "by_category", "items"}

# Acceptable range for total_replacements (fixture has ~22 banned items)
TOTAL_MIN = 12
TOTAL_MAX = 28


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


def _load_audit(workspace_path: str):
    path = Path(workspace_path) / "audit.json"
    if not path.exists():
        return None, "audit.json not found in workspace"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return None, f"audit.json is not valid JSON: {e}"
    return data, None


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _extract_headers(text: str) -> set:
    return {h.strip().lower() for h in re.findall(r"^#{1,6}\s+(.+)$", text, re.MULTILINE)}


# ---------------------------------------------------------------------------
# Per-criterion checks
# ---------------------------------------------------------------------------

def _check_clean_exists(clean, audit, ec, ea):
    if clean is None:
        return 0.0, ec or "clean.md missing"
    return 1.0, None


def _check_headers_preserved(clean, audit, ec, ea):
    if clean is None:
        return 0.0, "clean.md missing"
    found = _extract_headers(clean)
    missing = ORIGINAL_HEADERS - found
    if missing:
        return 0.0, (
            f"section headers missing from clean.md: {sorted(missing)}. "
            "All 6 markdown headers must be preserved exactly."
        )
    return 1.0, None


def _check_word_count_ratio(clean, audit, ec, ea):
    if clean is None:
        return 0.0, "clean.md missing"
    out_wc = _word_count(clean)
    ratio = out_wc / ORIGINAL_WORD_COUNT
    if not (0.70 <= ratio <= 1.10):
        return 0.0, (
            f"word count ratio {ratio:.2f} outside [0.70, 1.10]: "
            f"clean.md has {out_wc} words vs original {ORIGINAL_WORD_COUNT}. "
            "Removing filler phrases should produce a modest reduction."
        )
    return 1.0, None


def _check_no_chatgpt_transitions(clean, audit, ec, ea):
    """'Additionally,', 'Furthermore,', 'Moreover,' are the primary common-default-wrong trap.
    Models almost always retain these when rewriting markdown articles."""
    if clean is None:
        return 0.0, "clean.md missing"
    found = [t for t in CHATGPT_TRANSITIONS if t.lower() in clean.lower()]
    if found:
        return 0.0, (
            f"ChatGPT-default sentence-starting transitions still present: {found}. "
            "These are the most common AI transition markers -- they must be completely "
            "removed or restructured."
        )
    return 1.0, None


def _check_no_filler_phrases(clean, audit, ec, ea):
    if clean is None:
        return 0.0, "clean.md missing"
    found = [t for t in BANNED_FILLERS if t.lower() in clean.lower()]
    if found:
        return 0.0, f"banned filler phrases still present in clean.md: {found}"
    return 1.0, None


def _check_no_banned_vocab(clean, audit, ec, ea):
    if clean is None:
        return 0.0, "clean.md missing"
    found = [t for t in BANNED_VOCAB if re.search(r'\b' + re.escape(t) + r'\b', clean, re.IGNORECASE)]
    if found:
        return 0.0, f"banned AI vocabulary still present in clean.md: {found}"
    return 1.0, None


def _check_no_chatbot_artifacts(clean, audit, ec, ea):
    if clean is None:
        return 0.0, "clean.md missing"
    found = [t for t in BANNED_CHATBOT if t.lower() in clean.lower()]
    if found:
        return 0.0, (
            f"chatbot artifact phrases still present: {found}. "
            "The article ends with 'I hope this analysis has been helpful. Feel free to contact us' -- "
            "these sentences must be removed."
        )
    return 1.0, None


def _check_audit_exists(clean, audit, ec, ea):
    if audit is None:
        return 0.0, ea or "audit.json missing"
    return 1.0, None


def _check_audit_schema(clean, audit, ec, ea):
    if audit is None:
        return 0.0, "audit.json missing"
    missing = REQUIRED_AUDIT_KEYS - set(audit.keys())
    if missing:
        return 0.0, f"audit.json missing required keys: {sorted(missing)}"
    if not isinstance(audit.get("items"), list):
        return 0.0, "audit.json 'items' must be a list"
    if not isinstance(audit.get("by_category"), dict):
        return 0.0, "audit.json 'by_category' must be an object"
    items = audit.get("items", [])
    if items:
        first = items[0]
        if not isinstance(first, dict) or "phrase" not in first:
            return 0.0, "audit.json items entries must be objects with at least a 'phrase' key"
    return 1.0, None


def _check_total_replacements_range(clean, audit, ec, ea):
    """total_replacements must be in [12, 28]. The fixture has ~22 banned instances."""
    if audit is None:
        return 0.0, "audit.json missing"
    total = audit.get("total_replacements")
    try:
        total = int(total)
    except (TypeError, ValueError):
        return 0.0, f"total_replacements is not an integer: {total!r}"
    if not (TOTAL_MIN <= total <= TOTAL_MAX):
        return 0.0, (
            f"total_replacements={total} is outside [{TOTAL_MIN}, {TOTAL_MAX}]. "
            "The fixture contains approximately 22 banned phrase/vocab instances."
        )
    return 1.0, None


def _check_by_category_coverage(clean, audit, ec, ea):
    """by_category must have at least 3 distinct keys, showing the agent categorized
    the different types of AI patterns (e.g. ai-vocab, filler-phrase, chatgpt-transition)."""
    if audit is None:
        return 0.0, "audit.json missing"
    cbc = audit.get("by_category", {})
    if not isinstance(cbc, dict):
        return 0.0, "by_category is not a dict"
    if len(cbc) < 3:
        return 0.0, (
            f"by_category has only {len(cbc)} category/categories (need at least 3). "
            "The fixture has AI vocabulary, filler-hedge phrases, ChatGPT transitions, and chatbot "
            "artifacts -- the agent should distinguish at least 3 of these types."
        )
    return 1.0, None


def _check_total_matches_items(clean, audit, ec, ea):
    """Stateful invariant: total_replacements must equal len(items). A common failure is
    the agent estimating or hardcoding a count that does not match its logged changes."""
    if audit is None:
        return 0.0, "audit.json missing"
    total = audit.get("total_replacements")
    items = audit.get("items", [])
    try:
        total_int = int(total)
    except (TypeError, ValueError):
        return 0.0, f"total_replacements not an integer: {total!r}"
    items_len = len(items) if isinstance(items, list) else 0
    if total_int != items_len:
        return 0.0, (
            f"total_replacements={total_int} does not match len(items)={items_len}. "
            "The count field must equal the actual number of entries in the items list."
        )
    return 1.0, None


# ---------------------------------------------------------------------------
# CRITERIA list (weights must sum to 1.0)
# ---------------------------------------------------------------------------

CRITERIA = [
    {
        "id": "clean-exists",
        "weight": 0.05,
        "description": "clean.md exists at the workspace root with at least 100 characters of content.",
        "check": _check_clean_exists,
    },
    {
        "id": "headers-preserved",
        "weight": 0.08,
        "description": (
            "All 6 markdown section headers from article.md are preserved in clean.md "
            "(case-insensitive): 'The Rise of SaaS in Enterprise Technology', 'Overview', "
            "'Adoption Patterns', 'Integration Challenges', 'Vendor Management', 'Conclusion'. "
            "Rewriting must not remove or rename any section."
        ),
        "check": _check_headers_preserved,
    },
    {
        "id": "word-count-ratio",
        "weight": 0.06,
        "description": (
            "The word count of clean.md is between 70% and 110% of the original 316 words "
            "(221-347 words). Removing filler phrases produces a modest reduction; values "
            "outside this band indicate either a gutted rewrite or bloated additions."
        ),
        "check": _check_word_count_ratio,
    },
    {
        "id": "no-chatgpt-transitions",
        "weight": 0.16,
        "description": (
            "The ChatGPT-default sentence-starting transitions are absent from clean.md: "
            "'Additionally,', 'Furthermore,', 'Moreover,'. The fixture has 4 instances of these "
            "transitions. Retaining them is the most common common-default-wrong failure in "
            "text humanization tasks."
        ),
        "check": _check_no_chatgpt_transitions,
    },
    {
        "id": "no-filler-phrases",
        "weight": 0.14,
        "description": (
            "None of the banned filler/hedge phrases appear in clean.md: "
            "'it's worth noting', 'it is important to note', 'it is crucial to understand', "
            "'it goes without saying', 'nothing short of', 'serves as a testament', "
            "'in order to', 'due to the fact that'. Every instance must be removed or rewritten."
        ),
        "check": _check_no_filler_phrases,
    },
    {
        "id": "no-banned-vocab",
        "weight": 0.14,
        "description": (
            "None of the banned AI vocabulary words appear in clean.md: cornerstone, tapestry, "
            "landscape, pivotal, multifaceted, groundbreaking, undoubtedly, delve/delving, "
            "foster/fostering, leverage. These are primary AI-vocabulary markers."
        ),
        "check": _check_no_banned_vocab,
    },
    {
        "id": "no-chatbot-artifacts",
        "weight": 0.07,
        "description": (
            "Chatbot artifact phrases are absent: 'I hope', 'Feel free', 'As an AI'. "
            "The article's conclusion ends with 'I hope this analysis has been helpful. "
            "Feel free to contact us for a personalized assessment.' -- both sentences must be removed."
        ),
        "check": _check_no_chatbot_artifacts,
    },
    {
        "id": "audit-exists",
        "weight": 0.05,
        "description": "audit.json exists at the workspace root and parses as valid JSON.",
        "check": _check_audit_exists,
    },
    {
        "id": "audit-schema",
        "weight": 0.07,
        "description": (
            "audit.json has the required top-level keys: total_replacements (integer), "
            "by_category (object), and items (list). Each items entry must be an object "
            "with at least a 'phrase' key documenting what was removed."
        ),
        "check": _check_audit_schema,
    },
    {
        "id": "total-replacements-range",
        "weight": 0.08,
        "description": (
            "audit.json total_replacements is between 12 and 28. The fixture contains "
            "approximately 22 banned pattern instances across AI vocabulary, filler phrases, "
            "ChatGPT transitions, and chatbot artifacts. A count outside this range indicates "
            "systematic under- or over-counting."
        ),
        "check": _check_total_replacements_range,
    },
    {
        "id": "by-category-coverage",
        "weight": 0.06,
        "description": (
            "audit.json by_category has at least 3 distinct keys, showing the agent classified "
            "the different types of AI patterns (e.g. ai-vocab, filler-phrase, chatgpt-transition, "
            "chatbot-artifact). A single-category or two-category audit indicates the agent did "
            "not distinguish between pattern families."
        ),
        "check": _check_by_category_coverage,
    },
    {
        "id": "total-matches-items",
        "weight": 0.04,
        "description": (
            "Stateful invariant: audit.json total_replacements must equal the length of the items "
            "list. A mismatch means the agent reported a summary count that does not match its own "
            "detailed log -- a multi-step coordination failure."
        ),
        "check": _check_total_matches_items,
    },
]

# Sanity check at import time
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    clean, ec = _load_clean(workspace_path)
    audit, ea = _load_audit(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](clean, audit, ec, ea)
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

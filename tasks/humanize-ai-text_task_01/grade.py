"""
Grade function for humanize-ai-text_task_01.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: direct text checks on output.txt in the workspace.
The task requires the agent to rewrite a 5-paragraph AI-generated supply-chain
article per a strict humanization protocol. All checks are structural/lexical —
subjective prose quality is handled by the llm-judge.

Archetypes hit:
  1. Under-specified step — the rewrite verb is pinned to a specific banned-token
     list and paragraph-count protocol.
  2. Common-default-wrong — models default to keeping "landscape", "pivotal",
     "furthermore," and em-dashes even when asked to humanize.
  5. Stateful invariant — paragraph count and word-count ratio must be preserved.
"""
from __future__ import annotations

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Expected fixture properties (computed from fixtures/input.txt offline)
# ---------------------------------------------------------------------------
ORIGINAL_WORD_COUNT = 234   # words in input.txt
ORIGINAL_PARA_COUNT = 5     # non-empty paragraphs in input.txt

# Banned tokens — must not appear in output.txt (case-insensitive)
# These are all explicitly named in the task prompt.
BANNED_VOCAB = [
    "delve",
    "tapestry",
    "pivotal",
    "multifaceted",
    "groundbreaking",
    "undoubtedly",
    "hallmark",
    "cornerstone",
]

BANNED_FILLERS = [
    "it's important to note",
    "it's worth noting",
    "in order to",
    "due to the fact that",
    "furthermore,",
    "indeed,",
]

BANNED_INFLATION = [
    "cannot be overstated",
    "nothing short of",
    "serves as a testament",
]

BANNED_CHATBOT = [
    "i hope",
    "feel free",
    "as an ai",
    "great question",
]

# Markdown patterns that must NOT appear (input had none)
MARKDOWN_BOLD_RE = re.compile(r"\*\*.+?\*\*", re.DOTALL)
MARKDOWN_HEADER_RE = re.compile(r"^#{1,6}\s", re.MULTILINE)
MARKDOWN_BULLET_RE = re.compile(r"^\s*[-*]\s", re.MULTILINE)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_output(workspace_path: str):
    path = Path(workspace_path) / "output.txt"
    if not path.exists():
        return None, "output.txt not found in workspace"
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text.strip()) < 50:
        return None, f"output.txt is too short ({len(text.strip())} chars)"
    return text, None


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _para_count(text: str) -> int:
    return len([p for p in text.split("\n\n") if p.strip()])


# ---------------------------------------------------------------------------
# Per-criterion check functions
# ---------------------------------------------------------------------------

def _check_output_exists(text, err):
    if text is None:
        return 0.0, err or "output.txt missing"
    return 1.0, None


def _check_para_count(text, err):
    if text is None:
        return 0.0, "output.txt missing"
    got = _para_count(text)
    if got != ORIGINAL_PARA_COUNT:
        return 0.0, (
            f"paragraph count changed: expected {ORIGINAL_PARA_COUNT}, got {got}. "
            "The prompt requires paragraph count to match the input exactly."
        )
    return 1.0, None


def _check_word_count_ratio(text, err):
    if text is None:
        return 0.0, "output.txt missing"
    out_wc = _word_count(text)
    ratio = out_wc / ORIGINAL_WORD_COUNT
    if not (0.80 <= ratio <= 1.20):
        return 0.0, (
            f"word count ratio {ratio:.2f} outside [0.80, 1.20]: "
            f"output has {out_wc} words, original has {ORIGINAL_WORD_COUNT}."
        )
    return 1.0, None


def _check_no_banned_vocab(text, err):
    if text is None:
        return 0.0, "output.txt missing"
    found = [t for t in BANNED_VOCAB if t.lower() in text.lower()]
    if found:
        return 0.0, f"banned AI vocabulary still present: {found}"
    return 1.0, None


def _check_no_filler_phrases(text, err):
    if text is None:
        return 0.0, "output.txt missing"
    found = [t for t in BANNED_FILLERS if t.lower() in text.lower()]
    if found:
        return 0.0, f"banned filler phrases still present: {found}"
    return 1.0, None


def _check_no_inflation(text, err):
    if text is None:
        return 0.0, "output.txt missing"
    found = [t for t in BANNED_INFLATION if t.lower() in text.lower()]
    if found:
        return 0.0, f"significance inflation phrases still present: {found}"
    return 1.0, None


def _check_no_chatbot_artifacts(text, err):
    if text is None:
        return 0.0, "output.txt missing"
    found = [t for t in BANNED_CHATBOT if t.lower() in text.lower()]
    if found:
        return 0.0, f"chatbot artifact phrases still present: {found}"
    return 1.0, None


def _check_no_em_dashes(text, err):
    if text is None:
        return 0.0, "output.txt missing"
    count = text.count("\u2014")
    if count > 0:
        return 0.0, f"em-dash (—) appears {count} time(s); must be replaced with comma or period"
    return 1.0, None


def _check_no_landscape(text, err):
    """'landscape' is one of the most common AI defaults — a dedicated criterion
    because models reliably keep it even when other vocab is removed."""
    if text is None:
        return 0.0, "output.txt missing"
    if "landscape" in text.lower():
        return 0.0, (
            "'landscape' (as a business/tech metaphor) still present. "
            "This is one of the primary AI vocabulary markers listed in the prompt."
        )
    return 1.0, None


def _check_no_markdown_added(text, err):
    """The input had no markdown. Adding bold/headers/bullets is a common-default-wrong
    behavior where models improve formatting when asked to rewrite."""
    if text is None:
        return 0.0, "output.txt missing"
    issues = []
    if MARKDOWN_BOLD_RE.search(text):
        issues.append("bold (**...**)")
    if MARKDOWN_HEADER_RE.search(text):
        issues.append("headers (## ...)")
    if MARKDOWN_BULLET_RE.search(text):
        issues.append("bullets (- or *)")
    if issues:
        return 0.0, (
            f"markdown introduced where input had none: {issues}. "
            "The prompt requires no formatting changes beyond prose rewriting."
        )
    return 1.0, None


# ---------------------------------------------------------------------------
# CRITERIA list (weights sum to 1.0)
# ---------------------------------------------------------------------------

CRITERIA = [
    {
        "id": "output-exists",
        "weight": 0.05,
        "description": "output.txt exists at the workspace root with at least 50 characters of content.",
        "check": _check_output_exists,
    },
    {
        "id": "para-count-invariant",
        "weight": 0.10,
        "description": (
            "The rewritten text has exactly 5 paragraphs (double-newline separated), matching the "
            "input's paragraph count. This stateful invariant ensures the agent didn't collapse or "
            "split the section structure."
        ),
        "check": _check_para_count,
    },
    {
        "id": "word-count-ratio",
        "weight": 0.08,
        "description": (
            "The output word count is between 80% and 120% of the original 234 words (187–281 words). "
            "Ratios outside this band indicate either a gutted rewrite or bloated padding."
        ),
        "check": _check_word_count_ratio,
    },
    {
        "id": "no-banned-vocab",
        "weight": 0.18,
        "description": (
            "None of the explicitly banned AI vocabulary tokens appear in output.txt: "
            "delve, tapestry, pivotal, multifaceted, groundbreaking, undoubtedly, hallmark, cornerstone. "
            "These are the primary AI-vocabulary markers the prompt requires removal of."
        ),
        "check": _check_no_banned_vocab,
    },
    {
        "id": "no-landscape",
        "weight": 0.12,
        "description": (
            "'landscape' (used as a business/technology metaphor) must not appear in the output. "
            "It appears twice in the input and is explicitly listed as a banned term. "
            "Models commonly retain it even when other banned terms are removed."
        ),
        "check": _check_no_landscape,
    },
    {
        "id": "no-filler-phrases",
        "weight": 0.15,
        "description": (
            "None of the banned filler phrases appear: 'it's important to note', 'it's worth noting', "
            "'in order to', 'due to the fact that', 'furthermore,', 'indeed,'. "
            "These are medium-signal AI filler patterns that must be rewritten or removed."
        ),
        "check": _check_no_filler_phrases,
    },
    {
        "id": "no-significance-inflation",
        "weight": 0.12,
        "description": (
            "Significance inflation phrases are absent: 'cannot be overstated', 'nothing short of', "
            "'serves as a testament'. These puffery constructions are high-signal AI markers "
            "and must be removed per the prompt's protocol."
        ),
        "check": _check_no_inflation,
    },
    {
        "id": "no-chatbot-artifacts",
        "weight": 0.08,
        "description": (
            "Chatbot artifact phrases are absent from output.txt: 'I hope', 'Feel free', "
            "'As an AI', 'Great question'. The original had 'I hope this analysis has been helpful' "
            "at the end — the model must remove it entirely."
        ),
        "check": _check_no_chatbot_artifacts,
    },
    {
        "id": "no-em-dashes",
        "weight": 0.07,
        "description": (
            "No em-dashes (—) appear in the output. The input contained one em-dash used for "
            "emphasis; the prompt requires em-dashes to be replaced with commas or periods."
        ),
        "check": _check_no_em_dashes,
    },
    {
        "id": "no-markdown-added",
        "weight": 0.05,
        "description": (
            "No markdown formatting (bold **...**, headers ##, or bullets -/*) was introduced. "
            "The input was plain prose with no markdown. Adding formatting is a common-default-wrong "
            "reflex where models 'improve' text structure when asked to rewrite."
        ),
        "check": _check_no_markdown_added,
    },
]

# Sanity check at import time
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    text, err = _load_output(workspace_path)
    records = []
    for spec in CRITERIA:
        score, details = spec["check"](text, err)
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

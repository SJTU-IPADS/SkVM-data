"""
Grade function for humanizer_task_01.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: direct text checks on output.txt in the workspace.

The task requires the agent to rewrite a 4-paragraph AI-generated healthcare/
telemedicine blog post per a strict humanization protocol. All checks are
structural/lexical — subjective prose quality is handled by the llm-judge.

Archetypes hit:
  2. Common-default-wrong — models keep curly/smart quotes and AI vocabulary
     (groundbreaking, landscape, pivotal, undoubtedly) even when asked to humanize.
  4. Known-edge-case — "Not only...but also" negative parallelism is a documented
     AI writing pattern that models almost never flag or remove without explicit
     instruction; curly quotes left over from ChatGPT copy-paste are similarly
     under-caught.
"""
from __future__ import annotations

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Fixture properties
# ---------------------------------------------------------------------------
ORIGINAL_WORD_COUNT = 260   # words in draft.txt
ORIGINAL_PARA_COUNT = 4     # non-empty paragraphs in draft.txt

# Smart/curly quote codepoints — must be straightened in output.txt
CURLY_OPEN  = "\u201c"   # "
CURLY_CLOSE = "\u201d"   # "
CURLY_APOS  = "\u2019"   # '

# Banned AI vocabulary tokens (case-insensitive whole-word match)
BANNED_VOCAB = [
    "groundbreaking",
    "landscape",
    "delving",
    "delve",
    "pivotal",
    "multifaceted",
    "undoubtedly",
    "hallmark",
    "cornerstone",
    "foster",
    "fostering",
    "leverage",
]

# Banned filler / chatbot phrases
BANNED_FILLERS = [
    "it's important to note",
    "it\u2019s important to note",  # curly-apostrophe variant
    "it is important to note",
    "furthermore,",
    "in order to",
    "due to the fact that",
    "cannot be overstated",
    "nothing short of",
]

BANNED_CHATBOT = [
    "i hope",
    "feel free",
    "as an ai",
]

# Negative parallelism trigger phrase — both halves
NOT_ONLY_RE = re.compile(r"not only.{0,200}but (it )?also", re.IGNORECASE | re.DOTALL)

# "serve as" / "serves as" copula avoidance phrase
SERVE_AS_RE = re.compile(r"\bserves?\s+as\b", re.IGNORECASE)

# "boast" / "boasts" copula avoidance
BOAST_RE = re.compile(r"\bboasts?\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_output(workspace_path: str):
    path = Path(workspace_path) / "output.txt"
    if not path.exists():
        return None, "output.txt not found in workspace"
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text.strip()) < 50:
        return None, f"output.txt too short ({len(text.strip())} chars)"
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
            "The prompt requires the output to have exactly 4 paragraphs matching the input."
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


def _check_no_curly_quotes(text, err):
    """Curly/smart quotes (\u201c \u201d \u2019) must be replaced with straight ASCII
    equivalents. The fixture contains ChatGPT-signature curly quotes around a filler
    phrase and around a direct quotation. Models commonly leave these unchanged."""
    if text is None:
        return 0.0, "output.txt missing"
    found = []
    if CURLY_OPEN in text:
        found.append(f'left double curly quote \u201c (count: {text.count(CURLY_OPEN)})')
    if CURLY_CLOSE in text:
        found.append(f'right double curly quote \u201d (count: {text.count(CURLY_CLOSE)})')
    if CURLY_APOS in text:
        found.append(f'curly apostrophe \u2019 (count: {text.count(CURLY_APOS)})')
    if found:
        return 0.0, (
            f"smart/curly quotes remain in output.txt: {found}. "
            "The prompt requires all curly quotes to be replaced with straight ASCII "
            "quotes (' and \") — leaving them is a common-default-wrong failure."
        )
    return 1.0, None


def _check_no_negative_parallelism(text, err):
    """'Not only...but also' constructions must be rewritten. The fixture has 2 instances.
    This is a documented AI writing pattern (negative parallelism / rule-of-opposition)
    that models almost never remove without an explicit instruction to do so."""
    if text is None:
        return 0.0, "output.txt missing"
    matches = NOT_ONLY_RE.findall(text)
    if matches:
        return 0.0, (
            f"'Not only...but also' negative parallelism still present ({len(matches)} instance(s)). "
            "The prompt requires these constructions to be rewritten as direct statements."
        )
    return 1.0, None


def _check_no_banned_vocab(text, err):
    if text is None:
        return 0.0, "output.txt missing"
    found = [t for t in BANNED_VOCAB if re.search(r'\b' + re.escape(t) + r'\b', text, re.IGNORECASE)]
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


def _check_no_chatbot_artifacts(text, err):
    if text is None:
        return 0.0, "output.txt missing"
    found = [t for t in BANNED_CHATBOT if t.lower() in text.lower()]
    if found:
        return 0.0, f"chatbot artifact phrases still present: {found}"
    return 1.0, None


def _check_no_copula_avoidance(text, err):
    """'serves as' and 'boasts' are copula-avoidance patterns — AI writes 'serves as X'
    instead of 'is X', and 'boasts X' instead of 'has X'. The fixture has one instance
    each. These must be replaced with direct verbs."""
    if text is None:
        return 0.0, "output.txt missing"
    issues = []
    if SERVE_AS_RE.search(text):
        issues.append("'serves as' / 'serve as' (copula avoidance — replace with 'is'/'are')")
    if BOAST_RE.search(text):
        issues.append("'boasts' / 'boast' (copula avoidance — replace with 'has'/'have')")
    if issues:
        return 0.0, (
            f"copula-avoidance phrases still present: {issues}. "
            "The prompt requires these to be replaced with direct verbs."
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
        "weight": 0.08,
        "description": (
            "The rewritten text has exactly 4 paragraphs (double-newline separated), matching the "
            "input's paragraph count. This invariant ensures the agent did not collapse or split "
            "the section structure while rewriting."
        ),
        "check": _check_para_count,
    },
    {
        "id": "word-count-ratio",
        "weight": 0.07,
        "description": (
            "The output word count is between 80% and 120% of the original 260 words (208-312). "
            "Values outside this band indicate either a gutted rewrite or bloated padding."
        ),
        "check": _check_word_count_ratio,
    },
    {
        "id": "no-curly-quotes",
        "weight": 0.18,
        "description": (
            "All smart/curly quotes have been replaced with straight ASCII equivalents. "
            "The fixture contains 2 pairs of curly double-quotes (\u201c...\u201d) and 2 curly "
            "apostrophes (\u2019) — ChatGPT-signature artifacts. Leaving any curly quotes "
            "is the most common known-edge-case failure when humanizing copy-pasted AI text."
        ),
        "check": _check_no_curly_quotes,
    },
    {
        "id": "no-negative-parallelism",
        "weight": 0.17,
        "description": (
            "The 'Not only...but also' negative parallelism constructions are gone. "
            "The fixture has 2 instances of this AI writing pattern (one in para 1, one in para 4). "
            "This is a documented AI-default structure that models rarely remove without explicit "
            "instruction — a known-edge-case trap."
        ),
        "check": _check_no_negative_parallelism,
    },
    {
        "id": "no-banned-vocab",
        "weight": 0.17,
        "description": (
            "None of the explicitly banned AI vocabulary tokens appear in output.txt: "
            "groundbreaking, landscape, delving/delve, pivotal, multifaceted, undoubtedly, "
            "hallmark, cornerstone, foster/fostering, leverage. These are the primary AI-vocabulary "
            "markers the prompt requires removal of."
        ),
        "check": _check_no_banned_vocab,
    },
    {
        "id": "no-filler-phrases",
        "weight": 0.12,
        "description": (
            "None of the banned filler phrases appear: 'it's important to note' (including curly-"
            "apostrophe variant), 'furthermore,', 'in order to', 'due to the fact that', "
            "'cannot be overstated', 'nothing short of'. These medium-to-high-signal AI patterns "
            "must be rewritten or removed."
        ),
        "check": _check_no_filler_phrases,
    },
    {
        "id": "no-chatbot-artifacts",
        "weight": 0.08,
        "description": (
            "Chatbot artifact phrases are absent: 'I hope', 'Feel free', 'As an AI'. "
            "The original ends with 'I hope this overview has been helpful. Feel free to reach out' — "
            "both sentences must be removed entirely."
        ),
        "check": _check_no_chatbot_artifacts,
    },
    {
        "id": "no-copula-avoidance",
        "weight": 0.08,
        "description": (
            "Copula-avoidance phrases 'serves as' and 'boasts' are absent. The fixture uses "
            "'serve as a testament' (para 2) and 'boast sophisticated sensors' (para 2). "
            "These AI constructions must be replaced with direct verbs: 'is', 'has', etc."
        ),
        "check": _check_no_copula_avoidance,
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

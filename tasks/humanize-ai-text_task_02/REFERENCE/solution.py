"""
Reference solution for humanize-ai-text_task_02.

Reads article.md from cwd, removes all filler transition phrases per the
protocol, writes clean.md and changes.json. Intended to score 1.0 under grade.py.

Protocol:
- Remove / rewrite the following filler phrases (case-insensitive):
    "it's important to note that" / "it's important to note,"
    "it's worth noting that" / "it's worth noting,"
    "it is worth noting that" / "it is worth noting,"
    "additionally," (sentence-starting connector)
    "furthermore," (sentence-starting connector)
    "in addition to" -> rewrite
    "it is crucial to understand that"
    "it goes without saying that"
    "moreover," (sentence-starting connector)
    "in order to" -> rewrite as "to"
    "due to the fact that" -> rewrite as "because"
- Section headers must be preserved exactly
- Em-dashes may stay (they are not in the banned list for this task)
- Produce clean.md with the rewritten text
- Produce changes.json: list of {phrase, original_sentence, replacement_note}
  for each removal, plus top-level counts_by_category and total_removed
"""

from __future__ import annotations
import json
import re
from pathlib import Path

original = Path("article.md").read_text(encoding="utf-8")

# Each entry: (pattern regex, rewrite_fn, category, description)
REPLACEMENTS = [
    # "it's important to note that X" -> "X"
    (
        re.compile(r"[Ii]t'?s important to note that\s+", re.IGNORECASE),
        lambda m: "",
        "filler-hedge",
        "it's important to note that",
    ),
    (
        re.compile(r"[Ii]t'?s important to note[,]?\s+", re.IGNORECASE),
        lambda m: "",
        "filler-hedge",
        "it's important to note",
    ),
    # "it's worth noting that" / "it is worth noting that"
    (
        re.compile(r"[Ii]t'?s worth noting that\s+", re.IGNORECASE),
        lambda m: "",
        "filler-hedge",
        "it's worth noting that",
    ),
    (
        re.compile(r"[Ii]t is worth noting that\s+", re.IGNORECASE),
        lambda m: "",
        "filler-hedge",
        "it is worth noting that",
    ),
    (
        re.compile(r"[Ii]t'?s worth noting[,]?\s+", re.IGNORECASE),
        lambda m: "",
        "filler-hedge",
        "it's worth noting",
    ),
    # "Additionally,"
    (
        re.compile(r"\bAdditionally,\s+", re.IGNORECASE),
        lambda m: "",
        "chatgpt-transition",
        "Additionally,",
    ),
    # "Furthermore,"
    (
        re.compile(r"\bFurthermore,\s+", re.IGNORECASE),
        lambda m: "",
        "chatgpt-transition",
        "Furthermore,",
    ),
    # "Moreover,"
    (
        re.compile(r"\bMoreover,\s+", re.IGNORECASE),
        lambda m: "",
        "chatgpt-transition",
        "Moreover,",
    ),
    # "In addition to" -> keep the rest, just drop the phrase
    (
        re.compile(r"\bIn addition to\b", re.IGNORECASE),
        lambda m: "Beyond",
        "chatgpt-transition",
        "In addition to",
    ),
    # "It is crucial to understand that"
    (
        re.compile(r"[Ii]t is crucial to understand that\s+", re.IGNORECASE),
        lambda m: "",
        "filler-hedge",
        "It is crucial to understand that",
    ),
    # "It goes without saying that"
    (
        re.compile(r"[Ii]t goes without saying that\s+", re.IGNORECASE),
        lambda m: "",
        "filler-cliche",
        "It goes without saying that",
    ),
    # "in order to" -> "to"
    (
        re.compile(r"\bin order to\b", re.IGNORECASE),
        lambda m: "to",
        "verbose-phrase",
        "in order to",
    ),
    # "due to the fact that" -> "because"
    (
        re.compile(r"\bdue to the fact that\b", re.IGNORECASE),
        lambda m: "because",
        "verbose-phrase",
        "due to the fact that",
    ),
]

changes = []
text = original
categories_hit: dict[str, int] = {}

for pattern, rewrite_fn, category, phrase_label in REPLACEMENTS:
    matches = list(pattern.finditer(text))
    for m in matches:
        # Record the surrounding sentence for context
        start = max(0, m.start() - 80)
        end = min(len(text), m.end() + 80)
        context = text[start:end].replace("\n", " ").strip()
        replacement = rewrite_fn(m)
        changes.append({
            "phrase": phrase_label,
            "category": category,
            "context": context,
            "replacement": replacement if replacement else "(removed)",
        })
        categories_hit[category] = categories_hit.get(category, 0) + 1
    text = pattern.sub(rewrite_fn, text)

# Fix capitalization: after removal the first char of continuing word should be uppercased
# if it starts a sentence (preceded by ". " or start of line)
# Simple heuristic: fix double-spaces and obvious lowercase after period
text = re.sub(r"  +", " ", text)
text = re.sub(r"\. ([a-z])", lambda m: ". " + m.group(1).upper(), text)
# Fix lines that start with lowercase after removal
lines = text.split("\n")
fixed_lines = []
for line in lines:
    stripped = line.lstrip()
    if stripped and stripped[0].islower() and not stripped.startswith("http"):
        # Capitalize the first word of the line
        idx = len(line) - len(stripped)
        line = line[:idx] + stripped[0].upper() + stripped[1:]
    fixed_lines.append(line)
text = "\n".join(fixed_lines)

Path("clean.md").write_text(text, encoding="utf-8")

report = {
    "total_removed": len(changes),
    "counts_by_category": categories_hit,
    "changes": changes,
}
Path("changes.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

print(f"Written clean.md and changes.json")
print(f"  Total changes: {len(changes)}")
print(f"  By category: {categories_hit}")

# Verify none of the banned phrases remain
import re as _re
remaining = []
check_phrases = [
    "it's important to note",
    "it is important to note",
    "it's worth noting",
    "it is worth noting",
    "additionally,",
    "furthermore,",
    "moreover,",
    "it is crucial to understand",
    "it goes without saying",
    "in order to",
    "due to the fact that",
]
for p in check_phrases:
    if p.lower() in text.lower():
        remaining.append(p)
if remaining:
    print(f"WARNING: phrases still present in clean.md: {remaining}")
else:
    print("  All banned phrases removed from clean.md")

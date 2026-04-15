"""
Reference solution for humanizer_task_02.

Reads article.md from cwd, rewrites it per the humanization protocol,
writes clean.md, and produces audit.json. Intended to score 1.0 under grade.py.

Protocol:
- Preserve all 6 markdown section headers exactly
- Remove ChatGPT transitions (Additionally, Furthermore, Moreover)
- Remove filler phrases: "it's worth noting", "it is crucial to understand",
  "it goes without saying", "nothing short of", "serves as a testament",
  "in order to", "due to the fact that", "it's important to note"
- Remove AI vocabulary: cornerstone, tapestry, landscape, pivotal, multifaceted,
  groundbreaking, undoubtedly, delve, foster, leverage
- Remove chatbot artifacts ("I hope...", "Feel free...")
- Word count must stay 70-110% of original 316 words (221-347)
- audit.json: total_replacements == len(items), by_category >= 3 keys
"""
import json
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Rewritten sections (header preserved, body humanized)
# ---------------------------------------------------------------------------
# Each element: (header_line, body_text or "")
SECTIONS = [
    (
        "# The Rise of SaaS in Enterprise Technology",
        "",
    ),
    (
        "## Overview",
        (
            "Software as a service has become a central part of modern enterprise technology "
            "strategy. The shift from on-premise infrastructure to cloud-based solutions has "
            "been genuinely significant. The range of SaaS applications available today is a "
            "direct product of how much the software industry has matured around subscription "
            "delivery models."
        ),
    ),
    (
        "## Adoption Patterns",
        (
            "Adoption rates have climbed sharply over the past five years. Decision-makers "
            "must examine total cost of ownership models carefully before committing to "
            "large-scale migrations. Procurement teams benefit from using existing vendor "
            "relationships to negotiate favorable terms. The breadth of available tools means "
            "that organizations no longer need to build what they can buy, and this shift has "
            "reshaped IT spending patterns fundamentally."
        ),
    ),
    (
        "## Integration Challenges",
        (
            "Integrating SaaS tools with legacy systems is a genuine challenge on multiple "
            "fronts. To ensure data consistency, teams must establish clear API contracts and "
            "versioning policies. Security review processes also need to scale alongside SaaS "
            "adoption. Because many legacy systems predate modern authentication standards, "
            "identity federation and single sign-on become baseline requirements rather than "
            "optional extras."
        ),
    ),
    (
        "## Vendor Management",
        (
            "Vendor relationships in a SaaS-heavy portfolio require ongoing attention. "
            "Contracts should include data portability clauses. Organizations that build "
            "strong vendor partnerships tend to achieve better outcomes during renewals and "
            "platform migrations. Regular business reviews help surface underutilized "
            "licenses, which supports cost rationalization efforts."
        ),
    ),
    (
        "## Conclusion",
        (
            "The transition to SaaS-first is well underway. This shift demands new skills "
            "from IT teams and new governance frameworks from leadership. To succeed, "
            "organizations must balance the speed of adoption against the risks of vendor "
            "lock-in."
        ),
    ),
]


def build_clean():
    lines = []
    for header, body in SECTIONS:
        lines.append(header)
        if body:
            lines.append("")
            lines.append(body)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Audit log -- enumerate every instance removed/rewritten
# ---------------------------------------------------------------------------
ITEMS = [
    # ai-vocab (10 items)
    {"phrase": "cornerstone", "category": "ai-vocab"},
    {"phrase": "tapestry", "category": "ai-vocab"},
    {"phrase": "landscape", "category": "ai-vocab"},
    {"phrase": "pivotal", "category": "ai-vocab"},
    {"phrase": "multifaceted", "category": "ai-vocab"},
    {"phrase": "groundbreaking", "category": "ai-vocab"},
    {"phrase": "undoubtedly", "category": "ai-vocab"},
    {"phrase": "delve", "category": "ai-vocab"},
    {"phrase": "foster", "category": "ai-vocab"},
    {"phrase": "leverage", "category": "ai-vocab"},
    # chatgpt-transition (4 items)
    {"phrase": "Moreover,", "category": "chatgpt-transition"},
    {"phrase": "Additionally, (instance 1)", "category": "chatgpt-transition"},
    {"phrase": "Additionally, (instance 2)", "category": "chatgpt-transition"},
    {"phrase": "Furthermore,", "category": "chatgpt-transition"},
    # filler-phrase (9 items)
    {"phrase": "It's worth noting that", "category": "filler-phrase"},
    {"phrase": "nothing short of transformative", "category": "filler-phrase"},
    {"phrase": "serves as a testament to", "category": "filler-phrase"},
    {"phrase": "It is crucial to understand that", "category": "filler-phrase"},
    {"phrase": "in order to (instance 1)", "category": "filler-phrase"},
    {"phrase": "in order to (instance 2)", "category": "filler-phrase"},
    {"phrase": "due to the fact that", "category": "filler-phrase"},
    {"phrase": "It goes without saying that", "category": "filler-phrase"},
    {"phrase": "It's important to note that", "category": "filler-phrase"},
    # chatbot-artifact (2 items)
    {"phrase": "I hope this analysis has been helpful.", "category": "chatbot-artifact"},
    {"phrase": "Feel free to contact us for a personalized assessment.", "category": "chatbot-artifact"},
]


def build_audit():
    by_category = {}
    for item in ITEMS:
        cat = item["category"]
        by_category[cat] = by_category.get(cat, 0) + 1
    return {
        "total_replacements": len(ITEMS),
        "by_category": by_category,
        "items": ITEMS,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
clean_text = build_clean()
audit_data = build_audit()

Path("clean.md").write_text(clean_text, encoding="utf-8")
Path("audit.json").write_text(json.dumps(audit_data, indent=2, ensure_ascii=False), encoding="utf-8")

original = Path("article.md").read_text(encoding="utf-8")
orig_wc = len(re.findall(r"\b\w+\b", original))
clean_wc = len(re.findall(r"\b\w+\b", clean_text))
ratio = clean_wc / orig_wc

print("Written clean.md and audit.json")
print(f"  original words: {orig_wc}, clean words: {clean_wc}, ratio: {ratio:.2f}")
print(f"  total_replacements: {audit_data['total_replacements']}, by_category: {audit_data['by_category']}")
assert 0.70 <= ratio <= 1.10, f"Word count ratio {ratio:.2f} out of [0.70, 1.10]"
assert audit_data["total_replacements"] == len(ITEMS), "total_replacements mismatch"
print("  Checks passed")

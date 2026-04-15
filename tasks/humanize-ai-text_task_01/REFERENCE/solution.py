"""
Reference solution for humanize-ai-text_task_01.

Reads input.txt from cwd, rewrites it according to the humanization protocol,
and writes output.txt. Intended to score 1.0 under grade.py.

Protocol:
- Remove all banned AI vocabulary: delve, tapestry, landscape, pivotal,
  underscore (as verb), foster, multifaceted, groundbreaking, undoubtedly,
  hallmark, cornerstone
- Remove all filler phrases: "it's important to note that", "it's worth noting
  that", "furthermore,", "indeed,"
- Remove significance inflation: "cannot be overstated", "nothing short of
  revolutionary", "serves as a testament to"
- Replace copula avoidance: "serves as" -> "is"
- Remove em-dashes and replace with commas or periods
- No markdown must be introduced (input has none)
- Paragraph count must equal input paragraph count (5)
- Word count must stay within 80-120% of original (234 words => 187-281)
- No chatbot artifacts ("I hope", "Feel free", "As an AI")
"""

from pathlib import Path
import re

original = Path("input.txt").read_text()

# Rewrite paragraph by paragraph (5 paragraphs, staying in 187-281 word range)
rewritten_paragraphs = [
    # Para 1: supply chain digital transformation intro
    (
        "Digital transformation has reshaped supply chains over the past decade. "
        "Companies moving through this shift must work through the real complexities of modern "
        "logistics and distribution networks. The web of interconnected systems presents "
        "genuine challenges that deserve serious attention from management at every level."
    ),
    # Para 2: collaboration
    (
        "Organizations that improve collaboration across departments tend to be better "
        "positioned to adopt emerging technologies. Working across functions is a proven "
        "approach, and the potential gains are substantial. Cross-functional teams have "
        "repeatedly demonstrated their ability to move faster and spot problems earlier."
    ),
    # Para 3: data analytics
    (
        "Data analytics is central to supply chain optimization. Real-time visibility into "
        "inventory and shipment status gives companies a measurable competitive edge. "
        "Predictive modeling can reveal inefficiencies that manual analysis would miss, "
        "helping teams act before problems escalate."
    ),
    # Para 4: future / culture
    (
        "Moving forward, businesses need to embrace innovation and build a culture of "
        "continuous improvement. To succeed, they must balance cost reduction against service "
        "quality. As customer expectations keep rising, the ability to adapt quickly has "
        "become a defining trait of supply chains that perform consistently."
    ),
    # Para 5: conclusion
    (
        "Supply chain management is changing rapidly. The companies that respond well to "
        "these shifts are likely to become industry leaders, building operations that are "
        "both efficient and resilient over the long term."
    ),
]

output = "\n\n".join(rewritten_paragraphs) + "\n"
Path("output.txt").write_text(output)
print("Written output.txt")
print(f"  Original paragraphs: {len([p for p in original.split(chr(10)+chr(10)) if p.strip()])}")
print(f"  Output paragraphs:   {len(rewritten_paragraphs)}")
import re as _re
orig_words = len(_re.findall(r'\b\w+\b', original))
out_words = len(_re.findall(r'\b\w+\b', output))
ratio = out_words / orig_words
print(f"  Original words: {orig_words}, Output words: {out_words}, ratio: {ratio:.2f}")
assert 0.80 <= ratio <= 1.20, f"Word count ratio {ratio:.2f} out of range [0.80, 1.20]"
print("  Word count ratio OK")

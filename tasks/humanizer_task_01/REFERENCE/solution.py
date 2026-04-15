"""
Reference solution for humanizer_task_01.

Reads draft.txt from cwd, rewrites it according to the humanization protocol,
and writes output.txt. Intended to score 1.0 under grade.py.

Protocol:
- Replace all curly/smart quotes with straight ASCII equivalents
- Remove all "Not only...but also" negative parallelisms (rewrite as direct statements)
- Remove banned AI vocabulary: groundbreaking, landscape, delving/delve, pivotal,
  multifaceted, undoubtedly, hallmark, cornerstone, foster/fostering, leverage
- Remove filler phrases: "it's important to note" (curly-apostrophe variant), "furthermore,",
  "in order to", "due to the fact that", "cannot be overstated", "nothing short of"
- Remove chatbot artifacts: "I hope this overview has been helpful. Feel free to reach out
  if you have additional questions."
- Replace copula-avoidance: "serve as a testament to" -> "demonstrate", "boast" -> "have"
- Paragraph count must remain 4 (double-newline separated)
- Word count must stay within 80-120% of original 260 words (208-312)
"""
from pathlib import Path
import re

rewritten_paragraphs = [
    # Para 1: intro — remove "Not only...but also", remove groundbreaking, landscape,
    # delving, cannot be overstated, nothing short of revolutionary
    (
        "Telemedicine has fundamentally changed how patients access care and is reshaping the "
        "doctor-patient relationship in meaningful ways. Healthcare providers are exploring "
        "new models that use digital platforms to deliver services once confined to physical "
        "clinics. Modern medicine is changing rapidly, and many health systems are already "
        "well into that transition."
    ),
    # Para 2: remote monitoring — remove "serve as a testament", "boast", "fostering",
    # "pivotal", "undoubtedly", curly apostrophe filler phrase
    (
        "Remote monitoring devices demonstrate the value of patient-centered design. These "
        "tools have sophisticated sensors that track vital signs around the clock, enabling "
        "a new era of preventive care. Clinicians who make this transition will find "
        "themselves better equipped to serve diverse patient populations. Data privacy "
        "remains a serious concern that must be addressed before widespread adoption can "
        "move forward."
    ),
    # Para 3: AI diagnostics — remove "multifaceted", "Furthermore,", "in order to",
    # curly quotes around quote, curly apostrophe, "due to the fact that"
    (
        "Integrating AI diagnostics into clinical workflows is a genuine challenge. To ensure "
        "equitable access, healthcare systems must invest in broadband infrastructure across "
        "rural communities. \"Patients deserve the same quality of care regardless of "
        "geography,\" said the report's lead author. Because reimbursement models have not "
        "kept pace with technology, many providers remain hesitant to adopt remote-first "
        "approaches."
    ),
    # Para 4: evidence — remove second "Not only...but also", remove "Groundbreaking",
    # "underscore", "hallmark", chatbot artifacts ("I hope... Feel free...")
    (
        "The evidence supports improved outcomes for chronic disease management and "
        "highlights the cost savings achievable through early intervention. Studies from "
        "three continents identify the common traits of successful telehealth programs: "
        "accessibility, continuity, and solid integration with existing care delivery systems."
    ),
]

output = "\n\n".join(rewritten_paragraphs) + "\n"
Path("output.txt").write_text(output, encoding="utf-8")
print("Written output.txt")

import re as _re

original = Path("draft.txt").read_text(encoding="utf-8")
orig_words = len(_re.findall(r'\b\w+\b', original))
out_words = len(_re.findall(r'\b\w+\b', output))
ratio = out_words / orig_words
orig_paras = len([p for p in original.split("\n\n") if p.strip()])
out_paras = len([p for p in output.split("\n\n") if p.strip()])

print(f"  Original words: {orig_words}, Output words: {out_words}, ratio: {ratio:.2f}")
print(f"  Original paras: {orig_paras}, Output paras: {out_paras}")
assert 0.80 <= ratio <= 1.20, f"Word count ratio {ratio:.2f} out of range"
assert out_paras == 4, f"Para count {out_paras} != 4"
print("  Checks passed")

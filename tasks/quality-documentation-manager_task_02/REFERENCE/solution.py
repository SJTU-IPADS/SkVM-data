"""
Reference solution for quality-documentation-manager_task_02.

Reads change_request.json from the workspace, classifies each proposed change,
determines the new revision designation, and writes change_assessment.json.

Classification rules per the document control procedure:
  Administrative: no content impact (typos, formatting, branding) → Document Control approval
  Minor:          limited content change (clarifications, no new requirements) → Process Owner + QA
  Major:          significant content change (new requirements, process changes) → Full review cycle

Revision designation rule (highest classification wins):
  Major → increment number (02 → 03)
  Minor → sub-revision (02 → 02.1)
  Administrative → letter suffix (02 → 02a)
"""
import json
from pathlib import Path

workspace = Path(".")
cr = json.loads((workspace / "change_request.json").read_text())

# Classification logic (hardcoded for this deterministic fixture)
# Change X: Corporate logo update — Administrative (no content impact)
# Change Y: Clarifying note on investigation timelines — Minor (resolves ambiguity, limited content)
# Change Z: Typo corrections — Administrative (no content impact)
CLASSIFICATIONS = {
    "X": {
        "classification": "Administrative",
        "requires_training": False,
        "approval_level": "Document Control",
        "justification": (
            "Updating the corporate logo in the document header is a branding/formatting change "
            "with no impact on procedural content, requirements, or instructions."
        ),
    },
    "Y": {
        "classification": "Minor",
        "requires_training": False,
        "approval_level": "Process Owner + QA",
        "justification": (
            "Adding a clarifying note to resolve audit finding IA-2024-07 is a limited content "
            "change that removes ambiguity about existing timelines. It does not introduce new "
            "mandatory requirements or alter the procedure's scope — qualifying as Minor, not Major."
        ),
    },
    "Z": {
        "classification": "Administrative",
        "requires_training": False,
        "approval_level": "Document Control",
        "justification": (
            "Correcting three spelling errors (occured, analysed, personnell) has no impact on "
            "the meaning or requirements of the procedure — purely typographical corrections."
        ),
    },
}

# Determine highest classification
CLASS_RANK = {"Administrative": 0, "Minor": 1, "Major": 2}
highest_class = max(
    (CLASSIFICATIONS[cid]["classification"] for cid in CLASSIFICATIONS),
    key=lambda c: CLASS_RANK[c]
)

# Build new revision per hierarchy
current_rev = cr["current_revision"]  # "02"
if highest_class == "Major":
    new_rev = str(int(current_rev) + 1).zfill(2)  # "03"
elif highest_class == "Minor":
    new_rev = f"{current_rev}.1"  # "02.1"
else:
    new_rev = f"{current_rev}a"   # "02a"

# Build change entries
changes_out = []
for prop_change in cr["proposed_changes"]:
    cid = prop_change["change_id"]
    cls_info = CLASSIFICATIONS[cid]
    changes_out.append({
        "change_id": cid,
        "description": prop_change["description"],
        "section_affected": prop_change["section_affected"],
        "classification": cls_info["classification"],
        "justification": cls_info["justification"],
        "requires_training": cls_info["requires_training"],
        "approval_level": cls_info["approval_level"],
    })

# Build updated change history (preserve existing + add new entry)
history = list(cr["change_history_existing"])  # revisions 01, 02
history.append({
    "revision": new_rev,
    "date": cr["target_effective_date"],
    "description": (
        "Logo update (header); added clarifying note to section 4.3 regarding "
        "investigation timelines for customer complaints vs. internal nonconformances; "
        "corrected typographical errors in sections 2.1, 5.2, 6.1"
    ),
    "author": cr["requested_by"],
    "approver": "D. Simmons",
})

assessment = {
    "change_request_id": cr["change_request_id"],
    "document_number": cr["document_number"],
    "document_title": cr["document_title"],
    "current_revision": current_rev,
    "highest_classification": highest_class,
    "new_revision": new_rev,
    "changes": changes_out,
    "change_history": history,
}

(workspace / "change_assessment.json").write_text(json.dumps(assessment, indent=2))

print("Done.")
print(f"  highest_classification: {highest_class}")
print(f"  new_revision: {new_rev}")
print(f"  change_history entries: {len(history)}")
for h in history:
    print(f"    rev {h['revision']} ({h['date']}): {h['description'][:60]}...")

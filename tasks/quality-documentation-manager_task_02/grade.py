"""
Grade function for quality-documentation-manager_task_02.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: parse change_assessment.json from the workspace and verify:
  - Each change is classified correctly (Administrative / Minor / Administrative)
  - Requires-training and approval level match the classification
  - New revision designation follows the hierarchy rule (highest classification wins)
  - The new revision for Minor change = sub-revision (02.1), NOT a major increment (03)
  - Change history is complete, chronological, and contains the new entry
  - New history entry has all required fields

The common-default-wrong trap: models tend to increment the major revision number
for any change, producing "03" instead of the correct "02.1" for a Minor-only change.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


# ---- Expected values --------------------------------------------------------
# Change X: Administrative (logo/branding, no content impact)
# Change Y: Minor (clarifying note, limited content change)
# Change Z: Administrative (typos, no content impact)
# Highest classification = Minor → new revision = "02.1"
# All existing history entries must be preserved (rev 01, rev 02)
# New history entry must have revision "02.1", correct date, author, approver, description

EXPECTED_CLASSIFICATIONS = {
    "X": "Administrative",
    "Y": "Minor",
    "Z": "Administrative",
}

EXPECTED_TRAINING = {
    "X": False,
    "Y": False,
    "Z": False,
}

EXPECTED_APPROVAL_LEVEL = {
    "Administrative": "Document Control",
    "Minor": "Process Owner + QA",
    "Major": "Full review cycle",
}

EXPECTED_NEW_REVISION = "02.1"
EXPECTED_EXISTING_REVISIONS = {"01", "02"}
TARGET_EFFECTIVE_DATE = "2025-04-15"

NUMBER_RE = re.compile(r'^\d+\.\d+$|^\d+$')


# ---- Helpers ----------------------------------------------------------------

def _load_assessment(workspace_path: str):
    path = Path(workspace_path) / "change_assessment.json"
    if not path.exists():
        return None, "change_assessment.json not found in workspace"
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"change_assessment.json is not valid JSON: {e}"


def _get_changes_by_id(assessment) -> dict:
    if assessment is None:
        return {}
    changes = assessment.get("changes") or []
    return {str(c.get("change_id", "")).upper(): c for c in changes}


def _get_history(assessment) -> list:
    if assessment is None:
        return []
    return assessment.get("change_history") or []


# ---- Per-criterion checks ---------------------------------------------------

def _check_file_exists(assessment, _):
    if assessment is None:
        return 0.0, "change_assessment.json missing or unparseable"
    return 1.0, None


def _check_change_count(assessment, _):
    if assessment is None:
        return 0.0, "change_assessment.json missing"
    changes = assessment.get("changes") or []
    if len(changes) < 3:
        return 0.0, f"expected 3 change entries (X, Y, Z), found {len(changes)}"
    return 1.0, None


def _check_classifications(assessment, _):
    """Change X and Z are Administrative; Change Y is Minor — not Major."""
    if assessment is None:
        return 0.0, "change_assessment.json missing"
    by_id = _get_changes_by_id(assessment)
    wrong = []
    for cid, expected_class in EXPECTED_CLASSIFICATIONS.items():
        item = by_id.get(cid)
        if item is None:
            wrong.append(f"Change {cid}: not found in assessment")
            continue
        got = str(item.get("classification", "")).strip()
        if got != expected_class:
            wrong.append(f"Change {cid}: expected '{expected_class}', got '{got}'")
    if wrong:
        return 0.0, "; ".join(wrong)
    return 1.0, None


def _check_change_y_minor_not_major(assessment, _):
    """Change Y (clarifying note, limited content change) is Minor, not Major.
    Classifying a clarification as Major is the most common error — it overestimates
    the impact of a note that does not add new requirements."""
    if assessment is None:
        return 0.0, "change_assessment.json missing"
    by_id = _get_changes_by_id(assessment)
    item = by_id.get("Y")
    if item is None:
        return 0.0, "Change Y not found in assessment"
    got = str(item.get("classification", "")).strip()
    if got == "Major":
        return 0.0, (
            "Change Y (section 4.3 clarifying note) is classified as Major, but it is Minor: "
            "it clarifies existing intent without adding new mandatory requirements. "
            "Major classification would trigger a full review cycle and a full revision increment."
        )
    if got != "Minor":
        return 0.0, f"Change Y: expected 'Minor', got '{got!r}'"
    return 1.0, None


def _check_training_flags(assessment, _):
    """Training is not required for Administrative or Minor clarification changes in this batch."""
    if assessment is None:
        return 0.0, "change_assessment.json missing"
    by_id = _get_changes_by_id(assessment)
    wrong = []
    for cid, exp_training in EXPECTED_TRAINING.items():
        item = by_id.get(cid)
        if item is None:
            continue
        got = item.get("requires_training")
        # Accept bool or string "false"/"true"
        if isinstance(got, str):
            got = got.lower() == "true"
        if bool(got) != exp_training:
            wrong.append(f"Change {cid}: requires_training expected {exp_training}, got {got!r}")
    if wrong:
        return 0.0, "; ".join(wrong)
    return 1.0, None


def _check_approval_levels(assessment, _):
    """Approval levels must match the classification: Administrative→Document Control, Minor→Process Owner + QA."""
    if assessment is None:
        return 0.0, "change_assessment.json missing"
    by_id = _get_changes_by_id(assessment)
    wrong = []
    for cid, exp_class in EXPECTED_CLASSIFICATIONS.items():
        item = by_id.get(cid)
        if item is None:
            continue
        exp_approval = EXPECTED_APPROVAL_LEVEL[exp_class]
        got_approval = str(item.get("approval_level", "")).strip()
        # Case-insensitive match, allow reasonable synonyms
        if not got_approval:
            wrong.append(f"Change {cid}: approval_level is empty")
        elif exp_approval.lower() not in got_approval.lower() and got_approval.lower() not in exp_approval.lower():
            wrong.append(f"Change {cid}: expected approval_level '{exp_approval}', got '{got_approval}'")
    if wrong:
        return 0.0, "; ".join(wrong)
    return 1.0, None


def _check_new_revision(assessment, _):
    """New revision must be '02.1' — the sub-revision form for a Minor change at current revision 02.
    The most common default-wrong is to produce '03' (treating Minor as if it were Major)."""
    if assessment is None:
        return 0.0, "change_assessment.json missing"
    got = str(assessment.get("new_revision", "")).strip()
    if not got:
        return 0.0, "new_revision field is missing or empty"
    if got == "03":
        return 0.0, (
            "new_revision is '03', which is the Major-change increment. "
            "The highest classification in this batch is Minor, which uses "
            "the sub-revision format: '02.1'. A full increment to '03' would "
            "require at least one Major change."
        )
    if got != EXPECTED_NEW_REVISION:
        return 0.0, f"expected new_revision '02.1', got '{got}'"
    return 1.0, None


def _check_highest_classification(assessment, _):
    """The assessment must identify Minor as the highest classification driving the revision designation."""
    if assessment is None:
        return 0.0, "change_assessment.json missing"
    field = str(assessment.get("highest_classification", "")).strip()
    if not field:
        # Try to infer from new_revision
        new_rev = str(assessment.get("new_revision", "")).strip()
        if new_rev == EXPECTED_NEW_REVISION:
            return 1.0, None
        return 0.0, "highest_classification field missing and new_revision does not reflect Minor designation"
    if field != "Minor":
        return 0.0, f"highest_classification should be 'Minor' (changes X and Z are Administrative; Y is Minor), got '{field}'"
    return 1.0, None


def _check_history_complete(assessment, _):
    """change_history must preserve ALL existing entries (revisions 01 and 02) plus the new 02.1 entry — total 3 entries minimum."""
    if assessment is None:
        return 0.0, "change_assessment.json missing"
    history = _get_history(assessment)
    revisions = {str(h.get("revision", "")) for h in history}
    missing = EXPECTED_EXISTING_REVISIONS - revisions
    if missing:
        return 0.0, f"change_history missing existing revisions: {sorted(missing)}. History must include all prior entries."
    if len(history) < 3:
        return 0.0, f"change_history has only {len(history)} entries; expected at least 3 (01, 02, and new 02.1)"
    return 1.0, None


def _check_history_chronological(assessment, _):
    """change_history entries must be sorted in ascending date order — earlier revisions come first."""
    if assessment is None:
        return 0.0, "change_assessment.json missing"
    history = _get_history(assessment)
    dates = [str(h.get("date", "")) for h in history]
    # Check dates are parseable ISO strings in order
    import datetime
    parsed = []
    for d in dates:
        try:
            parsed.append(datetime.date.fromisoformat(d))
        except ValueError:
            return 0.0, f"non-ISO date in change_history: '{d}'"
    for i in range(1, len(parsed)):
        if parsed[i] < parsed[i - 1]:
            return 0.0, (
                f"change_history is not in ascending date order: "
                f"entry {i} date {dates[i]} is before entry {i-1} date {dates[i-1]}"
            )
    return 1.0, None


def _check_new_history_entry(assessment, _):
    """The new change_history entry for revision 02.1 must include revision, date, description, author, and approver fields."""
    if assessment is None:
        return 0.0, "change_assessment.json missing"
    history = _get_history(assessment)
    new_entry = None
    for h in history:
        if str(h.get("revision", "")).strip() == EXPECTED_NEW_REVISION:
            new_entry = h
            break
    if new_entry is None:
        return 0.0, f"no change_history entry with revision '{EXPECTED_NEW_REVISION}' found"
    required_fields = {"revision", "date", "description", "author", "approver"}
    missing = required_fields - set(new_entry.keys())
    if missing:
        return 0.0, f"new history entry (revision {EXPECTED_NEW_REVISION}) missing fields: {sorted(missing)}"
    # Check date is plausible (after current_effective_date 2023-04-10)
    import datetime
    try:
        entry_date = datetime.date.fromisoformat(str(new_entry.get("date", "")))
        baseline = datetime.date(2023, 4, 10)
        if entry_date <= baseline:
            return 0.0, f"new history entry date {entry_date} is not after current effective date 2023-04-10"
    except ValueError:
        return 0.0, f"new history entry date is not a valid ISO date: {new_entry.get('date')!r}"
    return 1.0, None


def _check_document_number_present(assessment, _):
    """change_assessment.json must record the document number SOP-08-002 and current_revision 02."""
    if assessment is None:
        return 0.0, "change_assessment.json missing"
    doc_num = str(assessment.get("document_number", "")).strip()
    cur_rev = str(assessment.get("current_revision", "")).strip()
    wrong = []
    if doc_num != "SOP-08-002":
        wrong.append(f"document_number: expected 'SOP-08-002', got '{doc_num}'")
    if cur_rev != "02":
        wrong.append(f"current_revision: expected '02', got '{cur_rev}'")
    if wrong:
        return 0.0, "; ".join(wrong)
    return 1.0, None


# ---- Criterion registry -----------------------------------------------------

CRITERIA = [
    {
        "id": "file-exists",
        "weight": 0.04,
        "description": "change_assessment.json exists at the workspace root and parses as valid JSON.",
        "check": _check_file_exists,
    },
    {
        "id": "change-count",
        "weight": 0.03,
        "description": "change_assessment.json contains assessment entries for all three proposed changes (X, Y, Z).",
        "check": _check_change_count,
    },
    {
        "id": "classifications",
        "weight": 0.20,
        "description": "Changes X and Z are classified as Administrative (logo update and typo corrections — no content impact) and Change Y is classified as Minor (clarifying note, limited content change). Misclassifying any change shifts the revision designation.",
        "check": _check_classifications,
    },
    {
        "id": "change-y-not-major",
        "weight": 0.15,
        "description": "Change Y (clarifying note in section 4.3) is Minor, not Major. A clarification that resolves ambiguity without adding new mandatory requirements is Minor. Classifying it as Major is the most common error and would incorrectly trigger a full revision increment.",
        "check": _check_change_y_minor_not_major,
    },
    {
        "id": "training-flags",
        "weight": 0.06,
        "description": "requires_training is false for all three changes: Administrative changes never require retraining, and this Minor clarification does not introduce new steps or equipment — it only removes ambiguity about an existing timeline.",
        "check": _check_training_flags,
    },
    {
        "id": "approval-levels",
        "weight": 0.08,
        "description": "Approval levels match each classification: Administrative changes require Document Control only; the Minor change (Y) requires Process Owner + QA; no change in this batch warrants a Full review cycle.",
        "check": _check_approval_levels,
    },
    {
        "id": "new-revision",
        "weight": 0.18,
        "description": "new_revision must be '02.1' — the sub-revision form used when the highest classification is Minor. A full increment to '03' is only correct when at least one change is Major. This is the primary trap: models default to incrementing the major number for all changes.",
        "check": _check_new_revision,
    },
    {
        "id": "highest-classification",
        "weight": 0.06,
        "description": "The assessment must indicate that Minor is the highest classification driving the revision designation, reflecting the hierarchy Major > Minor > Administrative.",
        "check": _check_highest_classification,
    },
    {
        "id": "history-complete",
        "weight": 0.10,
        "description": "change_history must contain all prior revision entries (01 and 02) plus the new 02.1 entry — a minimum of 3 entries. Omitting earlier entries destroys the audit trail required by document control procedures.",
        "check": _check_history_complete,
    },
    {
        "id": "history-chronological",
        "weight": 0.05,
        "description": "change_history entries must be ordered by date ascending — earlier revisions come first. Out-of-order entries make the audit trail unreadable and non-compliant.",
        "check": _check_history_chronological,
    },
    {
        "id": "new-history-entry",
        "weight": 0.04,
        "description": "The new change_history entry for revision 02.1 must contain all five required fields: revision, date, description, author, and approver. The date must be after the current effective date (2023-04-10).",
        "check": _check_new_history_entry,
    },
    {
        "id": "document-number-present",
        "weight": 0.01,
        "description": "change_assessment.json records document_number 'SOP-08-002' and current_revision '02', confirming the assessment is linked to the correct document version.",
        "check": _check_document_number_present,
    },
]

# Sanity check at import time.
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    assessment, _ = _load_assessment(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](assessment, None)
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

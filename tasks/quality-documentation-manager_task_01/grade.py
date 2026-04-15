"""
Grade function for quality-documentation-manager_task_01.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: parse assigned_numbers.json from the workspace and verify:
  - Document number format (PREFIX-CC-NNN)
  - Correct category code per functional area
  - Correct sequence continuation from the existing master list
  - No duplicates in the combined master list
  - Updated master list JSON with all 7 new documents merged in

Expected assignments are hardcoded from the deterministic fixture.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path


# ---- Expected assignments from deterministic fixture -------------------------
# Format: request_id -> {number, category_code, doc_type}
EXPECTED = {
    "REQ-001": {"number": "SOP-07-001", "category_code": "07", "doc_type": "SOP"},
    "REQ-002": {"number": "SOP-05-003", "category_code": "05", "doc_type": "SOP"},
    "REQ-003": {"number": "WI-06-002",  "category_code": "06", "doc_type": "WI"},
    "REQ-004": {"number": "TF-07-001",  "category_code": "07", "doc_type": "TF"},
    "REQ-005": {"number": "SPEC-04-003","category_code": "04", "doc_type": "SPEC"},
    "REQ-006": {"number": "PLN-09-001", "category_code": "09", "doc_type": "PLN"},
    "REQ-007": {"number": "WI-07-001",  "category_code": "07", "doc_type": "WI"},
}

# Existing master list numbers (from fixture); these must still be present in
# the updated master list and must not be re-used as new numbers.
EXISTING_NUMBERS = {
    "SOP-02-001", "SOP-05-001", "SOP-05-002",
    "WI-06-001",
    "TF-08-001",
    "SPEC-04-001", "SPEC-04-002",
    "PLN-01-001",
}

NUMBER_RE = re.compile(r'^([A-Z]+)-(\d{2})-(\d{3})$')


# ---- Helpers -----------------------------------------------------------------

def _load_assigned(workspace_path: str):
    path = Path(workspace_path) / "assigned_numbers.json"
    if not path.exists():
        return None, "assigned_numbers.json not found in workspace"
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"assigned_numbers.json is not valid JSON: {e}"


def _load_updated_master(workspace_path: str):
    path = Path(workspace_path) / "updated_master_list.json"
    if not path.exists():
        return None, "updated_master_list.json not found in workspace"
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"updated_master_list.json is not valid JSON: {e}"


def _get_assignments(assigned) -> dict:
    """Return dict request_id -> assignment record."""
    if assigned is None:
        return {}
    items = assigned.get("assignments") or assigned.get("documents") or []
    result = {}
    for item in items:
        rid = item.get("request_id") or item.get("id")
        if rid:
            result[rid] = item
    return result


# ---- Per-criterion checks ---------------------------------------------------

def _check_assigned_exists(assigned, updated_master):
    if assigned is None:
        return 0.0, "assigned_numbers.json missing or unparseable"
    items = assigned.get("assignments") or assigned.get("documents") or []
    if len(items) < 7:
        return 0.0, f"expected 7 assignment entries, found {len(items)}"
    return 1.0, None


def _check_number_format(assigned, updated_master):
    """Every assigned number must match PREFIX-CC-NNN exactly."""
    if assigned is None:
        return 0.0, "assigned_numbers.json missing"
    items = assigned.get("assignments") or assigned.get("documents") or []
    bad = []
    for item in items:
        num = item.get("number", "")
        if not NUMBER_RE.match(str(num)):
            bad.append(f"{item.get('request_id','?')}: {num!r} does not match PREFIX-CC-NNN")
    if bad:
        return 0.0, "; ".join(bad)
    return 1.0, None


def _check_category_codes(assigned, updated_master):
    """Category codes must exactly match the functional area per the standard table."""
    if assigned is None:
        return 0.0, "assigned_numbers.json missing"
    assignments = _get_assignments(assigned)
    wrong = []
    for rid, exp in EXPECTED.items():
        item = assignments.get(rid)
        if item is None:
            wrong.append(f"{rid}: missing from assignments")
            continue
        num = item.get("number", "")
        m = NUMBER_RE.match(str(num))
        if not m:
            wrong.append(f"{rid}: bad number format {num!r}")
            continue
        got_cc = m.group(2)
        if got_cc != exp["category_code"]:
            wrong.append(f"{rid}: expected category {exp['category_code']}, got {got_cc} (number: {num!r})")
    if wrong:
        return 0.0, "; ".join(wrong)
    return 1.0, None


def _check_req002_sequence(assigned, updated_master):
    """REQ-002 must be SOP-05-003, not SOP-05-001, because two SOPs already exist in category 05."""
    if assigned is None:
        return 0.0, "assigned_numbers.json missing"
    assignments = _get_assignments(assigned)
    item = assignments.get("REQ-002")
    if item is None:
        return 0.0, "REQ-002 not found in assignments"
    num = item.get("number", "")
    if num != "SOP-05-003":
        return 0.0, (
            f"REQ-002 (Supplier Re-qualification SOP in category 05) should be SOP-05-003 "
            f"because SOP-05-001 and SOP-05-002 already exist in the master list; got {num!r}"
        )
    return 1.0, None


def _check_req006_category(assigned, updated_master):
    """REQ-006 is a PLN for Risk Management (category 09), NOT Quality Management (01)."""
    if assigned is None:
        return 0.0, "assigned_numbers.json missing"
    assignments = _get_assignments(assigned)
    item = assignments.get("REQ-006")
    if item is None:
        return 0.0, "REQ-006 not found in assignments"
    num = item.get("number", "")
    if num != "PLN-09-001":
        return 0.0, (
            f"REQ-006 (Risk Management Plan) belongs to functional area 'Risk Management' "
            f"(category code 09), not 'Quality Management' (01). Expected PLN-09-001, got {num!r}"
        )
    return 1.0, None


def _check_spec04_sequence(assigned, updated_master):
    """REQ-005 must be SPEC-04-003 (not 001 or 002) because SPEC-04-001 and SPEC-04-002 already exist — even though SPEC-04-002 is Superseded."""
    if assigned is None:
        return 0.0, "assigned_numbers.json missing"
    assignments = _get_assignments(assigned)
    item = assignments.get("REQ-005")
    if item is None:
        return 0.0, "REQ-005 not found in assignments"
    num = item.get("number", "")
    if num != "SPEC-04-003":
        return 0.0, (
            f"REQ-005 (Sterilization Validation SPEC in category 04) should be SPEC-04-003 "
            f"because SPEC-04-001 and SPEC-04-002 already exist (the Superseded status of "
            f"SPEC-04-002 does not free up its number for reuse); got {num!r}"
        )
    return 1.0, None


def _check_no_duplicates(assigned, updated_master):
    """No two assigned documents may share a number, and no assigned number may duplicate an existing master list number."""
    if assigned is None:
        return 0.0, "assigned_numbers.json missing"
    items = assigned.get("assignments") or assigned.get("documents") or []
    new_numbers = [str(item.get("number", "")) for item in items]
    seen = set()
    dups = []
    for n in new_numbers:
        if n in seen:
            dups.append(f"duplicate within batch: {n!r}")
        seen.add(n)
    clashes = [n for n in new_numbers if n in EXISTING_NUMBERS]
    if clashes:
        dups.extend([f"clashes with existing master list entry: {n!r}" for n in clashes])
    if dups:
        return 0.0, "; ".join(dups)
    return 1.0, None


def _check_updated_master_exists(assigned, updated_master):
    """updated_master_list.json must exist and contain all 15 documents (8 existing + 7 new)."""
    if updated_master is None:
        return 0.0, "updated_master_list.json missing or unparseable"
    docs = updated_master.get("documents") or []
    if len(docs) < 15:
        return 0.0, f"expected 15 documents in updated master list (8 existing + 7 new), found {len(docs)}"
    return 1.0, None


def _check_existing_preserved(assigned, updated_master):
    """All 8 existing master list entries must still be present in updated_master_list.json with their original numbers."""
    if updated_master is None:
        return 0.0, "updated_master_list.json missing"
    docs = updated_master.get("documents") or []
    present = {str(d.get("number", "")) for d in docs}
    missing = EXISTING_NUMBERS - present
    if missing:
        return 0.0, f"existing documents missing from updated master list: {sorted(missing)}"
    return 1.0, None


def _check_new_docs_in_master(assigned, updated_master):
    """All 7 newly assigned numbers must appear in updated_master_list.json."""
    if assigned is None or updated_master is None:
        return 0.0, "assigned_numbers.json or updated_master_list.json missing"
    items = assigned.get("assignments") or assigned.get("documents") or []
    new_numbers = {str(item.get("number", "")) for item in items}
    docs = updated_master.get("documents") or []
    present = {str(d.get("number", "")) for d in docs}
    missing = new_numbers - present
    if missing:
        return 0.0, f"newly assigned numbers not in updated master list: {sorted(missing)}"
    return 1.0, None


def _check_required_master_fields(assigned, updated_master):
    """Every document in updated_master_list.json must have number, title, doc_type, category_code, revision, status, owner."""
    if updated_master is None:
        return 0.0, "updated_master_list.json missing"
    required = {"number", "title", "doc_type", "category_code", "revision", "status", "owner"}
    docs = updated_master.get("documents") or []
    bad = []
    for doc in docs:
        missing_fields = required - set(doc.keys())
        if missing_fields:
            bad.append(f"{doc.get('number','?')}: missing fields {sorted(missing_fields)}")
    if bad:
        return 0.0, "; ".join(bad[:3]) + (f" ... and {len(bad)-3} more" if len(bad) > 3 else "")
    return 1.0, None


def _check_new_docs_status_draft(assigned, updated_master):
    """Newly assigned documents must appear in the updated master list with status 'Draft' (they have not yet been approved or made effective)."""
    if assigned is None or updated_master is None:
        return 0.0, "assigned_numbers.json or updated_master_list.json missing"
    items = assigned.get("assignments") or assigned.get("documents") or []
    new_numbers = {str(item.get("number", "")) for item in items}
    docs = updated_master.get("documents") or []
    wrong = []
    for doc in docs:
        num = str(doc.get("number", ""))
        if num in new_numbers:
            status = str(doc.get("status", ""))
            if status != "Draft":
                wrong.append(f"{num}: expected status 'Draft', got {status!r}")
    if wrong:
        return 0.0, "; ".join(wrong)
    return 1.0, None


# ---- Criterion registry -------------------------------------------------------

CRITERIA = [
    {
        "id": "assigned-exists",
        "weight": 0.05,
        "description": "assigned_numbers.json exists at the workspace root, parses as JSON, and contains at least 7 assignment entries for the 7 document requests.",
        "check": _check_assigned_exists,
    },
    {
        "id": "number-format",
        "weight": 0.10,
        "description": "Every assigned document number strictly matches the format PREFIX-CC-NNN where PREFIX is the document type code, CC is a two-digit category code, and NNN is a three-digit zero-padded sequence — no deviations such as PREFIX-C-NNN or PREFIX-CC-NN.",
        "check": _check_number_format,
    },
    {
        "id": "category-codes",
        "weight": 0.20,
        "description": "Category codes in all 7 assigned numbers exactly match the functional area per the standard table (01=Quality Management, 04=Design & Development, 05=Purchasing, 06=Production, 07=Quality Control, 08=CAPA, 09=Risk Management). A wrong category code is a misclassification, not a format error.",
        "check": _check_category_codes,
    },
    {
        "id": "req002-sequence",
        "weight": 0.15,
        "description": "REQ-002 (Supplier Re-qualification SOP in Purchasing/category 05) must be assigned SOP-05-003 because SOP-05-001 and SOP-05-002 already exist in the master list. The next available sequence continues from the highest existing sequence, regardless of the order in which the new requests are processed.",
        "check": _check_req002_sequence,
    },
    {
        "id": "req006-category",
        "weight": 0.15,
        "description": "REQ-006 (Risk Management Plan) must be assigned PLN-09-001 under category 09 (Risk Management), not PLN-01-001 under category 01 (Quality Management). A plan's numbering category is determined by its functional area, not by whether it sits under the broader quality system umbrella.",
        "check": _check_req006_category,
    },
    {
        "id": "spec04-sequence",
        "weight": 0.10,
        "description": "REQ-005 (Sterilization Validation SPEC) must be SPEC-04-003 because both SPEC-04-001 and SPEC-04-002 already appear in the master list. A Superseded document retains its number permanently — its number is not recycled or reassigned to new documents.",
        "check": _check_spec04_sequence,
    },
    {
        "id": "no-duplicates",
        "weight": 0.10,
        "description": "No two requests in the batch may be assigned the same document number, and none of the newly assigned numbers may collide with any number already recorded in the existing master list (including Superseded documents).",
        "check": _check_no_duplicates,
    },
    {
        "id": "updated-master-exists",
        "weight": 0.04,
        "description": "updated_master_list.json exists at the workspace root and contains all 15 documents — the 8 original master list entries plus the 7 newly assigned documents.",
        "check": _check_updated_master_exists,
    },
    {
        "id": "existing-preserved",
        "weight": 0.04,
        "description": "All 8 original master list document numbers are still present in updated_master_list.json with their original numbers intact. Document Control may not renumber or remove existing entries when adding new ones.",
        "check": _check_existing_preserved,
    },
    {
        "id": "new-docs-in-master",
        "weight": 0.04,
        "description": "All 7 newly assigned document numbers appear in updated_master_list.json, confirming that the updated list is the authoritative single source of truth for all controlled documents.",
        "check": _check_new_docs_in_master,
    },
    {
        "id": "required-master-fields",
        "weight": 0.02,
        "description": "Every document record in updated_master_list.json contains the required fields: number, title, doc_type, category_code, revision, status, and owner.",
        "check": _check_required_master_fields,
    },
    {
        "id": "new-docs-status-draft",
        "weight": 0.01,
        "description": "Newly assigned documents in updated_master_list.json carry status 'Draft' — they have not yet been reviewed, approved, or made effective, so any other status is premature.",
        "check": _check_new_docs_status_draft,
    },
]

# Sanity check at import time.
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    assigned, _ = _load_assigned(workspace_path)
    updated_master, _ = _load_updated_master(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](assigned, updated_master)
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

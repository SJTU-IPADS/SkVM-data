"""
Reference solution for quality-documentation-manager_task_01.

Reads document_requests.json and master_list_current.json from the workspace,
assigns document numbers using PREFIX-CC-NNN format with correct category codes
and sequence continuation, then writes:
  - assigned_numbers.json
  - updated_master_list.json
"""
import json
from pathlib import Path

# Category code table per SKILL.md
CATEGORY_CODES = {
    "Quality Management":   "01",
    "Document Control":     "02",
    "Human Resources":      "03",
    "Design & Development": "04",
    "Purchasing":           "05",
    "Production":           "06",
    "Quality Control":      "07",
    "CAPA":                 "08",
    "Risk Management":      "09",
    "Regulatory Affairs":   "10",
}

workspace = Path(".")

# Load fixtures
requests_data = json.loads((workspace / "document_requests.json").read_text())
master_data   = json.loads((workspace / "master_list_current.json").read_text())

existing_docs = master_data["documents"]

# Build a registry: (prefix, category_code) -> highest_sequence_seen
sequence_registry: dict[tuple[str, str], int] = {}
for doc in existing_docs:
    num = doc["number"]
    parts = num.split("-")
    if len(parts) == 3:
        prefix = parts[0]
        cat    = parts[1]
        seq    = int(parts[2])
        key = (prefix, cat)
        sequence_registry[key] = max(sequence_registry.get(key, 0), seq)

# Process requests in order
assignments = []
for req in requests_data["requests"]:
    prefix   = req["doc_type"]
    area     = req["functional_area"]
    cat_code = CATEGORY_CODES[area]
    key = (prefix, cat_code)
    next_seq = sequence_registry.get(key, 0) + 1
    sequence_registry[key] = next_seq
    doc_number = f"{prefix}-{cat_code}-{next_seq:03d}"
    assignments.append({
        "request_id":     req["request_id"],
        "title":          req["title"],
        "doc_type":       prefix,
        "functional_area": area,
        "category_code":  cat_code,
        "number":         doc_number,
        "revision":       "01",
        "status":         "Draft",
        "requested_by":   req["requested_by"],
    })

# Write assigned_numbers.json
assigned_out = {
    "request_batch": requests_data["request_batch"],
    "processed_date": "2025-01-20",
    "assignments": assignments,
}
(workspace / "assigned_numbers.json").write_text(json.dumps(assigned_out, indent=2))

# Build updated master list: existing + new (status=Draft for new)
new_docs = []
for asgn in assignments:
    new_docs.append({
        "number":        asgn["number"],
        "title":         asgn["title"],
        "doc_type":      asgn["doc_type"],
        "category_code": asgn["category_code"],
        "revision":      "01",
        "status":        "Draft",
        "effective_date": None,
        "review_due":    None,
        "owner":         asgn["requested_by"],
    })

updated_master = {
    "company": master_data["company"],
    "system_version": master_data["system_version"],
    "last_updated": "2025-01-20",
    "documents": existing_docs + new_docs,
}
(workspace / "updated_master_list.json").write_text(json.dumps(updated_master, indent=2))

print("Done.")
print(f"  assigned_numbers.json: {len(assignments)} assignments")
print(f"  updated_master_list.json: {len(updated_master['documents'])} total documents")
for asgn in assignments:
    print(f"    {asgn['request_id']} -> {asgn['number']}")

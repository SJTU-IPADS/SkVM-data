"""
Grade function for schema-markup-generator_task_02.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum=1.0), description, details?}.

Task: agent reads page_brief.json and writes combined_schema.json — a JSON
array containing both BreadcrumbList and FAQPage schemas.

Trap archetypes targeted:
- Archetype 1 (under-specified step): BreadcrumbList ListItem structure is
  vague in most guides — agents must use 'item' (not 'url'), 'name', 'position'
  (1-indexed integer), and @type='ListItem'
- Archetype 2 (common-default-wrong): agents commonly use 'url' instead of
  'item' for the breadcrumb URL; position starting at 0 instead of 1; writing
  the output as a single object instead of a JSON array
- Archetype 3 (multi-step coordination): BreadcrumbList and FAQPage must
  both be correct simultaneously in the same JSON array output file
"""
from __future__ import annotations

import json
from pathlib import Path


# ---- Helpers ----------------------------------------------------------------

def _load_combined(workspace_path: str) -> tuple[list | None, str | None]:
    p = Path(workspace_path) / "combined_schema.json"
    if not p.exists():
        return None, "combined_schema.json not found in workspace"
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        return None, f"combined_schema.json is not valid JSON: {e}"
    return data, None


def _find_schema(schemas: list, type_name: str) -> dict | None:
    """Find the first schema object in the array with the given @type."""
    for obj in schemas:
        if isinstance(obj, dict) and obj.get("@type") == type_name:
            return obj
    return None


# ---- Per-criterion checks ---------------------------------------------------

def _check_file_valid(schemas, _):
    if schemas is None:
        return 0.0, "combined_schema.json missing or not valid JSON"
    return 1.0, None


def _check_output_is_array(schemas, _):
    """
    combined_schema.json must be a JSON array, not a single object.
    The task requires two schemas in one file; a common mistake is to
    write them as a dict with two keys or as two separate files.
    """
    if schemas is None:
        return 0.0, "combined_schema.json missing"
    if not isinstance(schemas, list):
        return 0.0, (
            f"combined_schema.json is a {type(schemas).__name__}, not a JSON array. "
            f"The output must be a JSON array containing both schema objects."
        )
    return 1.0, None


def _check_breadcrumb_present(schemas, _):
    if schemas is None or not isinstance(schemas, list):
        return 0.0, "combined_schema.json missing or not an array"
    bc = _find_schema(schemas, "BreadcrumbList")
    if bc is None:
        return 0.0, "No object with @type='BreadcrumbList' found in combined_schema.json"
    return 1.0, None


def _check_faqpage_present(schemas, _):
    if schemas is None or not isinstance(schemas, list):
        return 0.0, "combined_schema.json missing or not an array"
    faq = _find_schema(schemas, "FAQPage")
    if faq is None:
        return 0.0, "No object with @type='FAQPage' found in combined_schema.json"
    return 1.0, None


def _check_breadcrumb_context(schemas, _):
    if schemas is None or not isinstance(schemas, list):
        return 0.0, "combined_schema.json missing"
    bc = _find_schema(schemas, "BreadcrumbList")
    if bc is None:
        return 0.0, "BreadcrumbList not found"
    ctx = bc.get("@context")
    if ctx == "https://schema.org":
        return 1.0, None
    return 0.0, f"BreadcrumbList @context is {ctx!r}; must be 'https://schema.org'"


def _check_breadcrumb_item_list_element(schemas, _):
    """itemListElement must be an array on the BreadcrumbList object."""
    if schemas is None or not isinstance(schemas, list):
        return 0.0, "combined_schema.json missing"
    bc = _find_schema(schemas, "BreadcrumbList")
    if bc is None:
        return 0.0, "BreadcrumbList not found"
    ile = bc.get("itemListElement")
    if not isinstance(ile, list):
        return 0.0, f"BreadcrumbList.itemListElement must be an array, got {type(ile).__name__}"
    if len(ile) != 3:
        return 0.0, f"Expected 3 breadcrumb ListItems, got {len(ile)}"
    return 1.0, None


def _check_listitem_type(schemas, _):
    """Each breadcrumb item must have @type='ListItem'."""
    if schemas is None or not isinstance(schemas, list):
        return 0.0, "combined_schema.json missing"
    bc = _find_schema(schemas, "BreadcrumbList")
    if bc is None:
        return 0.0, "BreadcrumbList not found"
    ile = bc.get("itemListElement")
    if not isinstance(ile, list):
        return 0.0, "itemListElement is not an array"
    wrong = [i for i, el in enumerate(ile) if not (isinstance(el, dict) and el.get("@type") == "ListItem")]
    if wrong:
        got = [ile[i].get("@type") if isinstance(ile[i], dict) else type(ile[i]).__name__ for i in wrong]
        return 0.0, f"itemListElement[{wrong}] @type must be 'ListItem', got {got}"
    return 1.0, None


def _check_position_one_indexed(schemas, _):
    """
    BreadcrumbList positions must be 1-indexed sequential integers (1, 2, 3).
    Starting at 0 is a common default-wrong: it matches Python list indexes
    but violates Schema.org's ListItem spec where position is 1-based.
    """
    if schemas is None or not isinstance(schemas, list):
        return 0.0, "combined_schema.json missing"
    bc = _find_schema(schemas, "BreadcrumbList")
    if bc is None:
        return 0.0, "BreadcrumbList not found"
    ile = bc.get("itemListElement")
    if not isinstance(ile, list) or len(ile) == 0:
        return 0.0, "itemListElement missing or empty"
    positions = []
    for el in ile:
        if isinstance(el, dict):
            p = el.get("position")
            try:
                positions.append(int(p))
            except (TypeError, ValueError):
                positions.append(None)
    expected = list(range(1, len(ile) + 1))
    if positions == expected:
        return 1.0, None
    return 0.0, (
        f"positions are {positions}; must be {expected} (1-indexed integers, "
        f"not 0-indexed). Schema.org ListItem.position starts at 1."
    )


def _check_item_property_not_url(schemas, _):
    """
    Each BreadcrumbList ListItem must use the property name 'item' (not 'url')
    for the page URL. Using 'url' is the most common mistake because HTML
    anchor elements use href/url, but Schema.org ListItem uses 'item' for
    the URL of the breadcrumb destination.
    """
    if schemas is None or not isinstance(schemas, list):
        return 0.0, "combined_schema.json missing"
    bc = _find_schema(schemas, "BreadcrumbList")
    if bc is None:
        return 0.0, "BreadcrumbList not found"
    ile = bc.get("itemListElement")
    if not isinstance(ile, list) or len(ile) == 0:
        return 0.0, "itemListElement missing or empty"
    wrong_key = []
    missing_item = []
    for i, el in enumerate(ile):
        if not isinstance(el, dict):
            continue
        if "url" in el and "item" not in el:
            wrong_key.append(i)
        elif "item" not in el:
            missing_item.append(i)
    if wrong_key:
        return 0.0, (
            f"ListItem[{wrong_key}] uses 'url' instead of 'item' for the breadcrumb URL. "
            f"Schema.org ListItem uses the property 'item' (not 'url') for the destination URL."
        )
    if missing_item:
        return 0.0, f"ListItem[{missing_item}] is missing the 'item' property"
    return 1.0, None


def _check_breadcrumb_name_property(schemas, _):
    """Each BreadcrumbList ListItem must have a 'name' string property."""
    if schemas is None or not isinstance(schemas, list):
        return 0.0, "combined_schema.json missing"
    bc = _find_schema(schemas, "BreadcrumbList")
    if bc is None:
        return 0.0, "BreadcrumbList not found"
    ile = bc.get("itemListElement")
    if not isinstance(ile, list) or len(ile) == 0:
        return 0.0, "itemListElement missing or empty"
    missing = [i for i, el in enumerate(ile) if isinstance(el, dict) and not el.get("name")]
    if missing:
        return 0.0, f"ListItem[{missing}] is missing 'name' property"
    # Check names match expected breadcrumb names
    expected_names = ["Home", "Guides", "How to Choose Running Shoes"]
    got_names = [el.get("name") for el in ile if isinstance(el, dict)]
    if got_names != expected_names:
        return 0.0, f"breadcrumb names are {got_names}; expected {expected_names}"
    return 1.0, None


def _check_faqpage_context(schemas, _):
    if schemas is None or not isinstance(schemas, list):
        return 0.0, "combined_schema.json missing"
    faq = _find_schema(schemas, "FAQPage")
    if faq is None:
        return 0.0, "FAQPage not found"
    ctx = faq.get("@context")
    if ctx == "https://schema.org":
        return 1.0, None
    return 0.0, f"FAQPage @context is {ctx!r}; must be 'https://schema.org'"


def _check_faq_main_entity(schemas, _):
    """FAQPage.mainEntity must be an array with exactly 3 Question objects."""
    if schemas is None or not isinstance(schemas, list):
        return 0.0, "combined_schema.json missing"
    faq = _find_schema(schemas, "FAQPage")
    if faq is None:
        return 0.0, "FAQPage not found"
    me = faq.get("mainEntity")
    if not isinstance(me, list):
        return 0.0, f"FAQPage.mainEntity must be an array, got {type(me).__name__}"
    if len(me) != 3:
        return 0.0, f"Expected 3 FAQ questions in mainEntity, got {len(me)}"
    return 1.0, None


def _check_question_type(schemas, _):
    """Each mainEntity item must have @type='Question'."""
    if schemas is None or not isinstance(schemas, list):
        return 0.0, "combined_schema.json missing"
    faq = _find_schema(schemas, "FAQPage")
    if faq is None:
        return 0.0, "FAQPage not found"
    me = faq.get("mainEntity")
    if not isinstance(me, list):
        return 0.0, "mainEntity not an array"
    wrong = [i for i, el in enumerate(me) if not (isinstance(el, dict) and el.get("@type") == "Question")]
    if wrong:
        got = [me[i].get("@type") if isinstance(me[i], dict) else type(me[i]).__name__ for i in wrong]
        return 0.0, f"mainEntity[{wrong}] @type must be 'Question', got {got}"
    return 1.0, None


def _check_accepted_answer_structure(schemas, _):
    """
    Each Question must have acceptedAnswer with @type='Answer' and non-empty text.
    A common mistake is to put the answer text directly as a string value of
    'acceptedAnswer' rather than nesting it in an Answer object.
    """
    if schemas is None or not isinstance(schemas, list):
        return 0.0, "combined_schema.json missing"
    faq = _find_schema(schemas, "FAQPage")
    if faq is None:
        return 0.0, "FAQPage not found"
    me = faq.get("mainEntity")
    if not isinstance(me, list):
        return 0.0, "mainEntity not an array"
    errors = []
    for i, q in enumerate(me):
        if not isinstance(q, dict):
            errors.append(f"mainEntity[{i}] is not an object")
            continue
        aa = q.get("acceptedAnswer")
        if aa is None:
            errors.append(f"Question[{i}] missing acceptedAnswer")
        elif not isinstance(aa, dict):
            errors.append(f"Question[{i}].acceptedAnswer must be an object, got {type(aa).__name__}")
        elif aa.get("@type") != "Answer":
            errors.append(f"Question[{i}].acceptedAnswer.@type must be 'Answer', got {aa.get('@type')!r}")
        elif not aa.get("text"):
            errors.append(f"Question[{i}].acceptedAnswer.text is missing or empty")
    if errors:
        return 0.0, "; ".join(errors)
    return 1.0, None


# ---- Criterion registry -----------------------------------------------------

CRITERIA = [
    {
        "id": "file-valid",
        "weight": 0.04,
        "description": "combined_schema.json exists at the workspace root and is valid JSON.",
        "check": _check_file_valid,
    },
    {
        "id": "output-is-array",
        "weight": 0.12,
        "description": (
            "combined_schema.json is a JSON array (not a single object). "
            "When combining multiple schemas in one file, the output must be a "
            "top-level array of schema objects, not a single dict or separate files."
        ),
        "check": _check_output_is_array,
    },
    {
        "id": "breadcrumb-present",
        "weight": 0.06,
        "description": "The JSON array contains an object with @type='BreadcrumbList'.",
        "check": _check_breadcrumb_present,
    },
    {
        "id": "faqpage-present",
        "weight": 0.06,
        "description": "The JSON array contains an object with @type='FAQPage'.",
        "check": _check_faqpage_present,
    },
    {
        "id": "breadcrumb-context",
        "weight": 0.05,
        "description": "BreadcrumbList has @context='https://schema.org' (https, no trailing slash).",
        "check": _check_breadcrumb_context,
    },
    {
        "id": "breadcrumb-item-list-element",
        "weight": 0.06,
        "description": "BreadcrumbList.itemListElement is an array with exactly 3 ListItem objects, matching the 3 breadcrumbs in page_brief.json.",
        "check": _check_breadcrumb_item_list_element,
    },
    {
        "id": "listitem-type",
        "weight": 0.06,
        "description": "Every element in BreadcrumbList.itemListElement has @type='ListItem'.",
        "check": _check_listitem_type,
    },
    {
        "id": "position-one-indexed",
        "weight": 0.15,
        "description": (
            "BreadcrumbList positions are 1-indexed sequential integers (1, 2, 3). "
            "Schema.org ListItem.position is 1-based; using 0-based indexing (0, 1, 2) "
            "is incorrect and causes structured data validation errors."
        ),
        "check": _check_position_one_indexed,
    },
    {
        "id": "item-property-not-url",
        "weight": 0.18,
        "description": (
            "Each BreadcrumbList ListItem uses the property 'item' (not 'url') for the "
            "destination URL. Schema.org ListItem specifies 'item' as the URL property; "
            "using 'url' is the most common mistake because it sounds natural but "
            "structured data validators reject it."
        ),
        "check": _check_item_property_not_url,
    },
    {
        "id": "breadcrumb-name-property",
        "weight": 0.06,
        "description": "Each ListItem has a 'name' string property matching the breadcrumb labels from page_brief.json (Home, Guides, How to Choose Running Shoes).",
        "check": _check_breadcrumb_name_property,
    },
    {
        "id": "faqpage-context",
        "weight": 0.04,
        "description": "FAQPage has @context='https://schema.org' (https, no trailing slash).",
        "check": _check_faqpage_context,
    },
    {
        "id": "faq-main-entity",
        "weight": 0.06,
        "description": "FAQPage.mainEntity is an array with exactly 3 Question objects, matching the 3 FAQs in page_brief.json.",
        "check": _check_faq_main_entity,
    },
    {
        "id": "question-type",
        "weight": 0.04,
        "description": "Every object in FAQPage.mainEntity has @type='Question'.",
        "check": _check_question_type,
    },
    {
        "id": "accepted-answer-structure",
        "weight": 0.02,
        "description": (
            "Every Question has acceptedAnswer as an object with @type='Answer' and "
            "non-empty text. Placing the answer text directly as a string under "
            "'acceptedAnswer' (instead of nesting it in an Answer object) is invalid."
        ),
        "check": _check_accepted_answer_structure,
    },
]

# Sanity: weights sum to 1.0
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}"


def grade(transcript, workspace_path):
    schemas, _ = _load_combined(workspace_path)
    if not isinstance(schemas, list):
        schemas_list = None
    else:
        schemas_list = schemas

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](schemas_list, None)
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

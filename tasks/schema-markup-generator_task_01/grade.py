"""
Grade function for schema-markup-generator_task_01.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum=1.0), description, details?}.

Task: agent reads product_brief.json and writes product_schema.json containing
a Schema.org Product + AggregateRating JSON-LD object.

Trap archetypes targeted:
- Archetype 4 (known-edge-case): @context exact URL, availability/condition as
  full schema.org URLs, priceValidUntil as YYYY-MM-DD, priceCurrency as ISO 4217
- Archetype 5 (stateful invariant): ratingCount must match source; all nested
  @type values must be correct Schema.org type names
- Archetype 3 (multi-step coordination): Product + Offer + AggregateRating must
  all be correct simultaneously in one JSON-LD object
"""
from __future__ import annotations

import json
import re
from pathlib import Path


# ---- Helpers ----------------------------------------------------------------

def _load_schema(workspace_path: str) -> tuple[dict | None, str | None]:
    p = Path(workspace_path) / "product_schema.json"
    if not p.exists():
        return None, "product_schema.json not found in workspace"
    try:
        return json.loads(p.read_text()), None
    except json.JSONDecodeError as e:
        return None, f"product_schema.json is not valid JSON: {e}"


def _get_offers(schema: dict) -> dict | None:
    """Return the first Offer object, tolerating array or single-object."""
    offers = schema.get("offers")
    if isinstance(offers, list):
        return offers[0] if offers else None
    return offers if isinstance(offers, dict) else None


def _get_aggregate_rating(schema: dict) -> dict | None:
    ar = schema.get("aggregateRating")
    return ar if isinstance(ar, dict) else None


# ---- Per-criterion checks ---------------------------------------------------

def _check_file_exists(schema, _brief):
    if schema is None:
        return 0.0, "product_schema.json missing or not valid JSON"
    return 1.0, None


def _check_context_exact(schema, _brief):
    """@context must be exactly 'https://schema.org' — not http://, not with trailing slash."""
    if schema is None:
        return 0.0, "product_schema.json missing"
    ctx = schema.get("@context")
    if ctx == "https://schema.org":
        return 1.0, None
    return 0.0, (
        f"@context is {ctx!r}; must be exactly 'https://schema.org' "
        f"(https, no trailing slash, no path)"
    )


def _check_product_type(schema, _brief):
    if schema is None:
        return 0.0, "product_schema.json missing"
    t = schema.get("@type")
    if t == "Product":
        return 1.0, None
    return 0.0, f"@type is {t!r}; must be 'Product'"


def _check_required_product_fields(schema, _brief):
    """Product must carry name, description, sku, brand, offers, aggregateRating."""
    if schema is None:
        return 0.0, "product_schema.json missing"
    required = {"name", "description", "sku", "brand", "offers", "aggregateRating"}
    missing = required - set(schema.keys())
    if missing:
        return 0.0, f"Product missing required properties: {sorted(missing)}"
    return 1.0, None


def _check_brand_type(schema, _brief):
    """brand must be an object with @type 'Brand' and a non-empty name."""
    if schema is None:
        return 0.0, "product_schema.json missing"
    brand = schema.get("brand")
    if not isinstance(brand, dict):
        return 0.0, f"brand must be an object with @type 'Brand', got {type(brand).__name__}"
    t = brand.get("@type")
    name = brand.get("name")
    if t != "Brand":
        return 0.0, f"brand.@type is {t!r}; must be 'Brand'"
    if not name or not str(name).strip():
        return 0.0, "brand.name is empty or missing"
    return 1.0, None


def _check_offer_type(schema, _brief):
    """offers must contain an Offer object with @type exactly 'Offer'."""
    if schema is None:
        return 0.0, "product_schema.json missing"
    offers = _get_offers(schema)
    if offers is None:
        return 0.0, "offers property is missing or not an object"
    t = offers.get("@type")
    if t != "Offer":
        return 0.0, f"offers.@type is {t!r}; must be 'Offer'"
    return 1.0, None


def _check_availability_full_url(schema, _brief):
    """
    availability must be the full Schema.org URL 'https://schema.org/InStock',
    not the bare string 'InStock' or 'in stock'. This is a common-default-wrong
    trap: most JSON-LD examples use bare values but Google's structured data
    requires the full URL form.
    """
    if schema is None:
        return 0.0, "product_schema.json missing"
    offers = _get_offers(schema)
    if offers is None:
        return 0.0, "offers missing"
    avail = offers.get("availability")
    if avail == "https://schema.org/InStock":
        return 1.0, None
    return 0.0, (
        f"availability is {avail!r}; must be 'https://schema.org/InStock' "
        f"(full URL — bare 'InStock' or 'in stock' is invalid per Schema.org spec)"
    )


def _check_condition_full_url(schema, _brief):
    """
    itemCondition must be 'https://schema.org/NewCondition' (full URL).
    Bare 'NewCondition', 'new', or omitting the field altogether are wrong.
    """
    if schema is None:
        return 0.0, "product_schema.json missing"
    offers = _get_offers(schema)
    if offers is None:
        return 0.0, "offers missing"
    cond = offers.get("itemCondition")
    if cond == "https://schema.org/NewCondition":
        return 1.0, None
    return 0.0, (
        f"itemCondition is {cond!r}; must be 'https://schema.org/NewCondition' "
        f"(full URL — bare 'NewCondition' or 'new' is not valid)"
    )


def _check_price_valid_until_format(schema, _brief):
    """
    priceValidUntil must be a date string in YYYY-MM-DD format (ISO 8601 date-only).
    DateTime strings with time component or slashes are invalid.
    """
    if schema is None:
        return 0.0, "product_schema.json missing"
    offers = _get_offers(schema)
    if offers is None:
        return 0.0, "offers missing"
    pvu = offers.get("priceValidUntil")
    if pvu is None:
        return 0.0, "offers.priceValidUntil is missing"
    if isinstance(pvu, str) and re.match(r"^\d{4}-\d{2}-\d{2}$", pvu):
        return 1.0, None
    return 0.0, (
        f"priceValidUntil is {pvu!r}; must be YYYY-MM-DD format "
        f"(date-only ISO 8601 — no time component)"
    )


def _check_price_currency_iso(schema, _brief):
    """
    priceCurrency must be an ISO 4217 3-letter code like 'USD', not a symbol
    like '$'. This is a common mistake because the brief says 'currency: USD'
    but some agents substitute the currency symbol instead.
    """
    if schema is None:
        return 0.0, "product_schema.json missing"
    offers = _get_offers(schema)
    if offers is None:
        return 0.0, "offers missing"
    cur = offers.get("priceCurrency")
    if cur is None:
        return 0.0, "offers.priceCurrency is missing"
    if isinstance(cur, str) and re.match(r"^[A-Z]{3}$", cur):
        return 1.0, None
    return 0.0, (
        f"priceCurrency is {cur!r}; must be an ISO 4217 3-letter code like 'USD', "
        f"not a currency symbol like '$'"
    )


def _check_aggregate_rating_type(schema, _brief):
    if schema is None:
        return 0.0, "product_schema.json missing"
    ar = _get_aggregate_rating(schema)
    if ar is None:
        return 0.0, "aggregateRating is missing or not an object"
    t = ar.get("@type")
    if t == "AggregateRating":
        return 1.0, None
    return 0.0, f"aggregateRating.@type is {t!r}; must be 'AggregateRating'"


def _check_rating_value_numeric(schema, _brief):
    """ratingValue must be a JSON number (not a string) equal to 4.6 from the brief."""
    if schema is None:
        return 0.0, "product_schema.json missing"
    ar = _get_aggregate_rating(schema)
    if ar is None:
        return 0.0, "aggregateRating missing"
    rv = ar.get("ratingValue")
    if rv is None:
        return 0.0, "aggregateRating.ratingValue missing"
    if isinstance(rv, str):
        return 0.0, (
            f"ratingValue is a string {rv!r}; must be a JSON number. "
            f"Schema.org requires numeric type for ratingValue."
        )
    try:
        v = float(rv)
    except (TypeError, ValueError):
        return 0.0, f"ratingValue {rv!r} cannot be parsed as a number"
    if abs(v - 4.6) > 0.01:
        return 0.0, f"ratingValue is {v}; expected 4.6 from product_brief.json"
    return 1.0, None


def _check_rating_count_invariant(schema, _brief):
    """
    ratingCount must equal 312, matching the product_brief.json source.
    This is a stateful invariant: the agent must propagate the count from
    the input brief without inventing or rounding it.
    """
    if schema is None:
        return 0.0, "product_schema.json missing"
    ar = _get_aggregate_rating(schema)
    if ar is None:
        return 0.0, "aggregateRating missing"
    rc = ar.get("ratingCount")
    if rc is None:
        return 0.0, "aggregateRating.ratingCount is missing"
    try:
        rc_int = int(rc)
    except (TypeError, ValueError):
        return 0.0, f"ratingCount {rc!r} is not an integer"
    if rc_int == 312:
        return 1.0, None
    return 0.0, (
        f"ratingCount is {rc_int}; expected 312 as stated in product_brief.json"
    )


def _check_best_worst_rating(schema, _brief):
    """
    bestRating and worstRating must both be present and numeric.
    These are required by Google's Product rich result spec to define
    the rating scale, but many agents omit them because the brief
    only says 'rating 4.6 out of 5'.
    """
    if schema is None:
        return 0.0, "product_schema.json missing"
    ar = _get_aggregate_rating(schema)
    if ar is None:
        return 0.0, "aggregateRating missing"
    br = ar.get("bestRating")
    wr = ar.get("worstRating")
    missing = []
    if br is None:
        missing.append("bestRating")
    if wr is None:
        missing.append("worstRating")
    if missing:
        return 0.0, (
            f"aggregateRating missing: {missing}. "
            f"Google requires bestRating and worstRating to define the rating scale."
        )
    try:
        br_v = float(br)
        wr_v = float(wr)
    except (TypeError, ValueError):
        return 0.0, f"bestRating={br!r} or worstRating={wr!r} is not numeric"
    if abs(br_v - 5) > 0.01 or abs(wr_v - 1) > 0.01:
        return 0.0, (
            f"bestRating={br_v}, worstRating={wr_v}; "
            f"expected bestRating=5, worstRating=1 from product_brief.json"
        )
    return 1.0, None


# ---- Criterion registry -----------------------------------------------------

CRITERIA = [
    {
        "id": "file-exists",
        "weight": 0.04,
        "description": "product_schema.json exists at the workspace root and is valid JSON.",
        "check": _check_file_exists,
    },
    {
        "id": "context-exact",
        "weight": 0.10,
        "description": (
            "@context is exactly 'https://schema.org' — not 'http://', not "
            "'https://schema.org/' with a trailing slash. The https scheme without "
            "trailing slash is the canonical form required by Google's structured data parser."
        ),
        "check": _check_context_exact,
    },
    {
        "id": "product-type",
        "weight": 0.04,
        "description": "Top-level @type is 'Product' — confirming the agent selected the correct Schema.org type for this e-commerce item.",
        "check": _check_product_type,
    },
    {
        "id": "required-product-fields",
        "weight": 0.06,
        "description": "Product object carries all six required properties: name, description, sku, brand, offers, aggregateRating.",
        "check": _check_required_product_fields,
    },
    {
        "id": "brand-type",
        "weight": 0.05,
        "description": "brand is an object with @type='Brand' and a non-empty name property — not a plain string.",
        "check": _check_brand_type,
    },
    {
        "id": "offer-type",
        "weight": 0.04,
        "description": "offers is an object with @type='Offer' — the nested Offer entity must be typed correctly.",
        "check": _check_offer_type,
    },
    {
        "id": "availability-full-url",
        "weight": 0.15,
        "description": (
            "availability is 'https://schema.org/InStock' (full URL), not the bare "
            "string 'InStock' or 'in stock'. Schema.org enumerations require the full "
            "URL form; bare values are accepted by validators but rejected by Google's "
            "rich results eligibility check."
        ),
        "check": _check_availability_full_url,
    },
    {
        "id": "condition-full-url",
        "weight": 0.12,
        "description": (
            "itemCondition is 'https://schema.org/NewCondition' (full URL). "
            "Bare 'NewCondition' or 'new' fails Schema.org enumeration validation. "
            "This property is required for Product rich results."
        ),
        "check": _check_condition_full_url,
    },
    {
        "id": "price-valid-until-format",
        "weight": 0.08,
        "description": (
            "priceValidUntil is a YYYY-MM-DD date-only string (e.g. '2026-12-31'). "
            "DateTime strings with a time component like 'T00:00:00' are not valid "
            "for this property per Schema.org spec."
        ),
        "check": _check_price_valid_until_format,
    },
    {
        "id": "price-currency-iso",
        "weight": 0.05,
        "description": (
            "priceCurrency is an ISO 4217 3-letter code ('USD'), not a symbol ('$'). "
            "Currency symbols are not valid for priceCurrency even when semantically equivalent."
        ),
        "check": _check_price_currency_iso,
    },
    {
        "id": "aggregate-rating-type",
        "weight": 0.04,
        "description": "aggregateRating is an object with @type='AggregateRating'.",
        "check": _check_aggregate_rating_type,
    },
    {
        "id": "rating-value-numeric",
        "weight": 0.08,
        "description": (
            "ratingValue is a JSON number (not a string) equal to 4.6. "
            "Schema.org specifies ratingValue as a Number; passing it as a quoted "
            "string '4.6' is a type error that breaks structured data parsers."
        ),
        "check": _check_rating_value_numeric,
    },
    {
        "id": "rating-count-invariant",
        "weight": 0.10,
        "description": (
            "ratingCount equals 312, the exact value from product_brief.json. "
            "This stateful invariant checks that the agent faithfully propagated "
            "the source count rather than inventing or rounding it."
        ),
        "check": _check_rating_count_invariant,
    },
    {
        "id": "best-worst-rating",
        "weight": 0.05,
        "description": (
            "aggregateRating carries both bestRating=5 and worstRating=1. "
            "Google's Product rich result spec requires these to define the rating "
            "scale; omitting them causes the structured data to be ineligible for "
            "star display even when ratingValue is correct."
        ),
        "check": _check_best_worst_rating,
    },
]

# Sanity: weights sum to 1.0
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}"


def grade(transcript, workspace_path):
    schema, _ = _load_schema(workspace_path)
    records = []
    for spec in CRITERIA:
        score, details = spec["check"](schema, None)
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

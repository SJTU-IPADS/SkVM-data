"""
Reference solution for schema-markup-generator_task_01.

Reads product_brief.json from cwd and writes product_schema.json containing
a valid Schema.org Product + AggregateRating JSON-LD block.

Key correctness requirements tested by grade.py:
- @context is exactly "https://schema.org" (https, no trailing slash)
- availability is "https://schema.org/InStock" (full URL, not bare "InStock")
- condition is "https://schema.org/NewCondition" (full URL)
- priceValidUntil is "YYYY-MM-DD" (ISO 8601 date-only)
- priceCurrency is "USD" (ISO 4217 code, not "$")
- aggregateRating.ratingCount == 312 (matches source data)
- aggregateRating.ratingValue is 4.6 (numeric, not string)
- bestRating and worstRating present
- All nested @type values are exact Schema.org strings
"""
import json
from pathlib import Path


def main():
    brief = json.loads(Path("product_brief.json").read_text())

    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": brief["name"],
        "description": brief["description"],
        "sku": brief["sku"],
        "brand": {
            "@type": "Brand",
            "name": brief["brand"]
        },
        "image": brief["image_url"],
        "url": brief["product_url"],
        "offers": {
            "@type": "Offer",
            "priceCurrency": brief["currency"],
            "price": brief["price"],
            "priceValidUntil": brief["price_valid_until"],
            "availability": "https://schema.org/InStock",
            "itemCondition": "https://schema.org/NewCondition",
            "url": brief["product_url"]
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": brief["rating_value"],
            "ratingCount": brief["rating_count"],
            "bestRating": brief["best_rating"],
            "worstRating": brief["worst_rating"]
        }
    }

    Path("product_schema.json").write_text(json.dumps(schema, indent=2))
    print("Wrote product_schema.json")


if __name__ == "__main__":
    main()

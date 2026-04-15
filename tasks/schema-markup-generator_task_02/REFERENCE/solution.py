"""
Reference solution for schema-markup-generator_task_02.

Reads page_brief.json from cwd and writes combined_schema.json containing
a JSON array with BreadcrumbList and FAQPage schemas.

Key correctness requirements tested by grade.py:
- Output is a JSON array (not a single object)
- BreadcrumbList has @type="BreadcrumbList" with itemListElement array
- Each itemListElement has @type="ListItem", position (1-indexed integer),
  name (string), and item (URL string) — NOT "url" as the key
- Positions start at 1 and are sequential integers
- FAQPage has @type="FAQPage" with mainEntity array
- Each mainEntity item has @type="Question", name, and acceptedAnswer
- Each acceptedAnswer has @type="Answer" and text
- Both schemas share the same @context "https://schema.org"
- Exactly 3 breadcrumb items and 3 FAQ questions (matching the fixture)
"""
import json
from pathlib import Path


def main():
    brief = json.loads(Path("page_brief.json").read_text())

    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": crumb["name"],
                "item": crumb["url"]
            }
            for i, crumb in enumerate(brief["breadcrumbs"])
        ]
    }

    faqpage_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq["answer"]
                }
            }
            for faq in brief["faqs"]
        ]
    }

    combined = [breadcrumb_schema, faqpage_schema]
    Path("combined_schema.json").write_text(json.dumps(combined, indent=2))
    print("Wrote combined_schema.json")


if __name__ == "__main__":
    main()

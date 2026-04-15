"""
Reference solution for document-pdf_task_02.

Reads ledger.pdf from cwd and produces:
  - ledger_report.json
  - reconciliation_report.md

Protocol:
  1. Extract text from all pages using pdfplumber.
  2. Parse transaction rows (lines starting with TXN-NNNN).
  3. Strip $ and commas from amount strings before parsing to float.
  4. Deduplicate by txn_id using first-occurrence semantics.
  5. Aggregate totals per category over accepted rows only.
  6. Write ledger_report.json and reconciliation_report.md.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


def parse_amount(s: str) -> float | None:
    """Strip $ and commas and parse to float. Returns None on failure."""
    s = s.strip().replace("$", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def parse_row(line: str) -> dict | None:
    """
    Parse one transaction line. Format (from ledger.pdf text extraction):
      TXN-XXXX DATE [DESCRIPTION] $AMOUNT CATEGORY

    Description may be missing (empty cell becomes no tokens between date and amount).
    Returns dict with txn_id, date, description, amount, category, or None if not a data row.
    """
    m = re.match(
        r"^(TXN-\d+)\s+"
        r"(\d{4}-\d{2}-\d{2})\s+"
        r"(.*?)\s*(\$[\d,]+\.\d{2})\s+"
        r"(\w+)\s*$",
        line.strip(),
    )
    if not m:
        return None
    txn_id, date, desc, amount_str, category = m.groups()
    amount = parse_amount(amount_str)
    if amount is None:
        return None
    return {
        "txn_id": txn_id,
        "date": date,
        "description": desc.strip(),
        "amount": amount,
        "category": category,
    }


def extract_rows_from_pdf(pdf_path: str) -> list[dict]:
    """Extract all transaction rows from ledger.pdf using pdfplumber text extraction."""
    import pdfplumber

    all_rows: list[dict] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                row = parse_row(line)
                if row:
                    all_rows.append(row)
    return all_rows


def deduplicate(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """
    Deduplicate by txn_id using first-occurrence semantics.
    Returns (accepted_rows, duplicate_txn_ids).
    """
    seen: set[str] = set()
    accepted: list[dict] = []
    duplicates: list[str] = []

    for row in rows:
        tid = row["txn_id"]
        if tid not in seen:
            seen.add(tid)
            accepted.append(row)
        else:
            duplicates.append(tid)

    return accepted, duplicates


def main() -> None:
    pdf_path = "ledger.pdf"
    raw_rows = extract_rows_from_pdf(pdf_path)
    total_extracted = len(raw_rows)

    accepted, duplicate_ids = deduplicate(raw_rows)
    n_accepted = len(accepted)
    n_duplicates = len(duplicate_ids)

    # Aggregate by category
    by_category: dict[str, dict] = {}
    total_amount = 0.0
    for row in accepted:
        cat = row["category"]
        if cat not in by_category:
            by_category[cat] = {"count": 0, "total": 0.0}
        by_category[cat]["count"] += 1
        by_category[cat]["total"] = round(by_category[cat]["total"] + row["amount"], 2)
        total_amount += row["amount"]

    total_amount = round(total_amount, 2)

    # Sort categories by total descending
    sorted_cats = sorted(by_category.items(), key=lambda x: x[1]["total"], reverse=True)
    top_category = sorted_cats[0][0] if sorted_cats else ""

    report = {
        "total_rows_extracted": total_extracted,
        "duplicate_count": n_duplicates,
        "duplicate_txn_ids": sorted(set(duplicate_ids)),
        "accepted_count": n_accepted,
        "total_amount": total_amount,
        "top_category": top_category,
        "by_category": {
            cat: {"count": data["count"], "total": data["total"]}
            for cat, data in sorted_cats
        },
    }

    Path("ledger_report.json").write_text(json.dumps(report, indent=2) + "\n")

    # Write reconciliation report
    empty_desc = [r["txn_id"] for r in accepted if not r["description"]]
    lines = [
        "# Acme Technologies Ledger Reconciliation",
        "",
        "## Summary",
        "",
        f"- Rows extracted from PDF: **{total_extracted}**",
        f"- Duplicate transactions removed: **{n_duplicates}** ({', '.join(sorted(set(duplicate_ids)))})",
        f"- Accepted transactions: **{n_accepted}**",
        f"- Total accepted amount: **${total_amount:,.2f}**",
        f"- Top spending category: **{top_category}**",
        "",
        "## Category Breakdown",
        "",
    ]
    for cat, data in sorted_cats:
        lines.append(f"- **{cat}**: {data['count']} transactions, ${data['total']:,.2f}")

    lines += [
        "",
        "## Data Quality Notes",
        "",
    ]
    if empty_desc:
        lines.append(
            f"- {len(empty_desc)} transaction(s) have missing descriptions: {', '.join(empty_desc)}"
        )
    else:
        lines.append("- All transactions have descriptions.")

    lines += [
        f"- Duplicate detection used first-occurrence semantics by txn_id.",
        f"- Removed duplicates: {', '.join(sorted(set(duplicate_ids)))}.",
        "",
        "## Invariant Check",
        "",
        f"- accepted_count ({n_accepted}) + duplicate_count ({n_duplicates}) "
        + f"== total_rows_extracted ({total_extracted}): "
        + ("OK" if n_accepted + n_duplicates == total_extracted else "FAIL"),
        f"- sum(by_category totals) == total_amount: "
        + ("OK" if abs(sum(d['total'] for d in by_category.values()) - total_amount) < 0.02 else "FAIL"),
        "",
    ]

    Path("reconciliation_report.md").write_text("\n".join(lines))
    print(f"Extracted {total_extracted} rows, accepted {n_accepted}, "
          f"duplicates: {sorted(set(duplicate_ids))}")
    print(f"Total: ${total_amount:,.2f}, top category: {top_category}")


if __name__ == "__main__":
    main()

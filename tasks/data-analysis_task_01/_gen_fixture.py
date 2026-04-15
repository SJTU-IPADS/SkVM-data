"""
Deterministic fixture generator for data-analysis_task_03.

Produces fixtures/orders.csv with a seeded mix of valid, pending, returned,
duplicate, out-of-window, bad-date, and bad-amount rows. Prints the expected
reconciliation totals to stdout so the grader knows what the reference
solution must produce.

Run: python3 _gen_fixture.py
Output: fixtures/orders.csv + expected values printed to stdout

Design notes:
- The task targets Q3 2025 (2025-07-01 .. 2025-09-30).
- Every VALID row has status=Completed, return_flag=false, parseable date in
  window, positive numeric amount, and a unique order_id (no collision with
  any other accepted row).
- Duplicate rows share an order_id with an EARLIER row in CSV order. The
  earlier row is the winner (first-occurrence rule).
- Rejection priority (applied in order, only the first matching reason):
  bad_date > bad_amount > pending > returned > out_of_window > duplicate.
- Rows are interleaved (not grouped by category) so a naive agent that
  drops by row index instead of by rule will produce wrong totals.
"""
from __future__ import annotations

import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 20260412
random.seed(SEED)

OUT = Path(__file__).parent / "fixtures" / "orders.csv"

REGIONS = ["north", "south", "east", "west", "central"]
STATUSES_VALID = ["Completed"]
STATUSES_REJECT_PENDING = ["Pending"]

Q3_START = datetime(2025, 7, 1)
Q3_END = datetime(2025, 9, 30, 23, 59, 59)
Q2_START = datetime(2025, 4, 1)
Q2_END = datetime(2025, 6, 30, 23, 59, 59)

N_VALID = 120
N_OUT_OF_WINDOW = 15
N_RETURNED = 10
N_PENDING = 8
N_DUPLICATE = 10
N_BAD_DATE = 9
N_BAD_AMOUNT = 8

TOTAL = N_VALID + N_OUT_OF_WINDOW + N_RETURNED + N_PENDING + N_DUPLICATE + N_BAD_DATE + N_BAD_AMOUNT
assert TOTAL == 180, TOTAL


def rand_date(start: datetime, end: datetime) -> datetime:
    span = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, span))


def next_oid(state: list[int]) -> str:
    state[0] += 1
    return f"ORD-{state[0]:06d}"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    oid_state = [100000]
    customer_ids = [f"CUST-{1000+i:05d}" for i in range(60)]

    rows: list[dict] = []
    tag_counts: dict[str, int] = {}

    def tag(kind: str) -> None:
        tag_counts[kind] = tag_counts.get(kind, 0) + 1

    # Valid rows (will be interleaved with rejects below)
    valid_oids: list[str] = []
    for _ in range(N_VALID):
        oid = next_oid(oid_state)
        valid_oids.append(oid)
        dt = rand_date(Q3_START, Q3_END)
        amount = round(random.uniform(12.50, 980.00), 2)
        rows.append({
            "_kind": "valid",
            "order_id": oid,
            "created_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id": random.choice(customer_ids),
            "region": random.choice(REGIONS),
            "amount": f"{amount:.2f}",
            "status": "Completed",
            "return_flag": "false",
        })
        tag("valid")

    # Out-of-window rows (valid in every other respect but dated in Q2)
    for _ in range(N_OUT_OF_WINDOW):
        oid = next_oid(oid_state)
        dt = rand_date(Q2_START, Q2_END)
        amount = round(random.uniform(15.00, 600.00), 2)
        rows.append({
            "_kind": "out_of_window",
            "order_id": oid,
            "created_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id": random.choice(customer_ids),
            "region": random.choice(REGIONS),
            "amount": f"{amount:.2f}",
            "status": "Completed",
            "return_flag": "false",
        })
        tag("out_of_window")

    # Returned rows (Q3 window, Completed, return_flag=true)
    for _ in range(N_RETURNED):
        oid = next_oid(oid_state)
        dt = rand_date(Q3_START, Q3_END)
        amount = round(random.uniform(15.00, 600.00), 2)
        rows.append({
            "_kind": "returned",
            "order_id": oid,
            "created_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id": random.choice(customer_ids),
            "region": random.choice(REGIONS),
            "amount": f"{amount:.2f}",
            "status": "Completed",
            "return_flag": "true",
        })
        tag("returned")

    # Pending rows (Q3 window, status=Pending)
    for _ in range(N_PENDING):
        oid = next_oid(oid_state)
        dt = rand_date(Q3_START, Q3_END)
        amount = round(random.uniform(15.00, 600.00), 2)
        rows.append({
            "_kind": "pending",
            "order_id": oid,
            "created_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id": random.choice(customer_ids),
            "region": random.choice(REGIONS),
            "amount": f"{amount:.2f}",
            "status": "Pending",
            "return_flag": "false",
        })
        tag("pending")

    # Bad-date rows (Q3-ish data but created_at is garbage)
    BAD_DATES = ["not-a-date", "TBD", "2025-13-45", "", "n/a"]
    for i in range(N_BAD_DATE):
        oid = next_oid(oid_state)
        amount = round(random.uniform(15.00, 600.00), 2)
        rows.append({
            "_kind": "bad_date",
            "order_id": oid,
            "created_at": BAD_DATES[i % len(BAD_DATES)],
            "customer_id": random.choice(customer_ids),
            "region": random.choice(REGIONS),
            "amount": f"{amount:.2f}",
            "status": "Completed",
            "return_flag": "false",
        })
        tag("bad_date")

    # Bad-amount rows (Q3 window, valid in every other way)
    BAD_AMOUNTS = ["TBD", "pending-calc", "n/a", "", "---"]
    for i in range(N_BAD_AMOUNT):
        oid = next_oid(oid_state)
        dt = rand_date(Q3_START, Q3_END)
        rows.append({
            "_kind": "bad_amount",
            "order_id": oid,
            "created_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id": random.choice(customer_ids),
            "region": random.choice(REGIONS),
            "amount": BAD_AMOUNTS[i % len(BAD_AMOUNTS)],
            "status": "Completed",
            "return_flag": "false",
        })
        tag("bad_amount")

    # Duplicate rows — each one collides with a randomly-chosen earlier VALID
    # order_id. Different customer/region/amount to make sure the duplicate
    # detection isn't just a row-identity check.
    dup_targets = random.sample(valid_oids, N_DUPLICATE)
    for oid in dup_targets:
        dt = rand_date(Q3_START, Q3_END)
        amount = round(random.uniform(15.00, 600.00), 2)
        rows.append({
            "_kind": "duplicate",
            "order_id": oid,
            "created_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id": random.choice(customer_ids),
            "region": random.choice(REGIONS),
            "amount": f"{amount:.2f}",
            "status": "Completed",
            "return_flag": "false",
        })
        tag("duplicate")

    # Interleave all rows deterministically
    random.shuffle(rows)

    # Write CSV (strip internal _kind key)
    fieldnames = ["order_id", "created_at", "customer_id", "region", "amount", "status", "return_flag"]
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in fieldnames})

    # Compute expected totals by applying the first-occurrence classifier to
    # the SHUFFLED CSV. This is the authoritative logic grade.py will
    # compare against — not the _kind tags, because a duplicate row that
    # shuffles BEFORE its paired valid row becomes the accepted row under
    # first-occurrence semantics (and the valid row becomes the duplicate
    # rejection). Counts still balance, but sums differ.
    BAD_DATE_SENTINELS = {"not-a-date", "TBD", "2025-13-45", "", "n/a"}
    BAD_AMOUNT_SENTINELS = {"TBD", "pending-calc", "n/a", "", "---"}

    def _classify(row: dict, seen: set[str]) -> str | None:
        created = row["created_at"]
        if created in BAD_DATE_SENTINELS:
            return "bad_date"
        try:
            datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return "bad_date"
        try:
            float(row["amount"])
        except (TypeError, ValueError):
            return "bad_amount"
        if row["status"] == "Pending":
            return "pending"
        if row["return_flag"].strip().lower() == "true":
            return "returned"
        dt_ = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
        if not (Q3_START <= dt_ <= Q3_END):
            return "out_of_window"
        if row["order_id"] in seen:
            return "duplicate"
        return None

    accepted_rows: list[dict] = []
    reject_counts: dict[str, int] = {k: 0 for k in ("bad_date", "bad_amount", "pending", "returned", "out_of_window", "duplicate")}
    seen_oids: set[str] = set()
    for r in rows:
        reason = _classify(r, seen_oids)
        if reason is None:
            accepted_rows.append(r)
            seen_oids.add(r["order_id"])
        else:
            reject_counts[reason] += 1

    total_revenue = round(sum(float(r["amount"]) for r in accepted_rows), 2)

    monthly_revenue: dict[str, float] = {"2025-07": 0.0, "2025-08": 0.0, "2025-09": 0.0}
    region_stats: dict[str, dict] = {}
    customers_seen: set[str] = set()

    for r in accepted_rows:
        dt = datetime.strptime(r["created_at"], "%Y-%m-%d %H:%M:%S")
        month_key = dt.strftime("%Y-%m")
        monthly_revenue[month_key] = round(monthly_revenue[month_key] + float(r["amount"]), 2)
        region = r["region"]
        stats = region_stats.setdefault(region, {"count": 0, "revenue": 0.0})
        stats["count"] += 1
        stats["revenue"] = round(stats["revenue"] + float(r["amount"]), 2)
        customers_seen.add(r["customer_id"])

    top_region_name = max(region_stats, key=lambda k: region_stats[k]["revenue"])
    top_region = {
        "name": top_region_name,
        "count": region_stats[top_region_name]["count"],
        "revenue": region_stats[top_region_name]["revenue"],
    }

    expected = {
        "input_rows": len(rows),
        "accepted": len(accepted_rows),
        "rejected": len(rows) - len(accepted_rows),
        "rejection_reasons": reject_counts,
        "monthly_revenue": monthly_revenue,
        "top_region": top_region,
        "customer_count": len(customers_seen),
        "q3_revenue_total": total_revenue,
    }

    print(json.dumps(expected, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

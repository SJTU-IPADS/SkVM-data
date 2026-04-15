"""
_gen_fixture.py for data-analysis_task_02: A/B Test Experiment Analysis

This script generated fixtures/experiment_log.csv deterministically.
It is committed for reproducibility but NOT re-run at task execution time —
the fixture is a static file.

seed: 20260412

Domain: An e-commerce product team ran a September 2025 A/B test on a new
checkout flow. The raw log contains:
  - clean control users (550)
  - clean treatment users (550)
  - contaminated users appearing in both arms (25 users = 50 rows) — must be excluded
  - out-of-window sessions (18 rows, October 2025) — must be excluded
  - bad-revenue rows (12 rows: converted=True but revenue <= 0) — must be excluded

After exclusions: 1100 valid users, 550 per arm.

Trap archetypes:
  1. Under-specified step (arch 1): device_type segmentation protocol
  2. Common-default-wrong (arch 2): percentages without counts in brief
  3. Known-edge-case (arch 4): multiple comparisons (CVR + ARPU tested simultaneously)
  4. Stateful invariant (arch 5): control_users + treatment_users == valid_users
"""
import csv
import random
import os

random.seed(20260412)

uid_counter = [1000]


def next_uid():
    uid_counter[0] += 1
    return f"U{uid_counter[0]:05d}"


def rand_date_in_window():
    day = random.randint(1, 30)
    return f"2025-09-{day:02d}"


def rand_date_out_of_window():
    day = random.randint(1, 20)
    return f"2025-10-{day:02d}"


# CVRs by arm + device
CVR = {
    ("control", "mobile"): 0.12,
    ("control", "desktop"): 0.18,
    ("treatment", "mobile"): 0.148,
    ("treatment", "desktop"): 0.197,
}
REV_MEAN = {
    ("control", "mobile"): 31.0,
    ("control", "desktop"): 57.0,
    ("treatment", "mobile"): 33.0,
    ("treatment", "desktop"): 59.5,
}

rows = []


def make_clean_row(arm, device):
    uid = next_uid()
    cvr = CVR[(arm, device)]
    converted = random.random() < cvr
    if converted:
        rev = round(REV_MEAN[(arm, device)] + random.gauss(0, REV_MEAN[(arm, device)] * 0.3), 2)
        rev = max(0.01, rev)
    else:
        rev = 0.0
    return {
        "user_id": uid,
        "arm": arm,
        "device_type": device,
        "session_date": rand_date_in_window(),
        "converted": converted,
        "revenue": rev,
    }


# Clean control: 550 users
for _ in range(550):
    dev = "mobile" if random.random() < 0.56 else "desktop"
    rows.append(make_clean_row("control", dev))

# Clean treatment: 550 users
for _ in range(550):
    dev = "mobile" if random.random() < 0.56 else "desktop"
    rows.append(make_clean_row("treatment", dev))

# Contaminated users: 25 users each in both arms (50 rows)
for _ in range(25):
    uid = next_uid()
    dev = "mobile" if random.random() < 0.56 else "desktop"
    rows.append({
        "user_id": uid, "arm": "control", "device_type": dev,
        "session_date": rand_date_in_window(),
        "converted": False, "revenue": 0.0,
    })
    rows.append({
        "user_id": uid, "arm": "treatment", "device_type": dev,
        "session_date": rand_date_in_window(),
        "converted": True, "revenue": round(random.uniform(20, 80), 2),
    })

# Bad date rows: 18 rows (out of window)
for _ in range(18):
    arm = random.choice(["control", "treatment"])
    dev = "mobile" if random.random() < 0.56 else "desktop"
    uid = next_uid()
    rows.append({
        "user_id": uid, "arm": arm, "device_type": dev,
        "session_date": rand_date_out_of_window(),
        "converted": False, "revenue": 0.0,
    })

# Bad revenue rows: 12 rows (converted=True but revenue <= 0)
for i in range(12):
    arm = random.choice(["control", "treatment"])
    dev = "mobile" if random.random() < 0.56 else "desktop"
    uid = next_uid()
    rev = round(-random.uniform(1, 20), 2) if i % 2 == 0 else 0.0
    rows.append({
        "user_id": uid, "arm": arm, "device_type": dev,
        "session_date": rand_date_in_window(),
        "converted": True, "revenue": rev,
    })

# Shuffle
random.shuffle(rows)

os.makedirs("fixtures", exist_ok=True)
with open("fixtures/experiment_log.csv", "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["user_id", "arm", "device_type", "session_date", "converted", "revenue"],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Written {len(rows)} rows to fixtures/experiment_log.csv")

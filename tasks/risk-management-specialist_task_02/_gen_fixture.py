"""
_gen_fixture.py — generates fmea_inventory.csv for risk-management-specialist_task_02.

Run once offline (already done) and commit the static output.
Re-running with the same seed reproduces the exact same file.

Usage:
    python3 _gen_fixture.py            # writes fmea_inventory.csv in cwd
"""
import csv
import random

random.seed(20261117)

ROWS = [
    # (component_id, component, failure_mode, severity, occurrence, detectability,
    #  after_severity, after_occurrence, after_detectability)
    ('C-001', 'Power Supply Unit',   'Voltage spike to patient circuit',              9, 3, 4, 9, 2, 3),
    ('C-002', 'Alarm Module',        'Alarm fails to activate on threshold breach',   8, 2, 7, 8, 2, 4),
    ('C-003', 'Display Unit',        'Incorrect value displayed to operator',          6, 4, 5, 6, 2, 3),
    ('C-004', 'Battery Pack',        'Battery depletes without critical warning',      7, 5, 6, 7, 3, 5),
    ('C-005', 'SW Controller',       'Dose calculation error in edge case',           10, 2, 3, 10, 1, 2),
    ('C-006', 'Pump Actuator',       'Pump delivers wrong flow rate',                  9, 2, 2, 9, 1, 1),
    ('C-007', 'Pressure Sensor',     'Sensor reads 15% above actual pressure',        7, 3, 5, 7, 2, 3),
    ('C-008', 'Catheter Seal',       'Seal rupture during high-pressure delivery',     8, 2, 4, 8, 2, 4),
]

# Shuffle row order to make it non-trivial
random.shuffle(ROWS)

FIELDNAMES = [
    'component_id', 'component', 'failure_mode',
    'severity', 'occurrence', 'detectability',
    'after_severity', 'after_occurrence', 'after_detectability',
]

with open('fmea_inventory.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    for row in ROWS:
        writer.writerow({
            'component_id': row[0],
            'component': row[1],
            'failure_mode': row[2],
            'severity': row[3],
            'occurrence': row[4],
            'detectability': row[5],
            'after_severity': row[6],
            'after_occurrence': row[7],
            'after_detectability': row[8],
        })

print(f"Written {len(ROWS)} rows to fmea_inventory.csv")
print("Post-shuffle order:", [r[0] for r in ROWS])

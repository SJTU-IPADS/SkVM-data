"""
_gen_fixture.py — generates hazard_inventory.csv for risk-management-specialist_task_01.

Run once offline (already done) and commit the static output.
Re-running with the same seed reproduces the exact same file.

Usage:
    python3 _gen_fixture.py            # writes hazard_inventory.csv in cwd
"""
import csv
import random

random.seed(20260412)

# ISO 14971 5x5 risk matrix (from SKILL.md)
MATRIX = {
    ('P5', 'S1'): 'Medium', ('P5', 'S2'): 'High',   ('P5', 'S3'): 'High',         ('P5', 'S4'): 'Unacceptable', ('P5', 'S5'): 'Unacceptable',
    ('P4', 'S1'): 'Medium', ('P4', 'S2'): 'Medium',  ('P4', 'S3'): 'High',         ('P4', 'S4'): 'High',         ('P4', 'S5'): 'Unacceptable',
    ('P3', 'S1'): 'Low',    ('P3', 'S2'): 'Medium',  ('P3', 'S3'): 'Medium',       ('P3', 'S4'): 'High',         ('P3', 'S5'): 'High',
    ('P2', 'S1'): 'Low',    ('P2', 'S2'): 'Low',     ('P2', 'S3'): 'Medium',       ('P2', 'S4'): 'Medium',       ('P2', 'S5'): 'High',
    ('P1', 'S1'): 'Low',    ('P1', 'S2'): 'Low',     ('P1', 'S3'): 'Low',          ('P1', 'S4'): 'Medium',       ('P1', 'S5'): 'Medium',
}

ROWS = [
    ('H-001', 'Electrical shock from exposed terminal contact',   'Electrical', 'P3', 'S4'),
    ('H-002', 'Software incorrect dosage calculation',            'Software',   'P4', 'S5'),
    ('H-003', 'Mechanical entrapment during calibration cycle',   'Mechanical', 'P2', 'S3'),
    ('H-004', 'Biocompatibility reaction from device coating',    'Biological', 'P1', 'S2'),
    ('H-005', 'Thermal burn from heated probe surface',           'Thermal',    'P5', 'S3'),
    ('H-006', 'Radiation overexposure during imaging mode',       'Radiation',  'P2', 'S4'),
    ('H-007', 'User error: incorrect patient data entry',         'Use Error',  'P4', 'S2'),
    ('H-008', 'Battery depletion without warning during procedure', 'Electrical', 'P3', 'S3'),
    ('H-009', 'Chemical leachable from sterilization process',    'Chemical',   'P1', 'S3'),
    ('H-010', 'EMC interference causing display malfunction',     'Environment','P3', 'S2'),
    ('H-011', 'Locking mechanism failure during active use',      'Mechanical', 'P4', 'S4'),
    ('H-012', 'Alarm system failure on patient threshold breach', 'Software',   'P5', 'S4'),
]

# Shuffle order to ensure models don't assume sorted input
random.shuffle(ROWS)

FIELDNAMES = ['hazard_id', 'description', 'hazard_category', 'probability_label', 'severity_label']

with open('hazard_inventory.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    for hid, desc, cat, prob, sev in ROWS:
        writer.writerow({
            'hazard_id': hid,
            'description': desc,
            'hazard_category': cat,
            'probability_label': prob,
            'severity_label': sev,
        })

print(f"Written {len(ROWS)} rows to hazard_inventory.csv")
print("Post-shuffle order:", [r[0] for r in ROWS])

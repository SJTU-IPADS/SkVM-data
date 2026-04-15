"""
Reference solution for risk-management-specialist_task_01.

Reads hazard_inventory.csv from cwd, applies the ISO 14971 5x5 risk matrix
(exact mapping from the task prompt), and produces:
  - risk_register.json (risk register with all fields)
  - risk_summary.md   (markdown risk summary report)
"""
import csv
import json
from collections import Counter
from pathlib import Path

# ISO 14971 5x5 risk matrix — exact mapping from the task prompt
MATRIX = {
    ('P5', 'S1'): 'Medium',       ('P5', 'S2'): 'High',         ('P5', 'S3'): 'High',
    ('P5', 'S4'): 'Unacceptable', ('P5', 'S5'): 'Unacceptable',
    ('P4', 'S1'): 'Medium',       ('P4', 'S2'): 'Medium',       ('P4', 'S3'): 'High',
    ('P4', 'S4'): 'High',         ('P4', 'S5'): 'Unacceptable',
    ('P3', 'S1'): 'Low',          ('P3', 'S2'): 'Medium',       ('P3', 'S3'): 'Medium',
    ('P3', 'S4'): 'High',         ('P3', 'S5'): 'High',
    ('P2', 'S1'): 'Low',          ('P2', 'S2'): 'Low',          ('P2', 'S3'): 'Medium',
    ('P2', 'S4'): 'Medium',       ('P2', 'S5'): 'High',
    ('P1', 'S1'): 'Low',          ('P1', 'S2'): 'Low',          ('P1', 'S3'): 'Low',
    ('P1', 'S4'): 'Medium',       ('P1', 'S5'): 'Medium',
}

ACCEPTABILITY = {
    'Low':          'Accept',
    'Medium':       'ALARP',
    'High':         'Reduce',
    'Unacceptable': 'Redesign',
}

# Control priority: Unacceptable=1, High=1, Medium=2, Low=3
def control_priority(level):
    return 1 if level in ('Unacceptable', 'High') else (2 if level == 'Medium' else 3)


def main():
    ws = Path('.')
    rows = []
    with open(ws / 'hazard_inventory.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    hazards = []
    for row in rows:
        hid = row['hazard_id']
        desc = row['description']
        cat = row['hazard_category']
        prob = row['probability_label']
        sev = row['severity_label']
        level = MATRIX[(prob, sev)]
        acc = ACCEPTABILITY[level]
        cp = control_priority(level)
        hazards.append({
            'hazard_id': hid,
            'description': desc,
            'hazard_category': cat,
            'probability': prob,
            'severity': sev,
            'risk_level': level,
            'acceptability': acc,
            'control_priority': cp,
        })

    level_counts = Counter(h['risk_level'] for h in hazards)
    require_control = sum(1 for h in hazards if h['risk_level'] in ('High', 'Unacceptable'))
    total = len(hazards)

    # Build top-N action plan: hazards requiring control (Unacceptable first, then High)
    # sorted by control_priority asc, then by hazard_id
    action_plan_hazards = sorted(
        [h for h in hazards if h['risk_level'] in ('High', 'Unacceptable')],
        key=lambda h: (h['control_priority'], h['hazard_id'])
    )
    action_plan = []
    for h in action_plan_hazards:
        # Assign control type per ISO 14971 hierarchy
        if h['risk_level'] == 'Unacceptable':
            control_type = 'Inherent Safety by Design'
        else:  # High
            control_type = 'Protective Measures'
        action_plan.append({
            'hazard_id': h['hazard_id'],
            'risk_level': h['risk_level'],
            'control_priority': h['control_priority'],
            'recommended_control_type': control_type,
        })

    output = {
        'total_hazards': total,
        'hazards': hazards,
        'summary': {
            'by_level': {
                'Low': level_counts.get('Low', 0),
                'Medium': level_counts.get('Medium', 0),
                'High': level_counts.get('High', 0),
                'Unacceptable': level_counts.get('Unacceptable', 0),
            },
            'hazards_requiring_control': require_control,
        },
        'action_plan': action_plan,
    }

    (ws / 'risk_register.json').write_text(json.dumps(output, indent=2))
    print(f"Written risk_register.json: {total} hazards, {require_control} requiring control")

    # Write risk_summary.md
    level_order = ['Unacceptable', 'High', 'Medium', 'Low']
    lines = [
        '# Risk Assessment Summary',
        '',
        f'**Total hazards assessed:** {total}',
        f'**Hazards requiring control:** {require_control} (Unacceptable: {level_counts.get("Unacceptable", 0)}, High: {level_counts.get("High", 0)})',
        '',
        '## Risk Level Distribution',
        '',
    ]
    for lvl in level_order:
        cnt = level_counts.get(lvl, 0)
        pct = round(100 * cnt / total, 1)
        lines.append(f'- **{lvl}**: {cnt} of {total} ({pct}%)')
    lines += [
        '',
        '## Action Plan Summary',
        '',
        f'The following {require_control} hazards require immediate risk control measures:',
        '',
    ]
    for item in action_plan:
        lines.append(
            f'- **{item["hazard_id"]}** ({item["risk_level"]}): '
            f'Priority {item["control_priority"]} — {item["recommended_control_type"]}'
        )
    lines += [
        '',
        '## Acceptability Statement',
        '',
        (
            f'Of {total} identified hazards, {level_counts.get("Unacceptable", 0)} are Unacceptable '
            f'and require design changes, {level_counts.get("High", 0)} are High and require risk '
            f'reduction, {level_counts.get("Medium", 0)} are Medium (ALARP review), and '
            f'{level_counts.get("Low", 0)} are Low and acceptable.'
        ),
        '',
        '## Invariant Check',
        '',
        f'Total hazards: {level_counts.get("Low", 0)} + {level_counts.get("Medium", 0)} + '
        f'{level_counts.get("High", 0)} + {level_counts.get("Unacceptable", 0)} = {total}',
    ]
    (ws / 'risk_summary.md').write_text('\n'.join(lines) + '\n')
    print("Written risk_summary.md")


if __name__ == '__main__':
    main()

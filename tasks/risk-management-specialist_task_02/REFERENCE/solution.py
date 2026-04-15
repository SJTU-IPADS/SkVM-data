"""
Reference solution for risk-management-specialist_task_02.

Reads fmea_inventory.csv from cwd, computes RPN = severity × occurrence × detectability
for both initial and after-control values, classifies actions, identifies components
requiring benefit-risk analysis, and produces:
  - fmea_report.json (structured FMEA results)
  - residual_risk_report.md (markdown report covering all three stages)
"""
import csv
import json
from pathlib import Path


def classify_action(rpn: int) -> str:
    """RPN threshold classifications per the task spec."""
    if rpn >= 200:
        return 'Immediate'
    if rpn >= 100:
        return 'High Priority'
    if rpn >= 50:
        return 'Monitor'
    return 'Acceptable'


def main():
    ws = Path('.')
    rows = []
    with open(ws / 'fmea_inventory.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    components = []
    for row in rows:
        s = int(row['severity'])
        o = int(row['occurrence'])
        d = int(row['detectability'])
        as_ = int(row['after_severity'])
        ao = int(row['after_occurrence'])
        ad = int(row['after_detectability'])
        initial_rpn = s * o * d
        residual_rpn = as_ * ao * ad
        components.append({
            'component_id': row['component_id'],
            'component': row['component'],
            'failure_mode': row['failure_mode'],
            'severity': s,
            'occurrence': o,
            'detectability': d,
            'initial_rpn': initial_rpn,
            'initial_action': classify_action(initial_rpn),
            'after_severity': as_,
            'after_occurrence': ao,
            'after_detectability': ad,
            'residual_rpn': residual_rpn,
            'residual_action': classify_action(residual_rpn),
            'benefit_risk_required': classify_action(residual_rpn) in ('Immediate', 'High Priority'),
        })

    # Summary statistics
    total = len(components)
    initial_rpns = [c['initial_rpn'] for c in components]
    max_initial_rpn = max(initial_rpns)
    highest_component = next(c['component'] for c in components if c['initial_rpn'] == max_initial_rpn)

    initial_actions = [c['initial_action'] for c in components]
    action_summary = {
        'Immediate': initial_actions.count('Immediate'),
        'High Priority': initial_actions.count('High Priority'),
        'Monitor': initial_actions.count('Monitor'),
        'Acceptable': initial_actions.count('Acceptable'),
    }

    residual_actions = [c['residual_action'] for c in components]
    residual_summary = {
        'Immediate': residual_actions.count('Immediate'),
        'High Priority': residual_actions.count('High Priority'),
        'Monitor': residual_actions.count('Monitor'),
        'Acceptable': residual_actions.count('Acceptable'),
    }

    benefit_risk_components = [c['component_id'] for c in components if c['benefit_risk_required']]

    output = {
        'total_components': total,
        'components': components,
        'initial_summary': {
            'highest_rpn': max_initial_rpn,
            'highest_rpn_component': highest_component,
            'immediate_action_count': action_summary['Immediate'],
            'by_action': action_summary,
        },
        'residual_summary': {
            'by_action': residual_summary,
            'benefit_risk_required_count': len(benefit_risk_components),
            'benefit_risk_component_ids': benefit_risk_components,
        },
    }

    (ws / 'fmea_report.json').write_text(json.dumps(output, indent=2))
    print(f"Written fmea_report.json: {total} components")
    print(f"  Max initial RPN: {max_initial_rpn} ({highest_component})")
    print(f"  Initial: {action_summary}")
    print(f"  Residual: {residual_summary}")
    print(f"  Benefit-risk required: {benefit_risk_components}")

    # Write residual_risk_report.md
    lines = [
        '# FMEA Residual Risk Report',
        '',
        f'**Total components assessed:** {total}',
        f'**Maximum initial RPN:** {max_initial_rpn} ({highest_component})',
        '',
        '## Initial Risk Assessment',
        '',
        f'- Immediate action (RPN ≥ 200): {action_summary["Immediate"]} of {total}',
        f'- High Priority (100 ≤ RPN < 200): {action_summary["High Priority"]} of {total}',
        f'- Monitor (50 ≤ RPN < 100): {action_summary["Monitor"]} of {total}',
        f'- Acceptable (RPN < 50): {action_summary["Acceptable"]} of {total}',
        '',
        '## Invariant Check',
        '',
        f'Total components: {action_summary["Immediate"]} + {action_summary["High Priority"]} + '
        f'{action_summary["Monitor"]} + {action_summary["Acceptable"]} = {total}',
        '',
        '## Component Detail',
        '',
    ]
    for c in sorted(components, key=lambda x: x['component_id']):
        lines.append(
            f'- **{c["component_id"]}** {c["component"]}: '
            f'Initial RPN={c["initial_rpn"]} ({c["initial_action"]}) → '
            f'Residual RPN={c["residual_rpn"]} ({c["residual_action"]})'
            + (' ⚠ Benefit-risk required' if c['benefit_risk_required'] else '')
        )
    lines += [
        '',
        '## Residual Risk Summary',
        '',
        f'After implementing controls, {residual_summary["Acceptable"]} of {total} components are acceptable.',
        f'Residual Immediate: {residual_summary["Immediate"]}, '
        f'High Priority: {residual_summary["High Priority"]}, '
        f'Monitor: {residual_summary["Monitor"]}.',
        '',
        '## Benefit-Risk Analysis',
        '',
    ]
    if benefit_risk_components:
        lines.append(
            f'**{len(benefit_risk_components)} component(s) require benefit-risk analysis** '
            f'(residual RPN ≥ 100): {", ".join(benefit_risk_components)}.'
        )
        for cid in benefit_risk_components:
            c = next(x for x in components if x['component_id'] == cid)
            lines.append(
                f'- {cid} ({c["component"]}): Residual RPN={c["residual_rpn"]} — '
                f'clinical benefit of device outweighs residual risk given state-of-the-art controls.'
            )
    else:
        lines.append('No components require benefit-risk analysis — all residual risks are Acceptable or Monitor.')
    lines.append('')
    (ws / 'residual_risk_report.md').write_text('\n'.join(lines))
    print("Written residual_risk_report.md")


if __name__ == '__main__':
    main()

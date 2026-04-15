"""
Grade function for risk-management-specialist_task_02.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: direct checks on fmea_report.json and residual_risk_report.md.
Expected values hardcoded from the deterministic fixture (_gen_fixture.py, seed 20261117).

Key traps in this task:
  Archetype 2 (common-default-wrong): RPN = severity × occurrence × detectability uses
    numeric 1-10 scales, NOT ISO 14971 qualitative S1-S5/P1-P5 labels. Agents that apply
    the qualitative risk matrix instead of numeric multiplication get wrong RPN values.
  Archetype 3 (multi-step): initial FMEA + residual RPN + benefit-risk analysis must
    all be present and coherent in one output.
  Archetype 5 (stateful invariant): total_components == sum of all initial action counts;
    benefit_risk_required_count == count of components with residual_action in High Priority/Immediate.

Expected values from the fixture (post-shuffle order C-007, C-008, C-004, C-005, C-006, C-002, C-001, C-003):
  C-001: S=9 O=3 D=4 → RPN=108 (High Priority); residual S=9 O=2 D=3 → 54 (Monitor)
  C-002: S=8 O=2 D=7 → RPN=112 (High Priority); residual S=8 O=2 D=4 → 64 (Monitor)
  C-003: S=6 O=4 D=5 → RPN=120 (High Priority); residual S=6 O=2 D=3 → 36 (Acceptable)
  C-004: S=7 O=5 D=6 → RPN=210 (Immediate);     residual S=7 O=3 D=5 → 105 (High Priority)
  C-005: S=10 O=2 D=3 → RPN=60 (Monitor);       residual S=10 O=1 D=2 → 20 (Acceptable)
  C-006: S=9 O=2 D=2 → RPN=36 (Acceptable);     residual S=9 O=1 D=1 → 9 (Acceptable)
  C-007: S=7 O=3 D=5 → RPN=105 (High Priority); residual S=7 O=2 D=3 → 42 (Acceptable)
  C-008: S=8 O=2 D=4 → RPN=64 (Monitor);        residual S=8 O=2 D=4 → 64 (Monitor)
"""
from __future__ import annotations
import json
import re
from pathlib import Path

# ------ Expected values -------------------------------------------------------

EXPECTED_TOTAL = 8

EXPECTED_INITIAL_RPNS = {
    'C-001': 108,
    'C-002': 112,
    'C-003': 120,
    'C-004': 210,
    'C-005': 60,
    'C-006': 36,
    'C-007': 105,
    'C-008': 64,
}

EXPECTED_RESIDUAL_RPNS = {
    'C-001': 54,
    'C-002': 64,
    'C-003': 36,
    'C-004': 105,
    'C-005': 20,
    'C-006': 9,
    'C-007': 42,
    'C-008': 64,
}

EXPECTED_INITIAL_ACTIONS = {
    'C-001': 'High Priority',
    'C-002': 'High Priority',
    'C-003': 'High Priority',
    'C-004': 'Immediate',
    'C-005': 'Monitor',
    'C-006': 'Acceptable',
    'C-007': 'High Priority',
    'C-008': 'Monitor',
}

EXPECTED_RESIDUAL_ACTIONS = {
    'C-001': 'Monitor',
    'C-002': 'Monitor',
    'C-003': 'Acceptable',
    'C-004': 'High Priority',
    'C-005': 'Acceptable',
    'C-006': 'Acceptable',
    'C-007': 'Acceptable',
    'C-008': 'Monitor',
}

EXPECTED_MAX_RPN = 210
EXPECTED_MAX_COMPONENT = 'Battery Pack'
EXPECTED_IMMEDIATE_COUNT = 1

EXPECTED_INITIAL_BY_ACTION = {
    'Immediate': 1, 'High Priority': 4, 'Monitor': 2, 'Acceptable': 1,
}
EXPECTED_RESIDUAL_BY_ACTION = {
    'Immediate': 0, 'High Priority': 1, 'Monitor': 3, 'Acceptable': 4,
}

EXPECTED_BENEFIT_RISK_IDS = {'C-004'}
EXPECTED_BENEFIT_RISK_COUNT = 1

# ------ Helpers ---------------------------------------------------------------

def _load_json(workspace_path: str):
    path = Path(workspace_path) / 'fmea_report.json'
    if not path.exists():
        return None, 'fmea_report.json not found'
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f'fmea_report.json invalid JSON: {e}'


def _load_md(workspace_path: str):
    path = Path(workspace_path) / 'residual_risk_report.md'
    if not path.exists():
        return None, 'residual_risk_report.md not found'
    return path.read_text(), None


def _get_by_id(data, cid):
    """Find a component entry by component_id."""
    for c in data.get('components', []):
        if isinstance(c, dict) and c.get('component_id') == cid:
            return c
    return None


# ------ Per-criterion checks --------------------------------------------------

def _check_json_exists(data, md):
    if data is None:
        return 0.0, 'fmea_report.json missing or unparseable'
    return 1.0, None


def _check_json_schema(data, md):
    if data is None:
        return 0.0, 'fmea_report.json missing'
    required = {'total_components', 'components', 'initial_summary', 'residual_summary'}
    missing = required - set(data.keys())
    if missing:
        return 0.0, f'Missing top-level keys: {sorted(missing)}'
    init_required = {'highest_rpn', 'highest_rpn_component', 'immediate_action_count'}
    init_missing = init_required - set(data.get('initial_summary', {}).keys())
    if init_missing:
        return 0.0, f'initial_summary missing: {sorted(init_missing)}'
    res_required = {'benefit_risk_required_count', 'benefit_risk_component_ids'}
    res_missing = res_required - set(data.get('residual_summary', {}).keys())
    if res_missing:
        return 0.0, f'residual_summary missing: {sorted(res_missing)}'
    return 1.0, None


def _check_total_components(data, md):
    if data is None:
        return 0.0, 'fmea_report.json missing'
    got = data.get('total_components')
    if got != EXPECTED_TOTAL:
        return 0.0, f'total_components: expected {EXPECTED_TOTAL}, got {got}'
    return 1.0, None


def _check_component_fields(data, md):
    if data is None:
        return 0.0, 'fmea_report.json missing'
    components = data.get('components', [])
    if not isinstance(components, list) or len(components) == 0:
        return 0.0, 'components is not a non-empty list'
    required = {'component_id', 'initial_rpn', 'initial_action', 'residual_rpn', 'residual_action', 'benefit_risk_required'}
    problems = []
    for c in components:
        if not isinstance(c, dict):
            problems.append('entry is not a dict')
            continue
        missing = required - set(c.keys())
        if missing:
            problems.append(f'{c.get("component_id","?")}: missing {sorted(missing)}')
    if problems:
        return 0.0, '; '.join(problems[:3])
    return 1.0, None


def _check_initial_rpn_calculation(data, md):
    """initial_rpn must be the numeric product severity × occurrence × detectability (not ISO qualitative lookup)."""
    if data is None:
        return 0.0, 'fmea_report.json missing'
    wrongs = []
    for cid, expected_rpn in EXPECTED_INITIAL_RPNS.items():
        c = _get_by_id(data, cid)
        if c is None:
            wrongs.append(f'{cid}: component not found')
            continue
        got = c.get('initial_rpn')
        try:
            got_int = int(got)
        except (TypeError, ValueError):
            wrongs.append(f'{cid}: initial_rpn not integer: {got!r}')
            continue
        if got_int != expected_rpn:
            wrongs.append(f'{cid}: expected initial_rpn={expected_rpn}, got {got_int}')
    if wrongs:
        return 0.0, '; '.join(wrongs[:5])
    return 1.0, None


def _check_initial_action_classification(data, md):
    """initial_action thresholds: ≥200=Immediate, 100-199=High Priority, 50-99=Monitor, <50=Acceptable."""
    if data is None:
        return 0.0, 'fmea_report.json missing'
    wrongs = []
    for cid, expected_action in EXPECTED_INITIAL_ACTIONS.items():
        c = _get_by_id(data, cid)
        if c is None:
            continue
        got = c.get('initial_action')
        if got != expected_action:
            wrongs.append(f'{cid}: expected {expected_action!r}, got {got!r} (initial_rpn={EXPECTED_INITIAL_RPNS[cid]})')
    if wrongs:
        return 0.0, '; '.join(wrongs[:5])
    return 1.0, None


def _check_residual_rpn_calculation(data, md):
    """residual_rpn = after_severity × after_occurrence × after_detectability (numeric multiplication)."""
    if data is None:
        return 0.0, 'fmea_report.json missing'
    wrongs = []
    for cid, expected_rpn in EXPECTED_RESIDUAL_RPNS.items():
        c = _get_by_id(data, cid)
        if c is None:
            wrongs.append(f'{cid}: component not found')
            continue
        got = c.get('residual_rpn')
        try:
            got_int = int(got)
        except (TypeError, ValueError):
            wrongs.append(f'{cid}: residual_rpn not integer: {got!r}')
            continue
        if got_int != expected_rpn:
            wrongs.append(f'{cid}: expected residual_rpn={expected_rpn}, got {got_int}')
    if wrongs:
        return 0.0, '; '.join(wrongs[:5])
    return 1.0, None


def _check_residual_action_classification(data, md):
    """residual_action must apply the same RPN thresholds to the after-control values."""
    if data is None:
        return 0.0, 'fmea_report.json missing'
    wrongs = []
    for cid, expected_action in EXPECTED_RESIDUAL_ACTIONS.items():
        c = _get_by_id(data, cid)
        if c is None:
            continue
        got = c.get('residual_action')
        if got != expected_action:
            wrongs.append(f'{cid}: expected residual_action={expected_action!r}, got {got!r} (residual_rpn={EXPECTED_RESIDUAL_RPNS[cid]})')
    if wrongs:
        return 0.0, '; '.join(wrongs[:5])
    return 1.0, None


def _check_initial_summary(data, md):
    """initial_summary: highest_rpn=210 (Battery Pack), immediate_action_count=1."""
    if data is None:
        return 0.0, 'fmea_report.json missing'
    s = data.get('initial_summary', {})
    problems = []
    if s.get('highest_rpn') != EXPECTED_MAX_RPN:
        problems.append(f'highest_rpn: expected {EXPECTED_MAX_RPN}, got {s.get("highest_rpn")!r}')
    if s.get('highest_rpn_component') != EXPECTED_MAX_COMPONENT:
        problems.append(f'highest_rpn_component: expected {EXPECTED_MAX_COMPONENT!r}, got {s.get("highest_rpn_component")!r}')
    if s.get('immediate_action_count') != EXPECTED_IMMEDIATE_COUNT:
        problems.append(f'immediate_action_count: expected {EXPECTED_IMMEDIATE_COUNT}, got {s.get("immediate_action_count")!r}')
    if problems:
        return 0.0, '; '.join(problems)
    return 1.0, None


def _check_count_invariant(data, md):
    """Stateful invariant: total_components == Immediate + High Priority + Monitor + Acceptable."""
    if data is None:
        return 0.0, 'fmea_report.json missing'
    total = data.get('total_components')
    by_action = data.get('initial_summary', {}).get('by_action', {})
    if not isinstance(by_action, dict):
        return 0.0, 'initial_summary.by_action is not an object'
    try:
        action_sum = sum(int(v) for v in by_action.values())
    except (TypeError, ValueError):
        return 0.0, 'by_action values not integers'
    try:
        total_int = int(total)
    except (TypeError, ValueError):
        return 0.0, f'total_components not integer: {total!r}'
    if total_int != action_sum:
        return 0.0, f'total_components ({total_int}) != sum of by_action ({action_sum})'
    return 1.0, None


def _check_benefit_risk_identification(data, md):
    """residual_summary must flag C-004 as benefit-risk required (residual_rpn=105, High Priority)."""
    if data is None:
        return 0.0, 'fmea_report.json missing'
    rs = data.get('residual_summary', {})
    count = rs.get('benefit_risk_required_count')
    ids = rs.get('benefit_risk_component_ids', [])
    problems = []
    try:
        count_int = int(count)
    except (TypeError, ValueError):
        problems.append(f'benefit_risk_required_count not integer: {count!r}')
        count_int = -1
    if count_int != EXPECTED_BENEFIT_RISK_COUNT:
        problems.append(f'benefit_risk_required_count: expected {EXPECTED_BENEFIT_RISK_COUNT}, got {count_int}')
    if not isinstance(ids, list):
        problems.append('benefit_risk_component_ids is not a list')
    else:
        got_ids = set(ids)
        missing = EXPECTED_BENEFIT_RISK_IDS - got_ids
        extra = got_ids - EXPECTED_BENEFIT_RISK_IDS
        if missing:
            problems.append(f'missing from benefit_risk_component_ids: {sorted(missing)}')
        if extra:
            problems.append(f'extra (should not require benefit-risk): {sorted(extra)}')
    if problems:
        return 0.0, '; '.join(problems)
    return 1.0, None


def _check_md_exists(data, md):
    if md is None:
        return 0.0, 'residual_risk_report.md missing'
    if len(md.strip()) < 100:
        return 0.0, f'residual_risk_report.md too short ({len(md.strip())} chars)'
    return 1.0, None


def _check_md_benefit_risk_section(data, md):
    """residual_risk_report.md must include a benefit-risk analysis section mentioning C-004."""
    if md is None:
        return 0.0, 'residual_risk_report.md missing'
    text = md.lower()
    # Must mention benefit-risk analysis
    if 'benefit' not in text and 'benefit-risk' not in text:
        return 0.0, 'residual_risk_report.md does not mention benefit-risk analysis'
    # Must mention C-004 (the component requiring benefit-risk)
    if 'C-004' not in md and 'c-004' not in md.lower():
        return 0.0, 'residual_risk_report.md does not name C-004 (the component requiring benefit-risk analysis)'
    return 1.0, None


def _check_md_residual_coverage(data, md):
    """residual_risk_report.md must mention both initial and residual risk levels for components."""
    if md is None:
        return 0.0, 'residual_risk_report.md missing'
    text = md.lower()
    missing = []
    for term in ('initial', 'residual', 'high priority', 'monitor', 'acceptable'):
        if term not in text:
            missing.append(term)
    if missing:
        return 0.0, f'residual_risk_report.md missing expected terms: {missing}'
    return 1.0, None


# ------ Criterion registry ----------------------------------------------------

CRITERIA = [
    {
        'id': 'json-exists',
        'weight': 0.04,
        'description': 'fmea_report.json exists at the workspace root and parses as valid JSON.',
        'check': _check_json_exists,
    },
    {
        'id': 'json-schema',
        'weight': 0.04,
        'description': (
            'fmea_report.json contains all required top-level keys: total_components, components, '
            'initial_summary (with highest_rpn, highest_rpn_component, immediate_action_count), '
            'and residual_summary (with benefit_risk_required_count, benefit_risk_component_ids).'
        ),
        'check': _check_json_schema,
    },
    {
        'id': 'total-components',
        'weight': 0.03,
        'description': 'total_components equals 8 — the number of components in fmea_inventory.csv.',
        'check': _check_total_components,
    },
    {
        'id': 'component-fields',
        'weight': 0.03,
        'description': (
            'Each component entry contains all required fields: component_id, initial_rpn, '
            'initial_action, residual_rpn, residual_action, benefit_risk_required.'
        ),
        'check': _check_component_fields,
    },
    {
        'id': 'initial-rpn-calculation',
        'weight': 0.22,
        'description': (
            'initial_rpn for every component equals severity × occurrence × detectability '
            '(numeric multiplication, 1-10 scale). Trap: agents who apply the ISO 14971 qualitative '
            '5x5 matrix (S1-S5 × P1-P5) instead of numeric multiplication will get wrong RPN values.'
        ),
        'check': _check_initial_rpn_calculation,
    },
    {
        'id': 'initial-action-classification',
        'weight': 0.09,
        'description': (
            'initial_action thresholds: ≥200=Immediate, 100-199=High Priority, 50-99=Monitor, '
            '<50=Acceptable. Common-default-wrong: using "High/Medium/Low" ISO labels instead of '
            'the numeric-RPN action strings.'
        ),
        'check': _check_initial_action_classification,
    },
    {
        'id': 'residual-rpn-calculation',
        'weight': 0.17,
        'description': (
            'residual_rpn equals after_severity × after_occurrence × after_detectability '
            '(the same numeric multiplication applied to post-control scores). '
            'This is the second stage of the multi-step FMEA workflow.'
        ),
        'check': _check_residual_rpn_calculation,
    },
    {
        'id': 'residual-action-classification',
        'weight': 0.06,
        'description': (
            'residual_action applies the same RPN thresholds (≥200/100/50) to the residual_rpn. '
            'C-004 has residual_rpn=105 → High Priority, C-008 has 64 → Monitor, etc.'
        ),
        'check': _check_residual_action_classification,
    },
    {
        'id': 'initial-summary',
        'weight': 0.08,
        'description': (
            'initial_summary reports highest_rpn=210 (Battery Pack) and immediate_action_count=1, '
            'derived from the correct initial RPN calculations.'
        ),
        'check': _check_initial_summary,
    },
    {
        'id': 'count-invariant',
        'weight': 0.04,
        'description': (
            'Stateful invariant: total_components (8) equals the sum of all initial action category counts '
            '(Immediate=1 + High Priority=4 + Monitor=2 + Acceptable=1 = 8). '
            'Violated if any component is uncounted or double-counted.'
        ),
        'check': _check_count_invariant,
    },
    {
        'id': 'benefit-risk-identification',
        'weight': 0.11,
        'description': (
            'residual_summary correctly identifies C-004 (Battery Pack, residual_rpn=105, High Priority) '
            'as the only component requiring benefit-risk analysis. '
            'Agents that mis-classify residual RPNs produce wrong benefit-risk sets.'
        ),
        'check': _check_benefit_risk_identification,
    },
    {
        'id': 'md-exists',
        'weight': 0.02,
        'description': 'residual_risk_report.md exists at the workspace root and has non-trivial content.',
        'check': _check_md_exists,
    },
    {
        'id': 'md-benefit-risk-section',
        'weight': 0.04,
        'description': (
            'residual_risk_report.md includes a benefit-risk analysis section that names C-004 '
            'as the component with residual High Priority risk requiring clinical benefit justification.'
        ),
        'check': _check_md_benefit_risk_section,
    },
    {
        'id': 'md-residual-coverage',
        'weight': 0.03,
        'description': (
            'residual_risk_report.md mentions both initial and residual risk levels, using the '
            'correct action label vocabulary (High Priority, Monitor, Acceptable, Immediate).'
        ),
        'check': _check_md_residual_coverage,
    },
]

# Sanity-check weights at import time
_w_sum = sum(c['weight'] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f'CRITERIA weights sum to {_w_sum}, expected 1.0'


def grade(transcript, workspace_path):
    data, _data_err = _load_json(workspace_path)
    md, _md_err = _load_md(workspace_path)

    records = []
    for spec in CRITERIA:
        score, details = spec['check'](data, md)
        record = {
            'id': spec['id'],
            'score': float(score),
            'weight': float(spec['weight']),
            'description': spec['description'],
        }
        if details is not None and score < 1.0:
            record['details'] = details
        records.append(record)
    return records

"""
Grade function for risk-management-specialist_task_01.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: direct checks on risk_register.json and risk_summary.md.
Expected values are computed from the deterministic fixture (_gen_fixture.py, seed 20260412).
grade.py does NOT re-run the fixture generator — the fixture is static.

ISO 14971 5x5 matrix (from SKILL.md):
  P5: S1=Medium, S2=High, S3=High, S4=Unacceptable, S5=Unacceptable
  P4: S1=Medium, S2=Medium, S3=High, S4=High, S5=Unacceptable
  P3: S1=Low, S2=Medium, S3=Medium, S4=High, S5=High
  P2: S1=Low, S2=Low, S3=Medium, S4=Medium, S5=High
  P1: S1=Low, S2=Low, S3=Low, S4=Medium, S5=Medium

Expected values for the post-shuffle fixture:
  H-001: P3 x S4 = High    → Reduce    priority 1
  H-002: P4 x S5 = Unacceptable → Redesign priority 1
  H-003: P2 x S3 = Medium  → ALARP    priority 2
  H-004: P1 x S2 = Low     → Accept   priority 3
  H-005: P5 x S3 = High    → Reduce   priority 1
  H-006: P2 x S4 = Medium  → ALARP    priority 2
  H-007: P4 x S2 = Medium  → ALARP    priority 2
  H-008: P3 x S3 = Medium  → ALARP    priority 2
  H-009: P1 x S3 = Low     → Accept   priority 3
  H-010: P3 x S2 = Medium  → ALARP    priority 2
  H-011: P4 x S4 = High    → Reduce   priority 1
  H-012: P5 x S4 = Unacceptable → Redesign priority 1
"""
from __future__ import annotations
import json
import os
import re
from pathlib import Path

# ------ Expected values -------------------------------------------------------

EXPECTED_TOTAL = 12
EXPECTED_BY_LEVEL = {'Low': 2, 'Medium': 5, 'High': 3, 'Unacceptable': 2}
EXPECTED_REQUIRE_CONTROL = 5  # High + Unacceptable

# Per-hazard expected risk level
EXPECTED_LEVELS = {
    'H-001': 'High',
    'H-002': 'Unacceptable',
    'H-003': 'Medium',
    'H-004': 'Low',
    'H-005': 'High',
    'H-006': 'Medium',
    'H-007': 'Medium',
    'H-008': 'Medium',
    'H-009': 'Low',
    'H-010': 'Medium',
    'H-011': 'High',
    'H-012': 'Unacceptable',
}

EXPECTED_ACCEPTABILITY = {
    'Low': 'Accept',
    'Medium': 'ALARP',
    'High': 'Reduce',
    'Unacceptable': 'Redesign',
}

EXPECTED_CONTROL_PRIORITY = {
    'Unacceptable': 1, 'High': 1, 'Medium': 2, 'Low': 3,
}

# Hazards that must appear in the action plan (risk_level in High or Unacceptable)
EXPECTED_ACTION_HAZARDS = {'H-001', 'H-002', 'H-005', 'H-011', 'H-012'}

# ------ Helpers ---------------------------------------------------------------

def _load_json(workspace_path: str):
    path = Path(workspace_path) / 'risk_register.json'
    if not path.exists():
        return None, 'risk_register.json not found'
    try:
        return json.loads(path.read_text()), None
    except json.JSONDecodeError as e:
        return None, f'risk_register.json invalid JSON: {e}'


def _load_md(workspace_path: str):
    path = Path(workspace_path) / 'risk_summary.md'
    if not path.exists():
        return None, 'risk_summary.md not found'
    return path.read_text(), None


# ------ Per-criterion checks --------------------------------------------------

def _check_json_exists(data, md):
    if data is None:
        return 0.0, 'risk_register.json missing or unparseable'
    return 1.0, None


def _check_json_schema(data, md):
    if data is None:
        return 0.0, 'risk_register.json missing'
    required = {'total_hazards', 'hazards', 'summary', 'action_plan'}
    missing = required - set(data.keys())
    if missing:
        return 0.0, f'Missing top-level keys: {sorted(missing)}'
    summary_required = {'by_level', 'hazards_requiring_control'}
    summary_missing = summary_required - set(data.get('summary', {}).keys())
    if summary_missing:
        return 0.0, f'summary missing keys: {sorted(summary_missing)}'
    return 1.0, None


def _check_total_hazards(data, md):
    if data is None:
        return 0.0, 'risk_register.json missing'
    got = data.get('total_hazards')
    if got != EXPECTED_TOTAL:
        return 0.0, f'total_hazards: expected {EXPECTED_TOTAL}, got {got}'
    return 1.0, None


def _check_hazard_fields(data, md):
    """Each hazard entry must have all required fields."""
    if data is None:
        return 0.0, 'risk_register.json missing'
    hazards = data.get('hazards', [])
    if not isinstance(hazards, list) or len(hazards) == 0:
        return 0.0, 'hazards is not a non-empty list'
    required_fields = {'hazard_id', 'probability', 'severity', 'risk_level', 'acceptability', 'control_priority'}
    problems = []
    for h in hazards:
        if not isinstance(h, dict):
            problems.append('entry is not a dict')
            continue
        missing = required_fields - set(h.keys())
        if missing:
            problems.append(f'{h.get("hazard_id", "?")}: missing {sorted(missing)}')
    if problems:
        return 0.0, '; '.join(problems[:3])
    return 1.0, None


def _check_risk_level_matrix(data, md):
    """risk_level for each hazard must match the ISO 14971 5x5 matrix lookup."""
    if data is None:
        return 0.0, 'risk_register.json missing'
    hazards = data.get('hazards', [])
    wrongs = []
    for h in hazards:
        hid = h.get('hazard_id')
        if hid not in EXPECTED_LEVELS:
            continue
        expected = EXPECTED_LEVELS[hid]
        got = h.get('risk_level')
        if got != expected:
            wrongs.append(f'{hid}: expected {expected}, got {got!r}')
    if wrongs:
        return 0.0, '; '.join(wrongs[:5])
    return 1.0, None


def _check_acceptability_labels(data, md):
    """acceptability must map exactly from risk_level per the task spec."""
    if data is None:
        return 0.0, 'risk_register.json missing'
    hazards = data.get('hazards', [])
    wrongs = []
    for h in hazards:
        hid = h.get('hazard_id', '?')
        level = h.get('risk_level')
        acc = h.get('acceptability')
        if level not in EXPECTED_ACCEPTABILITY:
            continue  # invalid risk level handled elsewhere
        expected_acc = EXPECTED_ACCEPTABILITY[level]
        if acc != expected_acc:
            wrongs.append(f'{hid}: expected acceptability={expected_acc!r}, got {acc!r}')
    if wrongs:
        return 0.0, '; '.join(wrongs[:5])
    return 1.0, None


def _check_control_priority(data, md):
    """control_priority must be 1 for High/Unacceptable, 2 for Medium, 3 for Low."""
    if data is None:
        return 0.0, 'risk_register.json missing'
    hazards = data.get('hazards', [])
    wrongs = []
    for h in hazards:
        hid = h.get('hazard_id', '?')
        level = h.get('risk_level')
        cp = h.get('control_priority')
        if level not in EXPECTED_CONTROL_PRIORITY:
            continue
        expected_cp = EXPECTED_CONTROL_PRIORITY[level]
        try:
            got_cp = int(cp)
        except (TypeError, ValueError):
            wrongs.append(f'{hid}: control_priority not integer: {cp!r}')
            continue
        if got_cp != expected_cp:
            wrongs.append(f'{hid}: expected priority {expected_cp}, got {got_cp} (risk_level={level})')
    if wrongs:
        return 0.0, '; '.join(wrongs[:5])
    return 1.0, None


def _check_by_level_counts(data, md):
    """summary.by_level counts must match the expected distribution from the fixture."""
    if data is None:
        return 0.0, 'risk_register.json missing'
    by_level = data.get('summary', {}).get('by_level', {})
    if not isinstance(by_level, dict):
        return 0.0, 'summary.by_level is not an object'
    problems = []
    for level, expected_count in EXPECTED_BY_LEVEL.items():
        got = by_level.get(level)
        try:
            got_int = int(got)
        except (TypeError, ValueError):
            problems.append(f'{level}: non-integer value {got!r}')
            continue
        if got_int != expected_count:
            problems.append(f'{level}: expected {expected_count}, got {got_int}')
    if problems:
        return 0.0, '; '.join(problems)
    return 1.0, None


def _check_count_invariant(data, md):
    """total_hazards == sum of all by_level counts (stateful invariant)."""
    if data is None:
        return 0.0, 'risk_register.json missing'
    total = data.get('total_hazards')
    by_level = data.get('summary', {}).get('by_level', {})
    if not isinstance(by_level, dict):
        return 0.0, 'summary.by_level not an object'
    try:
        level_sum = sum(int(v) for v in by_level.values())
    except (TypeError, ValueError):
        return 0.0, 'by_level values not integers'
    try:
        total_int = int(total)
    except (TypeError, ValueError):
        return 0.0, f'total_hazards not integer: {total!r}'
    if total_int != level_sum:
        return 0.0, f'total_hazards ({total_int}) != sum of by_level ({level_sum})'
    return 1.0, None


def _check_hazards_requiring_control(data, md):
    """summary.hazards_requiring_control must equal number of High + Unacceptable hazards."""
    if data is None:
        return 0.0, 'risk_register.json missing'
    got = data.get('summary', {}).get('hazards_requiring_control')
    try:
        got_int = int(got)
    except (TypeError, ValueError):
        return 0.0, f'hazards_requiring_control not integer: {got!r}'
    if got_int != EXPECTED_REQUIRE_CONTROL:
        return 0.0, (
            f'hazards_requiring_control: expected {EXPECTED_REQUIRE_CONTROL} '
            f'(High=3 + Unacceptable=2), got {got_int}'
        )
    return 1.0, None


def _check_action_plan_hazards(data, md):
    """action_plan must include all and only High/Unacceptable hazards (5 entries)."""
    if data is None:
        return 0.0, 'risk_register.json missing'
    ap = data.get('action_plan', [])
    if not isinstance(ap, list):
        return 0.0, 'action_plan is not a list'
    ap_ids = {item.get('hazard_id') for item in ap if isinstance(item, dict)}
    missing = EXPECTED_ACTION_HAZARDS - ap_ids
    extra = ap_ids - EXPECTED_ACTION_HAZARDS
    problems = []
    if missing:
        problems.append(f'missing from action_plan: {sorted(missing)}')
    if extra:
        problems.append(f'extra items in action_plan (not High/Unacceptable): {sorted(extra)}')
    if problems:
        return 0.0, '; '.join(problems)
    return 1.0, None


def _check_md_exists(data, md):
    if md is None:
        return 0.0, 'risk_summary.md missing'
    if len(md.strip()) < 100:
        return 0.0, f'risk_summary.md too short ({len(md.strip())} chars)'
    return 1.0, None


def _check_md_level_distribution(data, md):
    """risk_summary.md must state risk level counts for all four levels."""
    if md is None:
        return 0.0, 'risk_summary.md missing'
    text = md.lower()
    missing = []
    for level in ('low', 'medium', 'high', 'unacceptable'):
        if level not in text:
            missing.append(level)
    if missing:
        return 0.0, f'risk_summary.md does not mention levels: {missing}'
    # Check that numbers 2, 5, 3, 2 appear near the level names
    problems = []
    for level, count in [('low', 2), ('medium', 5), ('high', 3), ('unacceptable', 2)]:
        # Look for the count number appearing within 100 chars of the level name
        idx = text.find(level)
        while idx != -1:
            window = text[max(0, idx-20):idx+60]
            if str(count) in window:
                break
            idx = text.find(level, idx + 1)
        else:
            problems.append(f'{level}: count {count} not found near "{level}"')
    if problems:
        return 0.0, 'Level counts not visible in markdown: ' + '; '.join(problems)
    return 1.0, None


def _check_md_invariant_section(data, md):
    """risk_summary.md must contain a section stating total hazards count (12)."""
    if md is None:
        return 0.0, 'risk_summary.md missing'
    # Must mention 12 somewhere meaningful (total hazards)
    if '12' not in md:
        return 0.0, 'risk_summary.md does not mention total hazard count (12)'
    # Must mention the required-control count (5)
    if '5' not in md:
        return 0.0, 'risk_summary.md does not mention hazards requiring control (5)'
    return 1.0, None


# ------ Criterion registry ----------------------------------------------------

CRITERIA = [
    {
        'id': 'json-exists',
        'weight': 0.05,
        'description': 'risk_register.json exists at the workspace root and parses as valid JSON.',
        'check': _check_json_exists,
    },
    {
        'id': 'json-schema',
        'weight': 0.06,
        'description': (
            'risk_register.json contains all required top-level keys: '
            'total_hazards, hazards, summary (with by_level + hazards_requiring_control), and action_plan.'
        ),
        'check': _check_json_schema,
    },
    {
        'id': 'total-hazards',
        'weight': 0.04,
        'description': (
            'total_hazards field equals 12 — the number of rows in hazard_inventory.csv, '
            'proving the agent processed all input rows.'
        ),
        'check': _check_total_hazards,
    },
    {
        'id': 'hazard-fields',
        'weight': 0.04,
        'description': (
            'Each hazard entry in the hazards array contains all required fields: '
            'hazard_id, probability, severity, risk_level, acceptability, control_priority.'
        ),
        'check': _check_hazard_fields,
    },
    {
        'id': 'risk-level-matrix',
        'weight': 0.22,
        'description': (
            'risk_level for every hazard matches the ISO 14971 5x5 matrix lookup '
            '(probability x severity → Low/Medium/High/Unacceptable). '
            'Trap: the matrix is asymmetric — (P4,S3)=High, (P3,S4)=High, (P2,S4)=Medium differ from naive P×S arithmetic.'
        ),
        'check': _check_risk_level_matrix,
    },
    {
        'id': 'acceptability-labels',
        'weight': 0.10,
        'description': (
            'acceptability field maps exactly from risk_level per the task spec: '
            'Low→Accept, Medium→ALARP, High→Reduce, Unacceptable→Redesign. '
            'Common wrong default: using "Acceptable" instead of "Accept", or "Reduce" for Medium.'
        ),
        'check': _check_acceptability_labels,
    },
    {
        'id': 'control-priority',
        'weight': 0.10,
        'description': (
            'control_priority is 1 for High and Unacceptable hazards, 2 for Medium, 3 for Low. '
            'Both High and Unacceptable share priority 1 — agents often assign Unacceptable=0 or a separate tier.'
        ),
        'check': _check_control_priority,
    },
    {
        'id': 'by-level-counts',
        'weight': 0.12,
        'description': (
            'summary.by_level counts are Low=2, Medium=5, High=3, Unacceptable=2 — '
            'the exact distribution produced by the pinned ISO 14971 matrix for this fixture. '
            'Wrong matrix lookups cascade into wrong counts.'
        ),
        'check': _check_by_level_counts,
    },
    {
        'id': 'count-invariant',
        'weight': 0.04,
        'description': (
            'Stateful invariant: total_hazards (12) equals the sum of all by_level counts '
            '(Low + Medium + High + Unacceptable = 12). Violated if any hazard is double-counted or dropped.'
        ),
        'check': _check_count_invariant,
    },
    {
        'id': 'hazards-requiring-control',
        'weight': 0.07,  # intentional - this is the multi-step coordination check
        'description': (
            'summary.hazards_requiring_control equals 5 — the count of High (3) and Unacceptable (2) hazards. '
            'Models that mis-classify matrix cells produce a different count here.'
        ),
        'check': _check_hazards_requiring_control,
    },
    {
        'id': 'action-plan-hazards',
        'weight': 0.08,
        'description': (
            'action_plan includes exactly the 5 High/Unacceptable hazards '
            '(H-001, H-002, H-005, H-011, H-012) and no others — '
            'verifying that the multi-step workflow (register → action plan) is coherent.'
        ),
        'check': _check_action_plan_hazards,
    },
    {
        'id': 'md-exists',
        'weight': 0.02,
        'description': 'risk_summary.md exists at the workspace root and has non-trivial content.',
        'check': _check_md_exists,
    },
    {
        'id': 'md-level-distribution',
        'weight': 0.04,
        'description': (
            'risk_summary.md states the risk level distribution with all four levels '
            'and their correct counts (Low=2, Medium=5, High=3, Unacceptable=2).'
        ),
        'check': _check_md_level_distribution,
    },
    {
        'id': 'md-invariant-section',
        'weight': 0.02,
        'description': (
            'risk_summary.md mentions the total hazard count (12) and the number '
            'requiring control (5) — ensuring the report is consistent with the register.'
        ),
        'check': _check_md_invariant_section,
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

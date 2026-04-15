"""
Grade function for calendar_task_02.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: parse executive_calendar.ics from the workspace, then check
each constraint independently.

Context:
  Reference date = Tuesday, April 14, 2026.
  "Next Tuesday" from Tuesday → April 21, 2026 (FOLLOWING Tuesday per
    SKILL.md: 'If today is Tuesday, next Tuesday means the following Tuesday').
  Team Sync: DTSTART=20260421T150000Z, DTEND=20260421T154500Z (45-min),
    RRULE:FREQ=MONTHLY;COUNT=6, attendees frank + grace.
  Budget Review: DTSTART=20260428T110000Z, DTEND=20260428T130000Z (2 hours,
    ending by 1 PM UTC constraint), attendee frank, has DESCRIPTION.
  Work Anniversary (Heidi): all-day event on 20260501, using DATE value type
    (DTSTART;VALUE=DATE:20260501, not a datetime with T and Z).
"""
from __future__ import annotations

import re
from pathlib import Path


def _load_ics(workspace_path: str):
    """Return (raw_text, error_str). error_str is None on success."""
    p = Path(workspace_path) / "executive_calendar.ics"
    if not p.exists():
        return None, "executive_calendar.ics not found in workspace"
    return p.read_text(), None


def _parse_vevents(text: str) -> list[dict]:
    """Parse all VEVENT blocks into dicts of {FIELD_BASE: [value, ...]}."""
    events = []
    in_event = False
    current: dict[str, list[str]] = {}
    raw_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == "BEGIN:VEVENT":
            in_event = True
            current = {}
            raw_lines = []
        elif line == "END:VEVENT":
            if in_event:
                current["_raw"] = raw_lines[:]
                events.append(current)
            in_event = False
            current = {}
            raw_lines = []
        elif in_event:
            raw_lines.append(line)
            if ":" in line:
                key, _, val = line.partition(":")
                # Normalize: keep the full key for special handling
                key_upper = key.upper()
                key_base = key_upper.split(";")[0]
                current.setdefault(key_base, [])
                current[key_base].append(val)
                # Also store full key for VALUE=DATE detection
                current.setdefault("_fullkeys", [])
                current["_fullkeys"].append(key_upper)
    return events


def _find_event(events: list[dict], summary_pattern: str) -> dict | None:
    pat = re.compile(summary_pattern, re.IGNORECASE)
    for ev in events:
        summaries = ev.get("SUMMARY", [])
        if any(pat.search(s) for s in summaries):
            return ev
    return None


def _dtstart_raw(ev: dict) -> str | None:
    vals = ev.get("DTSTART", [])
    return vals[0] if vals else None


def _dtend_raw(ev: dict) -> str | None:
    vals = ev.get("DTEND", [])
    return vals[0] if vals else None


def _attendee_emails(ev: dict) -> set[str]:
    result = set()
    for line in ev.get("ATTENDEE", []):
        m = re.search(r"mailto:(\S+)", line, re.IGNORECASE)
        if m:
            result.add(m.group(1).lower())
    return result


def _has_rrule_field(ev: dict, field: str, value: str) -> bool:
    for rrule in ev.get("RRULE", []):
        parts = dict(p.split("=", 1) for p in rrule.split(";") if "=" in p)
        if parts.get(field.upper(), "").upper() == value.upper():
            return True
    return False


def _is_date_only(ev: dict, field: str = "DTSTART") -> bool:
    """Return True if the DTSTART or DTEND uses VALUE=DATE (all-day format)."""
    raw_lines = ev.get("_raw", [])
    for line in raw_lines:
        if line.upper().startswith(field.upper()):
            return "VALUE=DATE" in line.upper()
    return False


# ---- Individual criterion checks ------------------------------------------

def _check_file_exists(ics, events):
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    return 1.0, None


def _check_vcalendar_structure(ics, events):
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    if "BEGIN:VCALENDAR" not in ics or "END:VCALENDAR" not in ics:
        return 0.0, "Missing BEGIN:VCALENDAR / END:VCALENDAR wrapper"
    if "VERSION:2.0" not in ics:
        return 0.0, "Missing VERSION:2.0 in VCALENDAR"
    return 1.0, None


def _check_three_vevents(ics, events):
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    if len(events) < 3:
        return 0.0, f"Expected at least 3 VEVENT blocks, found {len(events)}"
    return 1.0, None


def _check_team_sync_date(ics, events):
    """Team Sync must start on April 21, 2026 — the FOLLOWING Tuesday from
    the reference date Tuesday April 14. SKILL.md rule: 'If today is Tuesday,
    next Tuesday means the following Tuesday.'"""
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    ev = _find_event(events, r"team\s*sync")
    if ev is None:
        return 0.0, "No VEVENT with SUMMARY matching 'Team Sync' found"
    dtstart = _dtstart_raw(ev)
    if dtstart is None:
        return 0.0, "Team Sync VEVENT has no DTSTART"
    if not dtstart.startswith("20260421"):
        return 0.0, (
            f"Team Sync DTSTART date should be 20260421 (April 21 — next Tuesday "
            f"from Tuesday April 14, which per SKILL.md means the FOLLOWING Tuesday); "
            f"got {dtstart!r}"
        )
    return 1.0, None


def _check_team_sync_time_and_duration(ics, events):
    """Team Sync must be at 3:00 PM UTC (T150000Z) and last 45 minutes (DTEND T154500Z)."""
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    ev = _find_event(events, r"team\s*sync")
    if ev is None:
        return 0.0, "No Team Sync event found"
    dtstart = _dtstart_raw(ev)
    if dtstart is None or "T150000Z" not in dtstart:
        return 0.0, (
            f"Team Sync DTSTART should be 3:00 PM UTC (T150000Z); got {dtstart!r}"
        )
    dtend = _dtend_raw(ev)
    if dtend is None or "T154500Z" not in dtend:
        return 0.0, (
            f"Team Sync DTEND should be 3:45 PM UTC (T154500Z, 45-minute meeting); "
            f"got {dtend!r}"
        )
    return 1.0, None


def _check_team_sync_rrule(ics, events):
    """Team Sync must have RRULE:FREQ=MONTHLY;COUNT=6."""
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    ev = _find_event(events, r"team\s*sync")
    if ev is None:
        return 0.0, "No Team Sync event found"
    if not ev.get("RRULE"):
        return 0.0, "Team Sync VEVENT has no RRULE"
    if not _has_rrule_field(ev, "FREQ", "MONTHLY"):
        return 0.0, f"Team Sync RRULE is not FREQ=MONTHLY; got {ev.get('RRULE')}"
    if not _has_rrule_field(ev, "COUNT", "6"):
        return 0.0, f"Team Sync RRULE does not have COUNT=6; got {ev.get('RRULE')}"
    return 1.0, None


def _check_team_sync_attendees(ics, events):
    """Team Sync must have attendees frank@example.com and grace@example.com."""
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    ev = _find_event(events, r"team\s*sync")
    if ev is None:
        return 0.0, "No Team Sync event found"
    emails = _attendee_emails(ev)
    missing = []
    for required in ("frank@example.com", "grace@example.com"):
        if required not in emails:
            missing.append(required)
    if missing:
        return 0.0, f"Team Sync missing attendees: {missing}; found: {sorted(emails)}"
    return 1.0, None


def _check_budget_review_date(ics, events):
    """Budget Review must be on April 28, 2026."""
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    ev = _find_event(events, r"budget\s*review")
    if ev is None:
        return 0.0, "No VEVENT with SUMMARY matching 'Budget Review' found"
    dtstart = _dtstart_raw(ev)
    if dtstart is None:
        return 0.0, "Budget Review has no DTSTART"
    if not dtstart.startswith("20260428"):
        return 0.0, (
            f"Budget Review DTSTART should be April 28, 2026 (20260428); got {dtstart!r}"
        )
    return 1.0, None


def _check_budget_review_end_constraint(ics, events):
    """Budget Review DTEND must not exceed 1:00 PM UTC (T130000Z) because an afternoon
    conference starts then — the meeting must end by that time."""
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    ev = _find_event(events, r"budget\s*review")
    if ev is None:
        return 0.0, "No Budget Review event found"
    dtstart = _dtstart_raw(ev)
    if dtstart is None or "T110000Z" not in dtstart:
        return 0.0, (
            f"Budget Review DTSTART should be 11:00 AM UTC (T110000Z); got {dtstart!r}"
        )
    dtend = _dtend_raw(ev)
    if dtend is None:
        return 0.0, "Budget Review has no DTEND"
    # Extract time portion — must be <= 13:00:00 UTC
    m = re.search(r"T(\d{2})(\d{2})(\d{2})Z?", dtend)
    if not m:
        return 0.0, f"Budget Review DTEND has no parseable time: {dtend!r}"
    h, mi, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
    total_minutes = h * 60 + mi
    if total_minutes > 13 * 60:
        return 0.0, (
            f"Budget Review DTEND {dtend!r} exceeds 1:00 PM UTC constraint "
            f"(afternoon conference conflict)"
        )
    if total_minutes < 11 * 60 + 1:
        return 0.0, (
            f"Budget Review DTEND {dtend!r} is before or equal to DTSTART — "
            f"meeting must have positive duration"
        )
    return 1.0, None


def _check_budget_review_attendee(ics, events):
    """Budget Review must have attendee frank@example.com."""
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    ev = _find_event(events, r"budget\s*review")
    if ev is None:
        return 0.0, "No Budget Review event found"
    emails = _attendee_emails(ev)
    if "frank@example.com" not in emails:
        return 0.0, f"Budget Review missing frank@example.com; found: {sorted(emails)}"
    return 1.0, None


def _check_anniversary_date_only_format(ics, events):
    """The Work Anniversary must use the all-day DATE format (DTSTART;VALUE=DATE:20260501)
    rather than datetime format. All-day events must not carry a time component or Z suffix —
    using YYYYMMDDTHHMMSSZ for an all-day event misrepresents the event duration."""
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    ev = _find_event(events, r"(anniversary|heidi)")
    if ev is None:
        return 0.0, "No VEVENT with SUMMARY matching anniversary or 'Heidi' found"
    # Check DTSTART is on May 1, 2026
    dtstart = _dtstart_raw(ev)
    if dtstart is None:
        return 0.0, "Anniversary event has no DTSTART"
    # Date must include 20260501
    if "20260501" not in dtstart:
        return 0.0, (
            f"Work Anniversary DTSTART should be on May 1, 2026 (20260501); got {dtstart!r}"
        )
    # Must be DATE-only format (no T time component, no Z)
    if "T" in dtstart:
        return 0.0, (
            f"Work Anniversary should use all-day DATE format (DTSTART;VALUE=DATE:20260501), "
            f"not datetime format; got {dtstart!r} which includes a time component"
        )
    # Verify VALUE=DATE appears in the raw line
    if not _is_date_only(ev, "DTSTART"):
        return 0.0, (
            f"Work Anniversary DTSTART must use VALUE=DATE type parameter "
            f"(DTSTART;VALUE=DATE:20260501); got {dtstart!r}"
        )
    return 1.0, None


def _check_all_datetime_events_utc(ics, events):
    """All VEVENT entries with datetime (not all-day) DTSTART/DTEND must use UTC 'Z' suffix —
    omitting Z creates floating-time events that calendar apps interpret in local time, causing
    scheduling errors for distributed teams."""
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    violations = []
    for ev in events:
        for field in ("DTSTART", "DTEND"):
            for val in ev.get(field, []):
                # Skip DATE-only values (no T component)
                if "T" in val and not val.endswith("Z"):
                    summary = (ev.get("SUMMARY") or ["event"])[0]
                    violations.append(f"{summary}: {field}={val!r}")
    if violations:
        return 0.0, (
            f"Non-UTC datetime(s) found — all datetime DTSTART/DTEND must end with 'Z'; "
            f"violations: {'; '.join(violations[:3])}"
        )
    return 1.0, None


def _check_unique_uids(ics, events):
    """Each VEVENT must have a unique UID to prevent calendar clients from merging or
    dropping events when multiple events share an identifier."""
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    uids = []
    for ev in events:
        uid_vals = ev.get("UID", [])
        uids.extend(uid_vals)
    if not uids:
        return 0.0, "No UIDs found in any VEVENT"
    if len(set(uids)) < len(events):
        return 0.0, f"Duplicate or missing UIDs across {len(events)} events; found: {uids}"
    return 1.0, None


def _check_budget_description(ics, events):
    """Budget Review must have a DESCRIPTION field documenting the end-time constraint
    — the description conveys the scheduling context so attendees understand the constraint."""
    if ics is None:
        return 0.0, "executive_calendar.ics not found"
    ev = _find_event(events, r"budget\s*review")
    if ev is None:
        return 0.0, "No Budget Review event found"
    desc_vals = ev.get("DESCRIPTION", [])
    if not desc_vals:
        return 0.0, "Budget Review VEVENT has no DESCRIPTION field"
    desc = " ".join(desc_vals).lower()
    # Must mention the time constraint (1 PM / 13:00 / afternoon / conference)
    if not any(kw in desc for kw in ("1 pm", "13:00", "afternoon", "conference", "constraint", "must end")):
        return 0.0, (
            f"Budget Review DESCRIPTION does not mention the end-time constraint "
            f"(1 PM UTC / afternoon conference); got: {desc[:120]!r}"
        )
    return 1.0, None


# ---- Criterion registry ----------------------------------------------------

CRITERIA = [
    {
        "id": "file-exists",
        "weight": 0.05,
        "description": "executive_calendar.ics exists at the workspace root.",
        "check": _check_file_exists,
    },
    {
        "id": "vcalendar-structure",
        "weight": 0.04,
        "description": "executive_calendar.ics has the required BEGIN:VCALENDAR / END:VCALENDAR wrapper and VERSION:2.0 property.",
        "check": _check_vcalendar_structure,
    },
    {
        "id": "three-vevents",
        "weight": 0.04,
        "description": "The .ics file contains at least 3 VEVENT blocks — one per scheduled item (Team Sync, Budget Review, Work Anniversary).",
        "check": _check_three_vevents,
    },
    {
        "id": "team-sync-date",
        "weight": 0.14,
        "description": "Team Sync DTSTART falls on April 21, 2026 — the FOLLOWING Tuesday from the reference date Tuesday April 14. Per SKILL.md: 'If today is Tuesday, next Tuesday means the following Tuesday' — not the same day.",
        "check": _check_team_sync_date,
    },
    {
        "id": "team-sync-time-duration",
        "weight": 0.08,
        "description": "Team Sync DTSTART is 3:00 PM UTC (T150000Z) and DTEND is 3:45 PM UTC (T154500Z), reflecting the 45-minute duration in UTC.",
        "check": _check_team_sync_time_and_duration,
    },
    {
        "id": "team-sync-rrule",
        "weight": 0.10,
        "description": "Team Sync has RRULE:FREQ=MONTHLY;COUNT=6, creating 6 monthly occurrences — not a one-time event and not weekly.",
        "check": _check_team_sync_rrule,
    },
    {
        "id": "team-sync-attendees",
        "weight": 0.07,
        "description": "Team Sync VEVENT lists both frank@example.com and grace@example.com as ATTENDEE entries.",
        "check": _check_team_sync_attendees,
    },
    {
        "id": "budget-review-date",
        "weight": 0.06,
        "description": "Budget Review DTSTART date is April 28, 2026 (20260428).",
        "check": _check_budget_review_date,
    },
    {
        "id": "budget-review-end-constraint",
        "weight": 0.11,
        "description": "Budget Review DTSTART is 11:00 AM UTC and DTEND does not exceed 1:00 PM UTC (T130000Z) — the afternoon conference starts at 1 PM and the meeting must end before it.",
        "check": _check_budget_review_end_constraint,
    },
    {
        "id": "budget-review-attendee",
        "weight": 0.04,
        "description": "Budget Review VEVENT lists frank@example.com as an ATTENDEE entry.",
        "check": _check_budget_review_attendee,
    },
    {
        "id": "budget-review-description",
        "weight": 0.04,
        "description": "Budget Review VEVENT has a DESCRIPTION field that mentions the end-time constraint (1 PM, afternoon, or conference), so attendees understand why the meeting must end by 1 PM UTC.",
        "check": _check_budget_description,
    },
    {
        "id": "anniversary-date-only-format",
        "weight": 0.10,
        "description": "Heidi's Work Anniversary uses all-day DATE format (DTSTART;VALUE=DATE:20260501) without a time component or Z suffix — using YYYYMMDDTHHMMSSZ for an all-day event is the common-default-wrong failure for all-day events in iCalendar.",
        "check": _check_anniversary_date_only_format,
    },
    {
        "id": "all-datetime-events-utc",
        "weight": 0.08,
        "description": "All VEVENTs with datetime (not all-day) DTSTART/DTEND values use the UTC 'Z' suffix — omitting Z creates floating-time events that appear at wrong times for distributed teams.",
        "check": _check_all_datetime_events_utc,
    },
    {
        "id": "unique-uids",
        "weight": 0.03,
        "description": "Each VEVENT has a unique UID field, preventing calendar clients from merging or dropping events.",
        "check": _check_unique_uids,
    },
    {
        "id": "anniversary-date",
        "weight": 0.02,
        "description": "Heidi's Work Anniversary is scheduled on May 1, 2026 (20260501), not any other date.",
        "check": lambda ics, events: (
            (1.0, None)
            if (ev := _find_event(events, r"(anniversary|heidi)")) and "20260501" in (_dtstart_raw(ev) or "")
            else (0.0, "Anniversary not on 20260501")
        ),
    },
]

# Validate weight sum at import time.
_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    ics, _err = _load_ics(workspace_path)
    events = _parse_vevents(ics) if ics else []

    records = []
    for spec in CRITERIA:
        score, details = spec["check"](ics, events)
        record = {
            "id": spec["id"],
            "score": float(score),
            "weight": float(spec["weight"]),
            "description": spec["description"],
        }
        if details is not None and score < 1.0:
            record["details"] = details
        records.append(record)
    return records

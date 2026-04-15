"""
Grade function for calendar_task_01.

Contract: returns a list of criterion records per grade-py-protocol.md.
Each record: {id, score in [0,1], weight (sum to 1.0), description, details?}.

Strategy: parse team_schedule.ics from the workspace using Python's standard
ics library or manual parsing, then check each constraint independently.

Expected artifacts:
  - team_schedule.ics at workspace root

Context:
  Reference date = Wednesday, April 15, 2026.
  "Next Wednesday" from Wednesday → April 22, 2026 (following Wednesday, per
    the SKILL.md rule: "If today is X, 'next X' means the following X").
  "Upcoming Monday" from Wednesday April 15 → April 20, 2026.
  Sprint Planning: DTSTART=20260422T100000Z, DTEND=20260422T110000Z,
    RRULE:FREQ=WEEKLY;COUNT=10, attendees alice + bob.
  Design Review: DTSTART=20260420T140000Z, DTEND=20260420T153000Z,
    LOCATION=Conference Room B, attendee carol.
  Quarterly Kickoff: DTSTART=20260430T090000Z, DTEND=20260430T110000Z,
    attendees alice + dave + eve.
"""
from __future__ import annotations

import os
import re
from pathlib import Path


def _load_ics(workspace_path: str):
    """Return (raw_text, error_str). error_str is None on success."""
    p = Path(workspace_path) / "team_schedule.ics"
    if not p.exists():
        return None, "team_schedule.ics not found in workspace"
    return p.read_text(), None


def _parse_vevents(text: str) -> list[dict]:
    """Parse all VEVENT blocks into dicts of {FIELD: [value, ...]}."""
    events = []
    in_event = False
    current: dict[str, list[str]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == "BEGIN:VEVENT":
            in_event = True
            current = {}
        elif line == "END:VEVENT":
            if in_event:
                events.append(current)
            in_event = False
            current = {}
        elif in_event:
            if ":" in line:
                key, _, val = line.partition(":")
                key_base = key.split(";")[0].upper()  # strip parameters like CN=
                current.setdefault(key_base, [])
                current[key_base].append(val)
    return events


def _find_event(events: list[dict], summary_pattern: str) -> dict | None:
    """Return first event whose SUMMARY matches the pattern (case-insensitive)."""
    pat = re.compile(summary_pattern, re.IGNORECASE)
    for ev in events:
        summaries = ev.get("SUMMARY", [])
        if any(pat.search(s) for s in summaries):
            return ev
    return None


def _dtstart(ev: dict) -> str | None:
    vals = ev.get("DTSTART", [])
    return vals[0] if vals else None


def _dtend(ev: dict) -> str | None:
    vals = ev.get("DTEND", [])
    return vals[0] if vals else None


def _attendee_emails(ev: dict) -> set[str]:
    """Extract all mailto: email addresses from ATTENDEE lines."""
    result = set()
    for line in ev.get("ATTENDEE", []):
        m = re.search(r"mailto:(\S+)", line, re.IGNORECASE)
        if m:
            result.add(m.group(1).lower())
    return result


def _has_rrule_field(ev: dict, field: str, value: str) -> bool:
    """Check if any RRULE value contains 'FIELD=VALUE' (case-insensitive)."""
    for rrule in ev.get("RRULE", []):
        parts = dict(p.split("=", 1) for p in rrule.split(";") if "=" in p)
        if parts.get(field.upper(), "").upper() == value.upper():
            return True
    return False


# ---- Individual criterion checks ------------------------------------------

def _check_file_exists(ics, events):
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    return 1.0, None


def _check_vcalendar_structure(ics, events):
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    if "BEGIN:VCALENDAR" not in ics or "END:VCALENDAR" not in ics:
        return 0.0, "Missing BEGIN:VCALENDAR / END:VCALENDAR wrapper"
    if "VERSION:2.0" not in ics:
        return 0.0, "Missing VERSION:2.0 in VCALENDAR"
    return 1.0, None


def _check_three_vevents(ics, events):
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    if len(events) < 3:
        return 0.0, f"Expected at least 3 VEVENT blocks, found {len(events)}"
    return 1.0, None


def _check_sprint_planning_date(ics, events):
    """Sprint Planning must start on April 22, 2026 (next Wednesday from Wednesday April 15).
    Per SKILL.md: if today is Wednesday, 'next Wednesday' means the FOLLOWING Wednesday."""
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    ev = _find_event(events, r"sprint\s*planning")
    if ev is None:
        return 0.0, "No VEVENT with SUMMARY matching 'Sprint Planning' found"
    dtstart = _dtstart(ev)
    if dtstart is None:
        return 0.0, "Sprint Planning VEVENT has no DTSTART"
    # Must start on April 22, 2026 (date portion 20260422)
    if not dtstart.startswith("20260422"):
        return 0.0, (
            f"Sprint Planning DTSTART date should be 20260422 (April 22 — next Wednesday "
            f"from Wednesday April 15, per SKILL.md 'following' rule); got {dtstart!r}"
        )
    return 1.0, None


def _check_sprint_planning_time_utc(ics, events):
    """Sprint Planning must be at 10:00 AM UTC (T100000Z)."""
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    ev = _find_event(events, r"sprint\s*planning")
    if ev is None:
        return 0.0, "No Sprint Planning event found"
    dtstart = _dtstart(ev)
    if dtstart is None:
        return 0.0, "Sprint Planning has no DTSTART"
    # Accept T100000Z
    if "T100000Z" not in dtstart:
        return 0.0, (
            f"Sprint Planning DTSTART should be 10:00 AM UTC (T100000Z); "
            f"got {dtstart!r}"
        )
    # DTEND must be 1 hour later: T110000Z
    dtend = _dtend(ev)
    if dtend is None or "T110000Z" not in dtend:
        return 0.0, (
            f"Sprint Planning DTEND should be 11:00 AM UTC (T110000Z, 1 hour); "
            f"got {dtend!r}"
        )
    return 1.0, None


def _check_sprint_planning_rrule(ics, events):
    """Sprint Planning must have RRULE:FREQ=WEEKLY;COUNT=10."""
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    ev = _find_event(events, r"sprint\s*planning")
    if ev is None:
        return 0.0, "No Sprint Planning event found"
    if not ev.get("RRULE"):
        return 0.0, "Sprint Planning VEVENT has no RRULE"
    if not _has_rrule_field(ev, "FREQ", "WEEKLY"):
        return 0.0, f"Sprint Planning RRULE is not FREQ=WEEKLY; got {ev.get('RRULE')}"
    if not _has_rrule_field(ev, "COUNT", "10"):
        return 0.0, f"Sprint Planning RRULE does not have COUNT=10; got {ev.get('RRULE')}"
    return 1.0, None


def _check_sprint_planning_attendees(ics, events):
    """Sprint Planning must have attendees alice@example.com and bob@example.com."""
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    ev = _find_event(events, r"sprint\s*planning")
    if ev is None:
        return 0.0, "No Sprint Planning event found"
    emails = _attendee_emails(ev)
    missing = []
    for required in ("alice@example.com", "bob@example.com"):
        if required not in emails:
            missing.append(required)
    if missing:
        return 0.0, f"Sprint Planning missing attendees: {missing}; found: {sorted(emails)}"
    return 1.0, None


def _check_design_review_date(ics, events):
    """Design Review must be on April 20, 2026 (upcoming Monday from Wednesday April 15)."""
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    ev = _find_event(events, r"design\s*review")
    if ev is None:
        return 0.0, "No VEVENT with SUMMARY matching 'Design Review' found"
    dtstart = _dtstart(ev)
    if dtstart is None:
        return 0.0, "Design Review VEVENT has no DTSTART"
    if not dtstart.startswith("20260420"):
        return 0.0, (
            f"Design Review DTSTART date should be 20260420 (April 20 — upcoming Monday "
            f"from Wednesday April 15); got {dtstart!r}"
        )
    return 1.0, None


def _check_design_review_time_and_duration(ics, events):
    """Design Review: 2:00 PM UTC, 90-minute duration → DTEND T153000Z."""
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    ev = _find_event(events, r"design\s*review")
    if ev is None:
        return 0.0, "No Design Review event found"
    dtstart = _dtstart(ev)
    if dtstart is None or "T140000Z" not in dtstart:
        return 0.0, (
            f"Design Review DTSTART should be 2:00 PM UTC (T140000Z); got {dtstart!r}"
        )
    dtend = _dtend(ev)
    if dtend is None or "T153000Z" not in dtend:
        return 0.0, (
            f"Design Review DTEND should be 3:30 PM UTC (T153000Z, 90-minute meeting); "
            f"got {dtend!r}"
        )
    return 1.0, None


def _check_design_review_location(ics, events):
    """Design Review must have LOCATION:Conference Room B."""
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    ev = _find_event(events, r"design\s*review")
    if ev is None:
        return 0.0, "No Design Review event found"
    locs = ev.get("LOCATION", [])
    if not locs:
        return 0.0, "Design Review VEVENT has no LOCATION field"
    if not any("conference room b" in loc.lower() for loc in locs):
        return 0.0, f"Design Review LOCATION should be 'Conference Room B'; got {locs}"
    return 1.0, None


def _check_design_review_attendee(ics, events):
    """Design Review must have attendee carol@example.com."""
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    ev = _find_event(events, r"design\s*review")
    if ev is None:
        return 0.0, "No Design Review event found"
    emails = _attendee_emails(ev)
    if "carol@example.com" not in emails:
        return 0.0, f"Design Review missing carol@example.com; found: {sorted(emails)}"
    return 1.0, None


def _check_quarterly_kickoff_date_time(ics, events):
    """Quarterly Kickoff: April 30, 2026, 9:00 AM UTC, 2 hours → DTEND T110000Z."""
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    ev = _find_event(events, r"quarterly\s*kickoff")
    if ev is None:
        return 0.0, "No VEVENT with SUMMARY matching 'Quarterly Kickoff' found"
    dtstart = _dtstart(ev)
    if dtstart is None:
        return 0.0, "Quarterly Kickoff has no DTSTART"
    if not dtstart.startswith("20260430"):
        return 0.0, (
            f"Quarterly Kickoff DTSTART date should be 20260430 (April 30); got {dtstart!r}"
        )
    if "T090000Z" not in dtstart:
        return 0.0, (
            f"Quarterly Kickoff DTSTART should be 9:00 AM UTC (T090000Z); got {dtstart!r}"
        )
    dtend = _dtend(ev)
    if dtend is None or "T110000Z" not in dtend:
        return 0.0, (
            f"Quarterly Kickoff DTEND should be 11:00 AM UTC (T110000Z, 2-hour meeting); "
            f"got {dtend!r}"
        )
    return 1.0, None


def _check_quarterly_kickoff_attendees(ics, events):
    """Quarterly Kickoff must include alice, dave, and eve."""
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    ev = _find_event(events, r"quarterly\s*kickoff")
    if ev is None:
        return 0.0, "No Quarterly Kickoff event found"
    emails = _attendee_emails(ev)
    missing = []
    for required in ("alice@example.com", "dave@example.com", "eve@example.com"):
        if required not in emails:
            missing.append(required)
    if missing:
        return 0.0, f"Quarterly Kickoff missing attendees: {missing}; found: {sorted(emails)}"
    return 1.0, None


def _check_all_datetimes_utc(ics, events):
    """All DTSTART and DTEND values must use the UTC suffix 'Z' — local time format is not acceptable for team scheduling."""
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    violations = []
    for i, ev in enumerate(events):
        for field in ("DTSTART", "DTEND"):
            for val in ev.get(field, []):
                if "T" in val and not val.endswith("Z"):
                    summary = (ev.get("SUMMARY") or ["event"])[0]
                    violations.append(f"{summary}: {field}={val!r} (missing Z suffix)")
    if violations:
        return 0.0, (
            f"Non-UTC datetime(s) found — all DTSTART/DTEND must end with 'Z' for team "
            f"scheduling; violations: {'; '.join(violations[:3])}"
        )
    return 1.0, None


def _check_unique_uids(ics, events):
    """Each VEVENT must have a unique UID — duplicate UIDs cause calendar clients to merge or drop events."""
    if ics is None:
        return 0.0, "team_schedule.ics not found"
    uids = []
    for ev in events:
        uid_vals = ev.get("UID", [])
        uids.extend(uid_vals)
    if not uids:
        return 0.0, "No UIDs found in any VEVENT"
    if len(set(uids)) < len(events):
        return 0.0, f"Duplicate or missing UIDs across {len(events)} events; found: {uids}"
    return 1.0, None


# ---- Criterion registry ----------------------------------------------------

CRITERIA = [
    {
        "id": "file-exists",
        "weight": 0.05,
        "description": "team_schedule.ics exists at the workspace root and contains a valid VCALENDAR structure with VERSION:2.0.",
        "check": _check_file_exists,
    },
    {
        "id": "vcalendar-structure",
        "weight": 0.04,
        "description": "team_schedule.ics has the required BEGIN:VCALENDAR / END:VCALENDAR wrapper and VERSION:2.0 property, forming a valid iCalendar container.",
        "check": _check_vcalendar_structure,
    },
    {
        "id": "three-vevents",
        "weight": 0.05,
        "description": "The .ics file contains at least 3 VEVENT blocks — one per scheduled meeting (Sprint Planning, Design Review, Quarterly Kickoff).",
        "check": _check_three_vevents,
    },
    {
        "id": "sprint-planning-date",
        "weight": 0.14,
        "description": "Sprint Planning DTSTART falls on April 22, 2026 — the FOLLOWING Wednesday from the reference date Wednesday April 15. The SKILL.md rule states: if today is Wednesday, 'next Wednesday' means the following Wednesday (7 days later), not the same day.",
        "check": _check_sprint_planning_date,
    },
    {
        "id": "sprint-planning-time-utc",
        "weight": 0.08,
        "description": "Sprint Planning DTSTART is 10:00 AM UTC (T100000Z) and DTEND is 11:00 AM UTC (T110000Z), reflecting the 1-hour duration in UTC.",
        "check": _check_sprint_planning_time_utc,
    },
    {
        "id": "sprint-planning-rrule",
        "weight": 0.10,
        "description": "Sprint Planning has RRULE:FREQ=WEEKLY;COUNT=10, creating 10 weekly occurrences starting from the first instance — not a one-time event.",
        "check": _check_sprint_planning_rrule,
    },
    {
        "id": "sprint-planning-attendees",
        "weight": 0.07,
        "description": "Sprint Planning VEVENT lists both alice@example.com and bob@example.com as ATTENDEE entries.",
        "check": _check_sprint_planning_attendees,
    },
    {
        "id": "design-review-date",
        "weight": 0.09,
        "description": "Design Review DTSTART falls on April 20, 2026 — the upcoming Monday from Wednesday April 15, computed as 5 days forward (not 'next Monday' ambiguity — the task specifies 'upcoming Monday').",
        "check": _check_design_review_date,
    },
    {
        "id": "design-review-time-duration",
        "weight": 0.07,
        "description": "Design Review runs from 2:00 PM UTC (T140000Z) to 3:30 PM UTC (T153000Z), encoding a 90-minute duration as a concrete DTEND rather than a DURATION field.",
        "check": _check_design_review_time_and_duration,
    },
    {
        "id": "design-review-location",
        "weight": 0.06,
        "description": "Design Review VEVENT has a LOCATION field set to 'Conference Room B' — location must be a machine-readable field, not embedded in DESCRIPTION.",
        "check": _check_design_review_location,
    },
    {
        "id": "design-review-attendee",
        "weight": 0.04,
        "description": "Design Review VEVENT lists carol@example.com as an ATTENDEE entry.",
        "check": _check_design_review_attendee,
    },
    {
        "id": "quarterly-kickoff-datetime",
        "weight": 0.08,
        "description": "Quarterly Kickoff DTSTART is April 30, 2026 at 9:00 AM UTC (20260430T090000Z) and DTEND is 11:00 AM UTC (T110000Z), encoding a 2-hour duration.",
        "check": _check_quarterly_kickoff_date_time,
    },
    {
        "id": "quarterly-kickoff-attendees",
        "weight": 0.04,
        "description": "Quarterly Kickoff VEVENT lists all three attendees: alice@example.com, dave@example.com, and eve@example.com.",
        "check": _check_quarterly_kickoff_attendees,
    },
    {
        "id": "all-datetimes-utc",
        "weight": 0.07,
        "description": "All DTSTART and DTEND values across every VEVENT use the UTC suffix 'Z' — local (floating) time is not acceptable for multi-attendee scheduling because attendees in different time zones would see incorrect times.",
        "check": _check_all_datetimes_utc,
    },
    {
        "id": "unique-uids",
        "weight": 0.02,
        "description": "Each VEVENT has a unique UID — without distinct UIDs, calendar clients merge or silently drop events, breaking the multi-event schedule.",
        "check": _check_unique_uids,
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

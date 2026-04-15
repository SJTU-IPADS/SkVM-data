#!/usr/bin/env python3
"""
Reference solution for calendar_task_02.

Scenario: An executive assistant is composing a calendar file on Tuesday,
April 14, 2026. She has three scheduling requests from an email thread:

1. "Team Sync" — recurring monthly meeting, FIRST occurrence on "next Tuesday"
   (from Tuesday April 14 → April 21, 2026 per SKILL.md 'following' rule),
   at 3:00 PM UTC, 45 minutes long, repeating monthly for 6 occurrences.
   RRULE: FREQ=MONTHLY;COUNT=6
   Attendees: frank@example.com, grace@example.com

2. "Budget Review" — one-time meeting on April 28, 2026 at 11:00 AM UTC,
   2 hours long. The meeting is scheduled for the same day as a pre-existing
   conference, so DTEND must be no later than 1:00 PM UTC (T130000Z) to avoid
   conflict.
   Attendee: frank@example.com
   Description: "Q2 budget review - must end by 1 PM UTC due to afternoon conference"

3. "Heidi's Work Anniversary" — all-day event on May 1, 2026.
   All-day events use DATE format (YYYYMMDD), NOT datetime format.
   No DTEND needed (or DTEND = next day: 20260502).
   No attendees.

Output: executive_calendar.ics at workspace root.
"""

ICS_CONTENT = """\
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Agent//Calendar//EN
BEGIN:VEVENT
UID:team-sync-001@agent
DTSTART:20260421T150000Z
DTEND:20260421T154500Z
SUMMARY:Team Sync
RRULE:FREQ=MONTHLY;COUNT=6
ATTENDEE;CN=Frank:mailto:frank@example.com
ATTENDEE;CN=Grace:mailto:grace@example.com
END:VEVENT
BEGIN:VEVENT
UID:budget-review-001@agent
DTSTART:20260428T110000Z
DTEND:20260428T130000Z
SUMMARY:Budget Review
DESCRIPTION:Q2 budget review - must end by 1 PM UTC due to afternoon conference
ATTENDEE;CN=Frank:mailto:frank@example.com
END:VEVENT
BEGIN:VEVENT
UID:work-anniversary-001@agent
DTSTART;VALUE=DATE:20260501
DTEND;VALUE=DATE:20260502
SUMMARY:Heidi's Work Anniversary
END:VEVENT
END:VCALENDAR
"""

with open("executive_calendar.ics", "w") as f:
    f.write(ICS_CONTENT)

print("Written executive_calendar.ics")

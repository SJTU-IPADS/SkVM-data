#!/usr/bin/env python3
"""
Reference solution for calendar_task_01.

Scenario: An engineering team scheduling tool running on Wednesday, April 15, 2026
needs to generate a single .ics file containing three calendar events:

1. "Sprint Planning" — recurring weekly, every Wednesday at 10:00 AM UTC,
   starting "next Wednesday" (from April 15, which IS Wednesday → April 22)
   for 10 occurrences, 1 hour long.
   Attendees: alice@example.com, bob@example.com

2. "Design Review" — one-time meeting on the upcoming Monday (April 20, 2026)
   at 2:00 PM UTC, 90 minutes long.
   Location: "Conference Room B"
   Attendee: carol@example.com

3. "Quarterly Kickoff" — one-time meeting on April 30, 2026 at 9:00 AM UTC,
   2 hours long.
   Attendees: alice@example.com, dave@example.com, eve@example.com

Output: team_schedule.ics at the workspace root.
"""

import os

ICS_CONTENT = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Agent//Calendar//EN
BEGIN:VEVENT
UID:sprint-planning-001@agent
DTSTART:20260422T100000Z
DTEND:20260422T110000Z
SUMMARY:Sprint Planning
RRULE:FREQ=WEEKLY;COUNT=10
ATTENDEE;CN=Alice:mailto:alice@example.com
ATTENDEE;CN=Bob:mailto:bob@example.com
END:VEVENT
BEGIN:VEVENT
UID:design-review-001@agent
DTSTART:20260420T140000Z
DTEND:20260420T153000Z
SUMMARY:Design Review
LOCATION:Conference Room B
ATTENDEE;CN=Carol:mailto:carol@example.com
END:VEVENT
BEGIN:VEVENT
UID:quarterly-kickoff-001@agent
DTSTART:20260430T090000Z
DTEND:20260430T110000Z
SUMMARY:Quarterly Kickoff
ATTENDEE;CN=Alice:mailto:alice@example.com
ATTENDEE;CN=Dave:mailto:dave@example.com
ATTENDEE;CN=Eve:mailto:eve@example.com
END:VEVENT
END:VCALENDAR
"""

with open("team_schedule.ics", "w") as f:
    f.write(ICS_CONTENT.lstrip("\n"))

print("Written team_schedule.ics")

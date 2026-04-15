---
name: calendar
description: Calendar management and scheduling. Create ICS events, manage meetings, and handle date/time parsing.
---

# Calendar Management

## Creating ICS Calendar Events

The iCalendar (.ics) format is the standard for calendar event files. Use this structure:

```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Agent//Calendar//EN
BEGIN:VEVENT
DTSTART:20260405T150000Z
DTEND:20260405T160000Z
SUMMARY:Meeting Title
DESCRIPTION:Meeting description
ATTENDEE;CN=Name:mailto:email@example.com
UID:unique-id@agent
END:VEVENT
END:VCALENDAR
```

## Date/Time Handling

- Dates use `YYYYMMDD` format
- Date-times use `YYYYMMDDTHHMMSS` or `YYYYMMDDTHHMMSSZ` (UTC)
- "Next Tuesday" means the upcoming Tuesday from today's date. If today is Tuesday, it means the following Tuesday.
- Use 24-hour time: 3:00 PM = T150000

## Key Fields

| Field | Format | Example |
|-------|--------|---------|
| DTSTART | YYYYMMDDTHHMMSS | 20260407T150000 |
| SUMMARY | Plain text | Project Sync |
| DESCRIPTION | Plain text | Discuss Q1 roadmap |
| ATTENDEE | mailto:email | mailto:john@example.com |
| LOCATION | Plain text | Conference Room A |
| RRULE | Recurrence rule | FREQ=WEEKLY;COUNT=10 |

## Workflow

1. Parse the user's natural language request for date, time, title, attendees, and notes
2. Calculate absolute dates from relative expressions ("next Tuesday", "tomorrow")
3. Generate a valid .ics file with all required fields
4. Save the file to the workspace with a descriptive filename

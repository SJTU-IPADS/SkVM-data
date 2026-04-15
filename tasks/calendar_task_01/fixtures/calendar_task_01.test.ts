import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadICS(): string {
  return readFileSync("team_meeting.ics", "utf-8")
}

describe("team_meeting.ics", () => {
  test("file exists", () => {
    expect(existsSync("team_meeting.ics")).toBe(true)
  })

  test("has BEGIN:VCALENDAR and END:VCALENDAR wrappers", () => {
    const ics = loadICS()
    expect(ics).toContain("BEGIN:VCALENDAR")
    expect(ics).toContain("END:VCALENDAR")
  })

  test("has VERSION:2.0", () => {
    const ics = loadICS()
    expect(ics).toContain("VERSION:2.0")
  })

  test("has BEGIN:VEVENT and END:VEVENT block", () => {
    const ics = loadICS()
    expect(ics).toContain("BEGIN:VEVENT")
    expect(ics).toContain("END:VEVENT")
  })

  test("DTSTART is 20260504T100000Z", () => {
    const ics = loadICS()
    expect(ics).toMatch(/DTSTART.*20260504T100000Z/m)
  })

  test("DTEND is 20260504T110000Z", () => {
    const ics = loadICS()
    expect(ics).toMatch(/DTEND.*20260504T110000Z/m)
  })

  test("SUMMARY contains 'Weekly Engineering Sync'", () => {
    const ics = loadICS()
    expect(ics).toMatch(/SUMMARY.*Weekly Engineering Sync/im)
  })

  test("LOCATION contains 'Conference Room B'", () => {
    const ics = loadICS()
    expect(ics).toMatch(/LOCATION.*Conference Room B/im)
  })

  test("RRULE specifies FREQ=WEEKLY and COUNT=8", () => {
    const ics = loadICS()
    expect(ics).toMatch(/RRULE.*FREQ=WEEKLY/im)
    expect(ics).toMatch(/RRULE.*COUNT=8/im)
  })

  test("UID contains 'weekly-eng-sync'", () => {
    const ics = loadICS()
    expect(ics).toMatch(/UID.*weekly-eng-sync/im)
  })

  test("all 4 attendees are listed", () => {
    const ics = loadICS()
    expect(ics.toLowerCase()).toContain("alice@example.com")
    expect(ics.toLowerCase()).toContain("bob@example.com")
    expect(ics.toLowerCase()).toContain("carol@example.com")
    expect(ics.toLowerCase()).toContain("david@example.com")
  })
})

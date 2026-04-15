import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadICS(): string {
  return readFileSync("meetings.ics", "utf-8")
}

function countOccurrences(text: string, pattern: string): number {
  return (text.match(new RegExp(pattern, "g")) || []).length
}

describe("meetings.ics", () => {
  test("file exists", () => {
    expect(existsSync("meetings.ics")).toBe(true)
  })

  test("has BEGIN:VCALENDAR and END:VCALENDAR wrappers", () => {
    const ics = loadICS()
    expect(ics).toContain("BEGIN:VCALENDAR")
    expect(ics).toContain("END:VCALENDAR")
    expect(ics).toContain("VERSION:2.0")
  })

  test("contains exactly 3 VEVENT blocks", () => {
    const ics = loadICS()
    const beginCount = countOccurrences(ics, "BEGIN:VEVENT")
    const endCount = countOccurrences(ics, "END:VEVENT")
    expect(beginCount).toBe(3)
    expect(endCount).toBe(3)
  })

  test("Meeting 1: DTSTART is 20260610T140000Z and DTEND is 20260610T153000Z", () => {
    const ics = loadICS()
    expect(ics).toMatch(/DTSTART.*20260610T140000Z/m)
    expect(ics).toMatch(/DTEND.*20260610T153000Z/m)
  })

  test("Meeting 2: DTSTART is 20260612T090000Z and DTEND is 20260612T110000Z", () => {
    const ics = loadICS()
    expect(ics).toMatch(/DTSTART.*20260612T090000Z/m)
    expect(ics).toMatch(/DTEND.*20260612T110000Z/m)
  })

  test("Meeting 3: DTSTART is 20260615T153000Z and DTEND is 20260615T163000Z", () => {
    const ics = loadICS()
    expect(ics).toMatch(/DTSTART.*20260615T153000Z/m)
    expect(ics).toMatch(/DTEND.*20260615T163000Z/m)
  })

  test("UID for Meeting 1 contains 'roadmap-review-jun2026'", () => {
    const ics = loadICS()
    expect(ics.toLowerCase()).toContain("roadmap-review-jun2026")
  })

  test("UID for Meeting 2 contains 'design-sprint-jun2026'", () => {
    const ics = loadICS()
    expect(ics.toLowerCase()).toContain("design-sprint-jun2026")
  })

  test("UID for Meeting 3 contains 'q2-budget-jun2026'", () => {
    const ics = loadICS()
    expect(ics.toLowerCase()).toContain("q2-budget-jun2026")
  })

  test("all attendee emails are present", () => {
    const ics = loadICS().toLowerCase()
    expect(ics).toContain("pm@example.com")
    expect(ics).toContain("eng@example.com")
    expect(ics).toContain("design@example.com")
    expect(ics).toContain("ux@example.com")
    expect(ics).toContain("finance@example.com")
    expect(ics).toContain("ceo@example.com")
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadMinutes(): any {
  return JSON.parse(readFileSync("meeting_minutes.json", "utf-8"))
}

describe("meeting_minutes.json", () => {
  test("file exists", () => {
    expect(existsSync("meeting_minutes.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadMinutes()).not.toThrow()
  })

  test("meeting_info has required fields", () => {
    const m = loadMinutes()
    expect(m).toHaveProperty("meeting_info")
    expect(m.meeting_info).toHaveProperty("topic")
    expect(m.meeting_info).toHaveProperty("date")
    expect(m.meeting_info).toHaveProperty("duration_minutes")
    expect(m.meeting_info).toHaveProperty("attendees")
  })

  test("topic is Q2 Product Roadmap Review", () => {
    const m = loadMinutes()
    expect(m.meeting_info.topic).toBe("Q2 Product Roadmap Review")
  })

  test("date is 2026-04-08", () => {
    const m = loadMinutes()
    expect(m.meeting_info.date).toBe("2026-04-08")
  })

  test("duration_minutes is 90", () => {
    const m = loadMinutes()
    expect(m.meeting_info.duration_minutes).toBe(90)
  })

  test("exactly 4 attendees", () => {
    const m = loadMinutes()
    expect(Array.isArray(m.meeting_info.attendees)).toBe(true)
    expect(m.meeting_info.attendees.length).toBe(4)
  })

  test("attendees have name and role fields", () => {
    const m = loadMinutes()
    for (const a of m.meeting_info.attendees) {
      expect(a).toHaveProperty("name")
      expect(a).toHaveProperty("role")
      expect(typeof a.name).toBe("string")
      expect(typeof a.role).toBe("string")
    }
  })

  test("exactly 3 decisions with IDs D-1, D-2, D-3", () => {
    const m = loadMinutes()
    expect(Array.isArray(m.decisions)).toBe(true)
    expect(m.decisions.length).toBe(3)
    const ids = m.decisions.map((d: any) => d.id).sort()
    expect(ids).toContain("D-1")
    expect(ids).toContain("D-2")
    expect(ids).toContain("D-3")
  })

  test("exactly 3 action items with IDs A-1, A-2, A-3", () => {
    const m = loadMinutes()
    expect(Array.isArray(m.action_items)).toBe(true)
    expect(m.action_items.length).toBe(3)
    const ids = m.action_items.map((a: any) => a.id).sort()
    expect(ids).toContain("A-1")
    expect(ids).toContain("A-2")
    expect(ids).toContain("A-3")
  })

  test("action items have owner, task, and due_date fields", () => {
    const m = loadMinutes()
    for (const a of m.action_items) {
      expect(a).toHaveProperty("owner")
      expect(a).toHaveProperty("task")
      expect(a).toHaveProperty("due_date")
      expect(typeof a.due_date).toBe("string")
      // due_date should be YYYY-MM-DD format
      expect(a.due_date).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    }
  })

  test("summary field exists and is non-empty string", () => {
    const m = loadMinutes()
    expect(m).toHaveProperty("summary")
    expect(typeof m.summary).toBe("string")
    expect(m.summary.length).toBeGreaterThan(20)
  })
})

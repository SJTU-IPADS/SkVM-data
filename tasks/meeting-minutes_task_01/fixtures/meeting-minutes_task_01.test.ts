import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadMinutes(): any {
  return JSON.parse(readFileSync("minutes.json", "utf-8"))
}

function loadActionItems(): any {
  return JSON.parse(readFileSync("action_items.json", "utf-8"))
}

describe("minutes.json", () => {
  test("minutes file exists", () => {
    expect(existsSync("minutes.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadMinutes()).not.toThrow()
  })

  test("has required fields: date, attendees, summary, decisions, risks", () => {
    const m = loadMinutes()
    expect(m).toHaveProperty("date")
    expect(m).toHaveProperty("attendees")
    expect(m).toHaveProperty("summary")
    expect(m).toHaveProperty("decisions")
    expect(m).toHaveProperty("risks")
  })

  test("correct date is 2026-04-10", () => {
    const m = loadMinutes()
    expect(m.date).toBe("2026-04-10")
  })

  test("attendees array has 4 entries", () => {
    const m = loadMinutes()
    expect(Array.isArray(m.attendees)).toBe(true)
    expect(m.attendees.length).toBe(4)
  })

  test("each attendee has name and role fields", () => {
    const m = loadMinutes()
    for (const a of m.attendees) {
      expect(typeof a.name).toBe("string")
      expect(a.name.length).toBeGreaterThan(0)
      expect(typeof a.role).toBe("string")
      expect(a.role.length).toBeGreaterThan(0)
    }
  })

  test("decisions array is non-empty and references May 12 launch", () => {
    const m = loadMinutes()
    expect(Array.isArray(m.decisions)).toBe(true)
    expect(m.decisions.length).toBeGreaterThanOrEqual(1)
    const allDecisions = m.decisions.join(" ").toLowerCase()
    expect(allDecisions).toMatch(/may 12|launch date/)
  })

  test("risks array has at least 1 entry with description and owner", () => {
    const m = loadMinutes()
    expect(Array.isArray(m.risks)).toBe(true)
    expect(m.risks.length).toBeGreaterThanOrEqual(1)
    for (const r of m.risks) {
      expect(typeof r.description).toBe("string")
      expect(r.description.length).toBeGreaterThan(0)
      expect(typeof r.owner).toBe("string")
      expect(r.owner.length).toBeGreaterThan(0)
    }
  })

  test("summary is a non-empty string", () => {
    const m = loadMinutes()
    expect(typeof m.summary).toBe("string")
    expect(m.summary.length).toBeGreaterThan(20)
  })
})

describe("action_items.json", () => {
  test("action items file exists", () => {
    expect(existsSync("action_items.json")).toBe(true)
  })

  test("has action_items array with at least 3 items", () => {
    const a = loadActionItems()
    expect(a).toHaveProperty("action_items")
    expect(Array.isArray(a.action_items)).toBe(true)
    expect(a.action_items.length).toBeGreaterThanOrEqual(3)
  })

  test("each action item has id, description, owner, and due_date fields", () => {
    const a = loadActionItems()
    for (const item of a.action_items) {
      expect(typeof item.id).toBe("string")
      expect(typeof item.description).toBe("string")
      expect(typeof item.owner).toBe("string")
      expect(typeof item.due_date).toBe("string")
    }
  })

  test("action item IDs follow AI-001 pattern", () => {
    const a = loadActionItems()
    for (const item of a.action_items) {
      expect(item.id).toMatch(/^AI-\d{3}$/)
    }
  })

  test("due dates are in YYYY-MM-DD format", () => {
    const a = loadActionItems()
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/
    for (const item of a.action_items) {
      expect(item.due_date).toMatch(dateRegex)
    }
  })
})

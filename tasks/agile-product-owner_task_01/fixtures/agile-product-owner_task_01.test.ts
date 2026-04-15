import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadBacklog(): any {
  return JSON.parse(readFileSync("backlog.json", "utf-8"))
}

function loadSprintPlan(): any {
  return JSON.parse(readFileSync("sprint_plan.json", "utf-8"))
}

const FIBONACCI = new Set([1, 2, 3, 5, 8, 13, 21])

describe("backlog.json", () => {
  test("file exists", () => {
    expect(existsSync("backlog.json")).toBe(true)
  })

  test("has epic field and stories array", () => {
    const b = loadBacklog()
    expect(b).toHaveProperty("epic")
    expect(b).toHaveProperty("stories")
    expect(Array.isArray(b.stories)).toBe(true)
  })

  test("contains exactly 5 user stories", () => {
    const b = loadBacklog()
    expect(b.stories.length).toBe(5)
  })

  test("each story has required fields: id, title, persona, story, points, priority, acceptance_criteria", () => {
    const b = loadBacklog()
    for (const s of b.stories) {
      expect(s).toHaveProperty("id")
      expect(s).toHaveProperty("title")
      expect(s).toHaveProperty("persona")
      expect(s).toHaveProperty("story")
      expect(s).toHaveProperty("points")
      expect(s).toHaveProperty("priority")
      expect(s).toHaveProperty("acceptance_criteria")
    }
  })

  test("story IDs are US-001 through US-005", () => {
    const b = loadBacklog()
    const ids = b.stories.map((s: any) => s.id).sort()
    expect(ids).toContain("US-001")
    expect(ids).toContain("US-002")
    expect(ids).toContain("US-003")
    expect(ids).toContain("US-004")
    expect(ids).toContain("US-005")
  })

  test("each story text contains 'As a', 'I want', and 'So that'", () => {
    const b = loadBacklog()
    for (const s of b.stories) {
      const storyText: string = s.story.toLowerCase()
      expect(storyText).toContain("as a")
      expect(storyText).toContain("i want")
      expect(storyText).toContain("so that")
    }
  })

  test("each story has Fibonacci story points (1, 2, 3, 5, or 8)", () => {
    const b = loadBacklog()
    for (const s of b.stories) {
      expect(typeof s.points).toBe("number")
      expect(FIBONACCI.has(s.points)).toBe(true)
      expect(s.points).toBeLessThanOrEqual(8)
    }
  })

  test("each story has at least 3 acceptance criteria", () => {
    const b = loadBacklog()
    for (const s of b.stories) {
      expect(Array.isArray(s.acceptance_criteria)).toBe(true)
      expect(s.acceptance_criteria.length).toBeGreaterThanOrEqual(3)
    }
  })

  test("priority values are High, Medium, or Low", () => {
    const b = loadBacklog()
    const valid = new Set(["High", "Medium", "Low"])
    for (const s of b.stories) {
      expect(valid.has(s.priority)).toBe(true)
    }
  })
})

describe("sprint_plan.json", () => {
  test("file exists", () => {
    expect(existsSync("sprint_plan.json")).toBe(true)
  })

  test("has required fields", () => {
    const p = loadSprintPlan()
    expect(p).toHaveProperty("sprint_goal")
    expect(p).toHaveProperty("velocity")
    expect(p).toHaveProperty("availability_factor")
    expect(p).toHaveProperty("adjusted_capacity")
    expect(p).toHaveProperty("committed_points")
    expect(p).toHaveProperty("committed_stories")
  })

  test("velocity is 34 and availability_factor is 0.85", () => {
    const p = loadSprintPlan()
    expect(p.velocity).toBe(34)
    expect(p.availability_factor).toBe(0.85)
  })

  test("adjusted_capacity is 34 * 0.85 = 28.9, rounded to 29", () => {
    const p = loadSprintPlan()
    expect(p.adjusted_capacity).toBe(29)
  })

  test("committed_points does not exceed 85% of adjusted_capacity (24 points)", () => {
    const p = loadSprintPlan()
    // 85% of 29 = 24.65, so at most 24
    expect(p.committed_points).toBeLessThanOrEqual(Math.floor(29 * 0.85))
    expect(p.committed_points).toBeGreaterThan(0)
  })

  test("committed_stories is an array of valid story IDs", () => {
    const p = loadSprintPlan()
    expect(Array.isArray(p.committed_stories)).toBe(true)
    expect(p.committed_stories.length).toBeGreaterThanOrEqual(1)
    const validIds = new Set(["US-001", "US-002", "US-003", "US-004", "US-005"])
    for (const id of p.committed_stories) {
      expect(validIds.has(id)).toBe(true)
    }
  })
})

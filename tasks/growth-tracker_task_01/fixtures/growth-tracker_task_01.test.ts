import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadQS(): any {
  return JSON.parse(readFileSync("quantified_self.json", "utf-8"))
}

function loadSummary(): any {
  return JSON.parse(readFileSync("growth_summary.json", "utf-8"))
}

describe("quantified_self.json", () => {
  test("file exists", () => {
    expect(existsSync("quantified_self.json")).toBe(true)
  })

  test("has required top-level keys", () => {
    const d = loadQS()
    expect(d).toHaveProperty("initialized_at")
    expect(d).toHaveProperty("growth")
    expect(d).toHaveProperty("tasks")
    expect(d).toHaveProperty("learning")
    expect(d).toHaveProperty("efficiency")
    expect(d).toHaveProperty("achievements")
    expect(d).toHaveProperty("goals")
    expect(d).toHaveProperty("daily_stats")
  })

  test("growth baseline and current values are correct", () => {
    const d = loadQS()
    expect(d.growth.baseline.overall).toBe(42.0)
    expect(d.growth.current.overall).toBe(48.5)
    expect(d.growth.baseline.knowledge).toBe(8.0)
    expect(d.growth.current.knowledge).toBe(22.0)
  })

  test("growth history has 2 entries", () => {
    const d = loadQS()
    expect(Array.isArray(d.growth.history)).toBe(true)
    expect(d.growth.history.length).toBe(2)
  })

  test("tasks has required fields", () => {
    const d = loadQS()
    expect(d.tasks).toHaveProperty("total")
    expect(d.tasks).toHaveProperty("completed")
    expect(d.tasks).toHaveProperty("in_progress")
    expect(d.tasks).toHaveProperty("failed")
    expect(d.tasks).toHaveProperty("completion_rate")
    expect(d.tasks).toHaveProperty("average_quality")
    expect(d.tasks).toHaveProperty("by_type")
  })

  test("tasks total is 15 and completed is 12", () => {
    const d = loadQS()
    expect(d.tasks.total).toBe(15)
    expect(d.tasks.completed).toBe(12)
    expect(d.tasks.failed).toBe(1)
    expect(d.tasks.in_progress).toBe(2)
  })

  test("learning has 2 concepts with required fields", () => {
    const d = loadQS()
    expect(Array.isArray(d.learning.new_concepts)).toBe(true)
    expect(d.learning.new_concepts.length).toBe(2)
    expect(d.learning.total_concepts).toBe(2)
    for (const c of d.learning.new_concepts) {
      expect(c).toHaveProperty("name")
      expect(c).toHaveProperty("mastery")
      expect(c).toHaveProperty("applied_count")
    }
  })

  test("achievements array has 1 entry with type and title", () => {
    const d = loadQS()
    expect(Array.isArray(d.achievements)).toBe(true)
    expect(d.achievements.length).toBe(1)
    expect(d.achievements[0]).toHaveProperty("type")
    expect(d.achievements[0]).toHaveProperty("title")
  })

  test("daily_stats contains entry for 2024-01-15", () => {
    const d = loadQS()
    expect(d.daily_stats).toHaveProperty("2024-01-15")
    expect(d.daily_stats["2024-01-15"].tasks_completed).toBe(12)
    expect(d.daily_stats["2024-01-15"].concepts_learned).toBe(2)
  })
})

describe("growth_summary.json", () => {
  test("file exists", () => {
    expect(existsSync("growth_summary.json")).toBe(true)
  })

  test("summary has all 5 required fields", () => {
    const s = loadSummary()
    expect(s).toHaveProperty("overall_growth_delta")
    expect(s).toHaveProperty("completion_rate")
    expect(s).toHaveProperty("top_category")
    expect(s).toHaveProperty("total_concepts_learned")
    expect(s).toHaveProperty("first_try_rate")
  })

  test("overall_growth_delta is 6.5", () => {
    const s = loadSummary()
    expect(typeof s.overall_growth_delta).toBe("number")
    expect(s.overall_growth_delta).toBe(6.5)
  })

  test("completion_rate is 80.0 and first_try_rate is 80.0", () => {
    const s = loadSummary()
    expect(s.completion_rate).toBe(80.0)
    expect(s.first_try_rate).toBe(80.0)
  })

  test("top_category is coding", () => {
    const s = loadSummary()
    expect(s.top_category).toBe("coding")
  })

  test("total_concepts_learned is 2", () => {
    const s = loadSummary()
    expect(s.total_concepts_learned).toBe(2)
  })
})

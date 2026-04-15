import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadSession(): any {
  return JSON.parse(readFileSync("session_data.json", "utf-8"))
}

function loadReport(): any {
  return JSON.parse(readFileSync("efficiency_report.json", "utf-8"))
}

describe("session_data.json", () => {
  test("file exists", () => {
    expect(existsSync("session_data.json")).toBe(true)
  })

  test("has session_id, date, tasks, goals", () => {
    const d = loadSession()
    expect(d).toHaveProperty("session_id")
    expect(d).toHaveProperty("date")
    expect(d).toHaveProperty("tasks")
    expect(d).toHaveProperty("goals")
  })

  test("tasks array has 5 entries", () => {
    const d = loadSession()
    expect(Array.isArray(d.tasks)).toBe(true)
    expect(d.tasks.length).toBe(5)
  })

  test("each task has id, type, completed, quality, iterations", () => {
    const d = loadSession()
    for (const t of d.tasks) {
      expect(t).toHaveProperty("id")
      expect(t).toHaveProperty("type")
      expect(t).toHaveProperty("completed")
      expect(t).toHaveProperty("quality")
      expect(t).toHaveProperty("iterations")
    }
  })

  test("goals array has 2 entries", () => {
    const d = loadSession()
    expect(Array.isArray(d.goals)).toBe(true)
    expect(d.goals.length).toBe(2)
  })
})

describe("efficiency_report.json", () => {
  test("file exists", () => {
    expect(existsSync("efficiency_report.json")).toBe(true)
  })

  test("has all 11 required fields", () => {
    const r = loadReport()
    expect(r).toHaveProperty("total_tasks")
    expect(r).toHaveProperty("completed_tasks")
    expect(r).toHaveProperty("failed_tasks")
    expect(r).toHaveProperty("completion_rate")
    expect(r).toHaveProperty("avg_quality")
    expect(r).toHaveProperty("avg_iterations")
    expect(r).toHaveProperty("first_try_count")
    expect(r).toHaveProperty("first_try_rate")
    expect(r).toHaveProperty("goal_quality_met")
    expect(r).toHaveProperty("goal_iterations_met")
    expect(r).toHaveProperty("type_breakdown")
  })

  test("total_tasks is 5 and completed_tasks is 4", () => {
    const r = loadReport()
    expect(r.total_tasks).toBe(5)
    expect(r.completed_tasks).toBe(4)
    expect(r.failed_tasks).toBe(1)
  })

  test("completion_rate is 80.0", () => {
    const r = loadReport()
    expect(r.completion_rate).toBe(80.0)
  })

  test("avg_quality is 8.25 (average of 9.0, 7.5, 8.5, 8.0 for completed tasks)", () => {
    const r = loadReport()
    expect(typeof r.avg_quality).toBe("number")
    expect(r.avg_quality).toBe(8.25)
  })

  test("avg_iterations is 1.8 (average of 1+3+2+1+2 = 9 / 5)", () => {
    const r = loadReport()
    expect(typeof r.avg_iterations).toBe("number")
    expect(r.avg_iterations).toBe(1.8)
  })

  test("first_try_count is 2 and first_try_rate is 40.0", () => {
    const r = loadReport()
    expect(r.first_try_count).toBe(2)
    expect(r.first_try_rate).toBe(40.0)
  })

  test("goal_quality_met is false (8.25 < 8.5) and goal_iterations_met is false (1.8 > 1.5)", () => {
    const r = loadReport()
    expect(r.goal_quality_met).toBe(false)
    expect(r.goal_iterations_met).toBe(false)
  })

  test("type_breakdown covers all 4 task types with correct counts", () => {
    const r = loadReport()
    expect(typeof r.type_breakdown).toBe("object")
    expect(r.type_breakdown).toHaveProperty("coding")
    expect(r.type_breakdown).toHaveProperty("debugging")
    expect(r.type_breakdown).toHaveProperty("documentation")
    expect(r.type_breakdown).toHaveProperty("design")
    expect(r.type_breakdown.coding).toBe(2)
    expect(r.type_breakdown.debugging).toBe(1)
    expect(r.type_breakdown.documentation).toBe(1)
    expect(r.type_breakdown.design).toBe(1)
  })
})

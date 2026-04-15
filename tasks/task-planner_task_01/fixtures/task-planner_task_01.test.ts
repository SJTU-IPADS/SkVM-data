import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadTasks(): any {
  return JSON.parse(readFileSync("tasks.json", "utf-8"))
}

function loadSummary(): any {
  return JSON.parse(readFileSync("tasks_summary.json", "utf-8"))
}

describe("tasks.json", () => {
  test("file exists", () => {
    expect(existsSync("tasks.json")).toBe(true)
  })

  test("is valid JSON with tasks array", () => {
    const d = loadTasks()
    expect(d).toHaveProperty("tasks")
    expect(Array.isArray(d.tasks)).toBe(true)
  })

  test("tasks array has exactly 5 entries", () => {
    const d = loadTasks()
    expect(d.tasks.length).toBe(5)
  })

  test("each task has required fields with correct types", () => {
    const d = loadTasks()
    for (const t of d.tasks) {
      expect(typeof t.id).toBe("number")
      expect(typeof t.name).toBe("string")
      expect(typeof t.priority).toBe("string")
      expect(typeof t.due_date).toBe("string")
      expect(typeof t.status).toBe("string")
      expect(Array.isArray(t.tags)).toBe(true)
    }
  })

  test("priority values are high, medium, or low", () => {
    const d = loadTasks()
    for (const t of d.tasks) {
      expect(["high", "medium", "low"]).toContain(t.priority)
    }
  })

  test("status values are pending or completed", () => {
    const d = loadTasks()
    for (const t of d.tasks) {
      expect(["pending", "completed"]).toContain(t.status)
    }
  })

  test("due_date values match YYYY-MM-DD format", () => {
    const d = loadTasks()
    for (const t of d.tasks) {
      expect(t.due_date).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    }
  })

  test("Pay electricity bill is completed with high priority", () => {
    const d = loadTasks()
    const bill = d.tasks.find((t: any) => /electricity bill/i.test(t.name))
    expect(bill).toBeDefined()
    expect(bill.status).toBe("completed")
    expect(bill.priority).toBe("high")
    expect(bill.due_date).toBe("2026-04-13")
  })

  test("3 tasks have high priority", () => {
    const d = loadTasks()
    const highCount = d.tasks.filter((t: any) => t.priority === "high").length
    expect(highCount).toBe(3)
  })
})

describe("tasks_summary.json", () => {
  test("file exists", () => {
    expect(existsSync("tasks_summary.json")).toBe(true)
  })

  test("summary counts are correct", () => {
    const s = loadSummary()
    expect(s.total).toBe(5)
    expect(s.pending).toBe(4)
    expect(s.completed).toBe(1)
    expect(s.high_priority).toBe(3)
    expect(s.overdue).toBe(0)
  })
})

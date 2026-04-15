import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("daily_report.json", "utf-8"))
}

describe("daily_report.json", () => {
  test("file exists", () => {
    expect(existsSync("daily_report.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadReport()).not.toThrow()
  })

  test("required top-level keys", () => {
    const r = loadReport()
    expect(r).toHaveProperty("date")
    expect(r).toHaveProperty("completed")
    expect(r).toHaveProperty("pending")
    expect(r).toHaveProperty("problems")
    expect(r).toHaveProperty("tomorrow_plan")
  })

  test("date is 2026-03-15", () => {
    const r = loadReport()
    expect(r.date).toBe("2026-03-15")
  })

  test("completed is an array with exactly 3 items", () => {
    const r = loadReport()
    expect(Array.isArray(r.completed)).toBe(true)
    expect(r.completed.length).toBe(3)
  })

  test("completed items have item field", () => {
    const r = loadReport()
    for (const entry of r.completed) {
      expect(entry).toHaveProperty("item")
      expect(typeof entry.item).toBe("string")
      expect(entry.item.length).toBeGreaterThan(0)
    }
  })

  test("at least 1 pending item with item field", () => {
    const r = loadReport()
    expect(Array.isArray(r.pending)).toBe(true)
    expect(r.pending.length).toBeGreaterThanOrEqual(1)
    expect(r.pending[0]).toHaveProperty("item")
  })

  test("at least 1 problem with description field", () => {
    const r = loadReport()
    expect(Array.isArray(r.problems)).toBe(true)
    expect(r.problems.length).toBeGreaterThanOrEqual(1)
    expect(r.problems[0]).toHaveProperty("description")
  })

  test("at least 2 tomorrow_plan items as strings", () => {
    const r = loadReport()
    expect(Array.isArray(r.tomorrow_plan)).toBe(true)
    expect(r.tomorrow_plan.length).toBeGreaterThanOrEqual(2)
    for (const item of r.tomorrow_plan) {
      expect(typeof item).toBe("string")
      expect(item.length).toBeGreaterThan(0)
    }
  })
})

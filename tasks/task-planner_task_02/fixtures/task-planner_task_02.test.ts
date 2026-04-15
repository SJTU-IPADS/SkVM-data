import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadData(): any {
  return JSON.parse(readFileSync("weekly_schedule.json", "utf-8"))
}

const WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

describe("weekly_schedule.json", () => {
  test("file exists", () => {
    expect(existsSync("weekly_schedule.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadData()).not.toThrow()
  })

  test("has required top-level keys", () => {
    const d = loadData()
    expect(d).toHaveProperty("week_start")
    expect(d).toHaveProperty("total_tasks")
    expect(d).toHaveProperty("total_estimated_hours")
    expect(d).toHaveProperty("tasks")
    expect(d).toHaveProperty("critical_tasks")
    expect(d).toHaveProperty("schedule_by_day")
  })

  test("week_start is 2026-04-11", () => {
    const d = loadData()
    expect(d.week_start).toBe("2026-04-11")
  })

  test("total_tasks is 6", () => {
    const d = loadData()
    expect(d.total_tasks).toBe(6)
  })

  test("total_estimated_hours is 14.5", () => {
    const d = loadData()
    expect(d.total_estimated_hours).toBe(14.5)
  })

  test("tasks array has 6 entries with day_assigned field", () => {
    const d = loadData()
    expect(Array.isArray(d.tasks)).toBe(true)
    expect(d.tasks.length).toBe(6)
    for (const t of d.tasks) {
      expect(typeof t.name).toBe("string")
      expect(typeof t.day_assigned).toBe("string")
      expect(WEEKDAYS).toContain(t.day_assigned)
    }
  })

  test("each task has day_assigned field that is a valid weekday", () => {
    const d = loadData()
    for (const t of d.tasks) {
      expect(WEEKDAYS).toContain(t.day_assigned)
    }
  })

  test("critical_tasks array has 2 entries", () => {
    const d = loadData()
    expect(Array.isArray(d.critical_tasks)).toBe(true)
    expect(d.critical_tasks.length).toBe(2)
    for (const name of d.critical_tasks) {
      expect(typeof name).toBe("string")
    }
  })

  test("schedule_by_day has all 5 weekday keys", () => {
    const d = loadData()
    for (const day of WEEKDAYS) {
      expect(d.schedule_by_day).toHaveProperty(day)
      expect(Array.isArray(d.schedule_by_day[day])).toBe(true)
    }
  })

  test("all 6 tasks appear in schedule_by_day across all days", () => {
    const d = loadData()
    const allAssigned: string[] = []
    for (const day of WEEKDAYS) {
      allAssigned.push(...(d.schedule_by_day[day] || []))
    }
    expect(allAssigned.length).toBe(6)
  })
})

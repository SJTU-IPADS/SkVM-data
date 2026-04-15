import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadMatrix(): any {
  return JSON.parse(readFileSync("task_matrix.json", "utf-8"))
}

const VALID_ACTIONS = new Set(["do_now", "schedule", "delegate", "eliminate"])
const ALL_TASKS = new Set([1, 2, 3, 4, 5, 6, 7, 8])

describe("task_matrix.json", () => {
  test("file exists", () => {
    expect(existsSync("task_matrix.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadMatrix()).not.toThrow()
  })

  test("quadrants has 4 required keys", () => {
    const m = loadMatrix()
    expect(m).toHaveProperty("quadrants")
    expect(m.quadrants).toHaveProperty("do_now")
    expect(m.quadrants).toHaveProperty("schedule")
    expect(m.quadrants).toHaveProperty("delegate")
    expect(m.quadrants).toHaveProperty("eliminate")
  })

  test("each quadrant has label and tasks array", () => {
    const m = loadMatrix()
    for (const key of ["do_now", "schedule", "delegate", "eliminate"]) {
      const q = m.quadrants[key]
      expect(q).toHaveProperty("label")
      expect(q).toHaveProperty("tasks")
      expect(Array.isArray(q.tasks)).toBe(true)
    }
  })

  test("task 1 is in do_now", () => {
    const m = loadMatrix()
    expect(m.quadrants.do_now.tasks).toContain(1)
  })

  test("all 8 tasks appear exactly once across quadrants", () => {
    const m = loadMatrix()
    const allTaskNums: number[] = [
      ...m.quadrants.do_now.tasks,
      ...m.quadrants.schedule.tasks,
      ...m.quadrants.delegate.tasks,
      ...m.quadrants.eliminate.tasks,
    ]
    expect(allTaskNums.length).toBe(8)
    const unique = new Set(allTaskNums)
    expect(unique.size).toBe(8)
    for (const n of ALL_TASKS) {
      expect(unique.has(n)).toBe(true)
    }
  })

  test("action_plan has exactly 8 entries", () => {
    const m = loadMatrix()
    expect(Array.isArray(m.action_plan)).toBe(true)
    expect(m.action_plan.length).toBe(8)
  })

  test("each action_plan entry has task_number, action, rationale, and time_block fields", () => {
    const m = loadMatrix()
    for (const entry of m.action_plan) {
      expect(entry).toHaveProperty("task_number")
      expect(entry).toHaveProperty("action")
      expect(entry).toHaveProperty("rationale")
      expect(entry).toHaveProperty("time_block")
      expect(typeof entry.rationale).toBe("string")
      expect(entry.rationale.length).toBeGreaterThan(0)
    }
  })

  test("action values are valid (do_now, schedule, delegate, or eliminate)", () => {
    const m = loadMatrix()
    for (const entry of m.action_plan) {
      expect(VALID_ACTIONS.has(entry.action)).toBe(true)
    }
  })

  test("energy_tip is a non-empty string", () => {
    const m = loadMatrix()
    expect(m).toHaveProperty("energy_tip")
    expect(typeof m.energy_tip).toBe("string")
    expect(m.energy_tip.length).toBeGreaterThan(10)
  })
})

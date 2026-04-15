import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadPlan(): any {
  return JSON.parse(readFileSync("fitness_plan.json", "utf-8"))
}

describe("fitness_plan.json", () => {
  test("fitness_plan.json exists", () => {
    expect(existsSync("fitness_plan.json")).toBe(true)
  })

  test("parses as valid JSON", () => {
    expect(() => loadPlan()).not.toThrow()
  })

  test("has all top-level required keys", () => {
    const p = loadPlan()
    expect(p).toHaveProperty("goal_summary")
    expect(p).toHaveProperty("weekly_plan")
    expect(p).toHaveProperty("exercises")
    expect(p).toHaveProperty("progression_guidance")
    expect(p).toHaveProperty("recovery_tips")
    expect(p).toHaveProperty("nutrition_guidance")
  })
})

describe("goal_summary", () => {
  test("goal_summary has required fields", () => {
    const p = loadPlan()
    const g = p.goal_summary
    expect(g).toHaveProperty("goal")
    expect(g).toHaveProperty("experience_level")
    expect(g).toHaveProperty("training_location")
    expect(g).toHaveProperty("equipment")
    expect(g).toHaveProperty("days_per_week")
  })

  test("goal is 'fat loss'", () => {
    const p = loadPlan()
    expect(p.goal_summary.goal.toLowerCase()).toContain("fat loss")
  })

  test("experience_level is 'beginner'", () => {
    const p = loadPlan()
    expect(p.goal_summary.experience_level.toLowerCase()).toBe("beginner")
  })

  test("days_per_week is 3", () => {
    const p = loadPlan()
    expect(p.goal_summary.days_per_week).toBe(3)
  })

  test("equipment is an array", () => {
    const p = loadPlan()
    expect(Array.isArray(p.goal_summary.equipment)).toBe(true)
  })
})

describe("weekly_plan has 7 days", () => {
  test("weekly_plan is an array of exactly 7 items", () => {
    const p = loadPlan()
    expect(Array.isArray(p.weekly_plan)).toBe(true)
    expect(p.weekly_plan.length).toBe(7)
  })

  test("each day entry has 'day' and 'activity' fields", () => {
    const p = loadPlan()
    for (const d of p.weekly_plan) {
      expect(d).toHaveProperty("day")
      expect(d).toHaveProperty("activity")
      expect(typeof d.day).toBe("string")
      expect(typeof d.activity).toBe("string")
    }
  })
})

describe("exercises", () => {
  test("exercises array has at least 4 items", () => {
    const p = loadPlan()
    expect(Array.isArray(p.exercises)).toBe(true)
    expect(p.exercises.length).toBeGreaterThanOrEqual(4)
  })

  test("each exercise has name, sets, reps, rest_seconds fields", () => {
    const p = loadPlan()
    for (const ex of p.exercises) {
      expect(ex).toHaveProperty("name")
      expect(ex).toHaveProperty("sets")
      expect(ex).toHaveProperty("reps")
      expect(ex).toHaveProperty("rest_seconds")
    }
  })

  test("exercise sets are positive integers", () => {
    const p = loadPlan()
    for (const ex of p.exercises) {
      expect(typeof ex.sets).toBe("number")
      expect(ex.sets).toBeGreaterThanOrEqual(1)
    }
  })

  test("rest_seconds are at least 30 for each exercise", () => {
    const p = loadPlan()
    for (const ex of p.exercises) {
      expect(typeof ex.rest_seconds).toBe("number")
      expect(ex.rest_seconds).toBeGreaterThanOrEqual(30)
    }
  })
})

describe("progression_guidance", () => {
  test("progression_guidance is an array of at least 2 strings", () => {
    const p = loadPlan()
    expect(Array.isArray(p.progression_guidance)).toBe(true)
    expect(p.progression_guidance.length).toBeGreaterThanOrEqual(2)
    for (const item of p.progression_guidance) {
      expect(typeof item).toBe("string")
      expect(item.length).toBeGreaterThan(0)
    }
  })
})

describe("recovery_tips and nutrition_guidance", () => {
  test("recovery_tips is a non-empty array of strings", () => {
    const p = loadPlan()
    expect(Array.isArray(p.recovery_tips)).toBe(true)
    expect(p.recovery_tips.length).toBeGreaterThanOrEqual(1)
  })

  test("nutrition_guidance is a non-empty array of strings", () => {
    const p = loadPlan()
    expect(Array.isArray(p.nutrition_guidance)).toBe(true)
    expect(p.nutrition_guidance.length).toBeGreaterThanOrEqual(1)
  })
})

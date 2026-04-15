import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadProgram(): any {
  return JSON.parse(readFileSync("muscle_program.json", "utf-8"))
}

describe("muscle_program.json", () => {
  test("muscle_program.json exists", () => {
    expect(existsSync("muscle_program.json")).toBe(true)
  })

  test("parses as valid JSON", () => {
    expect(() => loadProgram()).not.toThrow()
  })

  test("has top-level required keys", () => {
    const p = loadProgram()
    expect(p).toHaveProperty("program_name")
    expect(p).toHaveProperty("duration_weeks")
    expect(p).toHaveProperty("days_per_week")
    expect(p).toHaveProperty("goal")
    expect(p).toHaveProperty("weeks")
    expect(p).toHaveProperty("progression_notes")
    expect(p).toHaveProperty("recovery_guidance")
  })

  test("duration_weeks is 4", () => {
    const p = loadProgram()
    expect(p.duration_weeks).toBe(4)
  })

  test("days_per_week is 4", () => {
    const p = loadProgram()
    expect(p.days_per_week).toBe(4)
  })

  test("goal mentions muscle gain", () => {
    const p = loadProgram()
    expect(p.goal.toLowerCase()).toContain("muscle")
  })
})

describe("weeks structure", () => {
  test("weeks is an array of exactly 4 week objects", () => {
    const p = loadProgram()
    expect(Array.isArray(p.weeks)).toBe(true)
    expect(p.weeks.length).toBe(4)
  })

  test("each week has week number, focus, and workouts", () => {
    const p = loadProgram()
    for (const w of p.weeks) {
      expect(w).toHaveProperty("week")
      expect(w).toHaveProperty("focus")
      expect(w).toHaveProperty("workouts")
      expect(typeof w.focus).toBe("string")
      expect(w.focus.length).toBeGreaterThan(0)
    }
  })

  test("week numbers are 1 through 4", () => {
    const p = loadProgram()
    const weekNums = p.weeks.map((w: any) => w.week).sort((a: number, b: number) => a - b)
    expect(weekNums).toEqual([1, 2, 3, 4])
  })

  test("each week has exactly 4 workouts per week", () => {
    const p = loadProgram()
    for (const w of p.weeks) {
      expect(Array.isArray(w.workouts)).toBe(true)
      expect(w.workouts.length).toBe(4)
    }
  })
})

describe("workout and exercise structure", () => {
  test("each workout has day, name, and exercises fields", () => {
    const p = loadProgram()
    for (const w of p.weeks) {
      for (const workout of w.workouts) {
        expect(workout).toHaveProperty("day")
        expect(workout).toHaveProperty("name")
        expect(workout).toHaveProperty("exercises")
        expect(Array.isArray(workout.exercises)).toBe(true)
      }
    }
  })

  test("each workout has at least 3 exercises", () => {
    const p = loadProgram()
    for (const w of p.weeks) {
      for (const workout of w.workouts) {
        expect(workout.exercises.length).toBeGreaterThanOrEqual(3)
      }
    }
  })

  test("exercise has required fields: name, sets, reps, rest_seconds", () => {
    const p = loadProgram()
    const firstWeekFirstWorkout = p.weeks[0].workouts[0]
    for (const ex of firstWeekFirstWorkout.exercises) {
      expect(ex).toHaveProperty("name")
      expect(ex).toHaveProperty("sets")
      expect(ex).toHaveProperty("reps")
      expect(ex).toHaveProperty("rest_seconds")
    }
  })

  test("exercise sets are positive integers and rest_seconds >= 60", () => {
    const p = loadProgram()
    for (const w of p.weeks) {
      for (const workout of w.workouts) {
        for (const ex of workout.exercises) {
          expect(typeof ex.sets).toBe("number")
          expect(ex.sets).toBeGreaterThanOrEqual(1)
          expect(typeof ex.rest_seconds).toBe("number")
          expect(ex.rest_seconds).toBeGreaterThanOrEqual(60)
        }
      }
    }
  })
})

describe("progression_notes and recovery_guidance", () => {
  test("progression_notes is an array of at least 2 strings", () => {
    const p = loadProgram()
    expect(Array.isArray(p.progression_notes)).toBe(true)
    expect(p.progression_notes.length).toBeGreaterThanOrEqual(2)
    for (const note of p.progression_notes) {
      expect(typeof note).toBe("string")
      expect(note.length).toBeGreaterThan(0)
    }
  })

  test("recovery_guidance is a non-empty string", () => {
    const p = loadProgram()
    expect(typeof p.recovery_guidance).toBe("string")
    expect(p.recovery_guidance.length).toBeGreaterThan(0)
  })
})

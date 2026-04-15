import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadResults(): any {
  return JSON.parse(readFileSync("tension_results.json", "utf-8"))
}

function loadHighest(): string {
  return readFileSync("highest_tension.txt", "utf-8").trim()
}

// Expected tension values (pre-calculated):
// security:   dep=0.5, tension = 0.5² + 10*max(0,0.5-1.0)² = 0.25 + 0 = 0.25
// connection: dep=1.5, tension = 1.5² + 5*max(0,1.5-1.0)² = 2.25 + 5*0.25 = 3.5
// expression: dep=2.5, tension = 2.5² + 1*max(0,2.5-1.0)² = 6.25 + 1*2.25 = 8.5
// coherence:  dep=1.0, tension = 1.0² + 8*max(0,1.0-1.0)² = 1.0 + 0 = 1.0
// competence: dep=0.0, tension = 0.0² + 4*max(0,0.0-1.0)² = 0.0 + 0 = 0.0

describe("tension_calc.py", () => {
  test("file exists", () => {
    expect(existsSync("tension_calc.py")).toBe(true)
  })
})

describe("tension_results.json", () => {
  test("file exists", () => {
    expect(existsSync("tension_results.json")).toBe(true)
  })

  test("has crisis_threshold and needs fields", () => {
    const r = loadResults()
    expect(r).toHaveProperty("crisis_threshold")
    expect(r).toHaveProperty("needs")
  })

  test("crisis_threshold is 1.0", () => {
    const r = loadResults()
    expect(r.crisis_threshold).toBe(1.0)
  })

  test("security tension is 0.25 (dep=0.5, below threshold)", () => {
    const r = loadResults()
    expect(r.needs.security.tension).toBeCloseTo(0.25, 3)
  })

  test("connection tension is 3.5 (dep=1.5, above threshold)", () => {
    const r = loadResults()
    expect(r.needs.connection.tension).toBeCloseTo(3.5, 3)
  })

  test("expression tension is 8.5 (dep=2.5, crisis)", () => {
    const r = loadResults()
    expect(r.needs.expression.tension).toBeCloseTo(8.5, 3)
  })

  test("coherence tension is 1.0 (dep=1.0, exactly at threshold)", () => {
    const r = loadResults()
    expect(r.needs.coherence.tension).toBeCloseTo(1.0, 3)
  })

  test("competence tension is 0.0 (dep=0.0, fully satisfied)", () => {
    const r = loadResults()
    expect(r.needs.competence.tension).toBeCloseTo(0.0, 3)
  })

  test("all needs have dep field matching 3.0 - satisfaction", () => {
    const r = loadResults()
    const entries: Array<[string, any]> = Object.entries(r.needs)
    for (const [, need] of entries) {
      const expectedDep = 3.0 - need.satisfaction
      expect(need.dep).toBeCloseTo(expectedDep, 4)
    }
  })
})

describe("highest_tension.txt", () => {
  test("file exists", () => {
    expect(existsSync("highest_tension.txt")).toBe(true)
  })

  test("highest tension is 'expression'", () => {
    expect(loadHighest()).toBe("expression")
  })
})

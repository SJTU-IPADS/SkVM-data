import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("velocity_report.json", "utf-8"))
}

// Expected values computed from given data:
// completed: [20, 23, 26, 25, 27, 28]
// average_velocity = (20+23+26+25+27+28)/6 = 149/6 = 24.833... -> 24.83
// recommended_commitment = floor(24.83 * 0.85) = floor(21.1055) = 21
// first 3 avg = (20+23+26)/3 = 23
// last 3 avg = (25+27+28)/3 = 26.67
// velocity_trend = 'improving'
// commitment_reliability: [20/22=0.9091, 23/24=0.9583, 26/26=1.0, 25/28=0.8929, 27/27=1.0, 28/30=0.9333]
// best_sprint = sprint 3 (reliability=1.0, earliest tie with sprint 5)
// worst_sprint = sprint 4 (reliability=0.8929)

describe("velocity_report.json", () => {
  test("file exists", () => {
    expect(existsSync("velocity_report.json")).toBe(true)
  })

  test("is valid JSON with all required top-level fields", () => {
    const r = loadReport()
    expect(r).toHaveProperty("sprints")
    expect(r).toHaveProperty("average_velocity")
    expect(r).toHaveProperty("recommended_commitment")
    expect(r).toHaveProperty("velocity_trend")
    expect(r).toHaveProperty("best_sprint")
    expect(r).toHaveProperty("worst_sprint")
  })

  test("sprints array has 6 entries with required sub-fields", () => {
    const r = loadReport()
    expect(Array.isArray(r.sprints)).toBe(true)
    expect(r.sprints.length).toBe(6)
    for (const s of r.sprints) {
      expect(s).toHaveProperty("sprint_number")
      expect(s).toHaveProperty("committed")
      expect(s).toHaveProperty("completed")
      expect(s).toHaveProperty("commitment_reliability")
    }
  })

  test("sprint committed and completed values match input data", () => {
    const r = loadReport()
    const expected = [
      { committed: 22, completed: 20 },
      { committed: 24, completed: 23 },
      { committed: 26, completed: 26 },
      { committed: 28, completed: 25 },
      { committed: 27, completed: 27 },
      { committed: 30, completed: 28 },
    ]
    for (let i = 0; i < 6; i++) {
      expect(r.sprints[i].committed).toBe(expected[i].committed)
      expect(r.sprints[i].completed).toBe(expected[i].completed)
    }
  })

  test("average_velocity is 24.83", () => {
    const r = loadReport()
    expect(r.average_velocity).toBe(24.83)
  })

  test("recommended_commitment is 21", () => {
    const r = loadReport()
    expect(r.recommended_commitment).toBe(21)
  })

  test("velocity_trend is 'improving'", () => {
    const r = loadReport()
    expect(r.velocity_trend.toLowerCase()).toBe("improving")
  })

  test("best_sprint is sprint 3 (earliest with 100% reliability)", () => {
    const r = loadReport()
    expect(r.best_sprint).toBe(3)
  })

  test("worst_sprint is sprint 4 (lowest commitment reliability)", () => {
    const r = loadReport()
    expect(r.worst_sprint).toBe(4)
  })

  test("commitment_reliability values are between 0 and 1", () => {
    const r = loadReport()
    for (const s of r.sprints) {
      expect(s.commitment_reliability).toBeGreaterThan(0)
      expect(s.commitment_reliability).toBeLessThanOrEqual(1)
    }
  })
})

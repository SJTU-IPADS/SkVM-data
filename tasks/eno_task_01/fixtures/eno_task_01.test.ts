import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("arch_report.json", "utf-8"))
}

const VALID_GRADES = new Set(["excellent", "good", "acceptable", "needs_improvement", "critical"])

describe("arch_report.json", () => {
  test("file exists", () => {
    expect(existsSync("arch_report.json")).toBe(true)
  })

  test("parses as valid JSON", () => {
    expect(() => loadReport()).not.toThrow()
  })

  test("has all required fields: project_type, scores, total_score, grade, issues, recommendations", () => {
    const r = loadReport()
    expect(r).toHaveProperty("project_type")
    expect(r).toHaveProperty("scores")
    expect(r).toHaveProperty("total_score")
    expect(r).toHaveProperty("grade")
    expect(r).toHaveProperty("issues")
    expect(r).toHaveProperty("recommendations")
  })

  test("project_type is 'React'", () => {
    const r = loadReport()
    expect(r.project_type).toBe("React")
  })

  test("scores object has tech_stack_health, architecture_design, engineering_maturity within valid range", () => {
    const r = loadReport()
    expect(r.scores).toHaveProperty("tech_stack_health")
    expect(r.scores).toHaveProperty("architecture_design")
    expect(r.scores).toHaveProperty("engineering_maturity")
    expect(r.scores.tech_stack_health).toBeGreaterThanOrEqual(0)
    expect(r.scores.tech_stack_health).toBeLessThanOrEqual(50)
    expect(r.scores.architecture_design).toBeGreaterThanOrEqual(0)
    expect(r.scores.architecture_design).toBeLessThanOrEqual(35)
    expect(r.scores.engineering_maturity).toBeGreaterThanOrEqual(0)
    expect(r.scores.engineering_maturity).toBeLessThanOrEqual(20)
  })

  test("total_score is an integer in range 0-100", () => {
    const r = loadReport()
    expect(typeof r.total_score).toBe("number")
    expect(r.total_score).toBeGreaterThanOrEqual(0)
    expect(r.total_score).toBeLessThanOrEqual(100)
    expect(Number.isInteger(r.total_score)).toBe(true)
  })

  test("grade is one of the valid values: excellent, good, acceptable, needs_improvement, critical", () => {
    const r = loadReport()
    expect(VALID_GRADES.has(r.grade)).toBe(true)
  })

  test("issues array has at least 3 entries", () => {
    const r = loadReport()
    expect(Array.isArray(r.issues)).toBe(true)
    expect(r.issues.length).toBeGreaterThanOrEqual(3)
  })

  test("each issue is a non-empty string", () => {
    const r = loadReport()
    for (const issue of r.issues) {
      expect(typeof issue).toBe("string")
      expect(issue.length).toBeGreaterThan(0)
    }
  })

  test("recommendations array has at least 3 entries", () => {
    const r = loadReport()
    expect(Array.isArray(r.recommendations)).toBe(true)
    expect(r.recommendations.length).toBeGreaterThanOrEqual(3)
  })
})

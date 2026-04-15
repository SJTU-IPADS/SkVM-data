import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("review_report.json", "utf-8"))
}

describe("review_report.json", () => {
  test("file exists", () => {
    expect(existsSync("review_report.json")).toBe(true)
  })

  test("target.py file was created", () => {
    expect(existsSync("target.py")).toBe(true)
  })

  test("valid JSON with required top-level fields", () => {
    const r = loadReport()
    expect(r).toHaveProperty("summary")
    expect(r).toHaveProperty("cyclomatic_complexity")
    expect(r).toHaveProperty("max_nesting_depth")
    expect(r).toHaveProperty("security_issues")
    expect(r).toHaveProperty("code_smells")
    expect(r).toHaveProperty("overall_score")
  })

  test("cyclomatic_complexity has entries for all three functions", () => {
    const r = loadReport()
    expect(r.cyclomatic_complexity).toHaveProperty("get_user_data")
    expect(r.cyclomatic_complexity).toHaveProperty("process_file")
    expect(r.cyclomatic_complexity).toHaveProperty("calculate")
  })

  test("cyclomatic_complexity values are positive integers", () => {
    const r = loadReport()
    for (const fn of ["get_user_data", "process_file", "calculate"]) {
      const v = r.cyclomatic_complexity[fn]
      expect(typeof v).toBe("number")
      expect(Number.isInteger(v)).toBe(true)
      expect(v).toBeGreaterThanOrEqual(1)
    }
  })

  test("calculate function has higher cyclomatic complexity than simple functions", () => {
    const r = loadReport()
    expect(r.cyclomatic_complexity.calculate).toBeGreaterThan(r.cyclomatic_complexity.get_user_data)
  })

  test("max_nesting_depth for calculate is at least 5", () => {
    const r = loadReport()
    expect(r.max_nesting_depth).toHaveProperty("calculate")
    expect(r.max_nesting_depth.calculate).toBeGreaterThanOrEqual(5)
  })

  test("security_issues is array with at least 2 entries", () => {
    const r = loadReport()
    expect(Array.isArray(r.security_issues)).toBe(true)
    expect(r.security_issues.length).toBeGreaterThanOrEqual(2)
  })

  test("each security issue has function, issue, severity, recommendation fields", () => {
    const r = loadReport()
    const validSeverities = new Set(["high", "medium", "low"])
    for (const issue of r.security_issues) {
      expect(issue).toHaveProperty("function")
      expect(issue).toHaveProperty("issue")
      expect(issue).toHaveProperty("severity")
      expect(issue).toHaveProperty("recommendation")
      expect(validSeverities.has(issue.severity.toLowerCase())).toBe(true)
    }
  })

  test("SQL injection is identified as a security issue", () => {
    const r = loadReport()
    const issueText = r.security_issues.map((i: any) => (i.issue + " " + i.function).toLowerCase()).join(" ")
    const hasSqlInjection = issueText.includes("sql") || issueText.includes("injection") || issueText.includes("query")
    expect(hasSqlInjection).toBe(true)
  })

  test("unsafe deserialization (pickle) is identified as a security issue", () => {
    const r = loadReport()
    const issueText = r.security_issues.map((i: any) => (i.issue + " " + i.function).toLowerCase()).join(" ")
    const hasPickle = issueText.includes("pickle") || issueText.includes("deserializ") || issueText.includes("serial")
    expect(hasPickle).toBe(true)
  })

  test("overall_score is an integer between 1 and 10", () => {
    const r = loadReport()
    expect(typeof r.overall_score).toBe("number")
    expect(Number.isInteger(r.overall_score)).toBe(true)
    expect(r.overall_score).toBeGreaterThanOrEqual(1)
    expect(r.overall_score).toBeLessThanOrEqual(10)
  })

  test("overall_score reflects poor code quality (at most 5)", () => {
    const r = loadReport()
    expect(r.overall_score).toBeLessThanOrEqual(5)
  })
})

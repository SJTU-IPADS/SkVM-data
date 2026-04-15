import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("naming_report.json", "utf-8"))
}

describe("naming_report.json", () => {
  test("file exists", () => {
    expect(existsSync("naming_report.json")).toBe(true)
  })

  test("app.js source file was created", () => {
    expect(existsSync("app.js")).toBe(true)
  })

  test("valid JSON with required top-level fields", () => {
    const r = loadReport()
    expect(r).toHaveProperty("total_lines")
    expect(r).toHaveProperty("comment_lines")
    expect(r).toHaveProperty("comment_rate")
    expect(r).toHaveProperty("naming_style_violations")
    expect(r).toHaveProperty("dominant_naming_style")
    expect(r).toHaveProperty("comment_rating")
    expect(r).toHaveProperty("recommendations")
  })

  test("total_lines and comment_lines are positive integers", () => {
    const r = loadReport()
    expect(typeof r.total_lines).toBe("number")
    expect(Number.isInteger(r.total_lines)).toBe(true)
    expect(r.total_lines).toBeGreaterThan(0)
    expect(typeof r.comment_lines).toBe("number")
    expect(Number.isInteger(r.comment_lines)).toBe(true)
    expect(r.comment_lines).toBeGreaterThanOrEqual(0)
  })

  test("comment_rate is a number between 0 and 100", () => {
    const r = loadReport()
    expect(typeof r.comment_rate).toBe("number")
    expect(r.comment_rate).toBeGreaterThanOrEqual(0)
    expect(r.comment_rate).toBeLessThanOrEqual(100)
  })

  test("comment_rate is consistent with comment_lines and total_lines", () => {
    const r = loadReport()
    const expected = Math.round((r.comment_lines / r.total_lines) * 100 * 100) / 100
    expect(Math.abs(r.comment_rate - expected)).toBeLessThan(2)
  })

  test("naming_style_violations is array with at least 3 entries", () => {
    const r = loadReport()
    expect(Array.isArray(r.naming_style_violations)).toBe(true)
    expect(r.naming_style_violations.length).toBeGreaterThanOrEqual(3)
  })

  test("each violation has identifier, current_style, expected_style, suggestion fields", () => {
    const r = loadReport()
    const validStyles = new Set(["camelCase", "snake_case", "UPPER_SNAKE_CASE", "PascalCase"])
    for (const v of r.naming_style_violations) {
      expect(v).toHaveProperty("identifier")
      expect(v).toHaveProperty("current_style")
      expect(v).toHaveProperty("expected_style")
      expect(v).toHaveProperty("suggestion")
      expect(typeof v.identifier).toBe("string")
      expect(typeof v.suggestion).toBe("string")
    }
  })

  test("dominant_naming_style is a valid style string", () => {
    const r = loadReport()
    const validStyles = new Set(["camelCase", "snake_case", "PascalCase", "UPPER_SNAKE_CASE"])
    expect(validStyles.has(r.dominant_naming_style)).toBe(true)
  })

  test("comment_rating is a valid rating value", () => {
    const r = loadReport()
    const validRatings = new Set(["excellent", "good", "fair", "poor"])
    expect(validRatings.has(r.comment_rating.toLowerCase())).toBe(true)
  })

  test("recommendations is a non-empty array of strings", () => {
    const r = loadReport()
    expect(Array.isArray(r.recommendations)).toBe(true)
    expect(r.recommendations.length).toBeGreaterThanOrEqual(1)
    for (const rec of r.recommendations) {
      expect(typeof rec).toBe("string")
      expect(rec.length).toBeGreaterThan(0)
    }
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadData(): any {
  return JSON.parse(readFileSync("url_audit.json", "utf-8"))
}

const VALID_SEVERITIES = ["low", "medium", "high", "critical"]
const VALID_ISSUE_TYPES = ["duplicate_content", "mixed_case", "http_not_https", "parameter_duplicate", "underscore_vs_hyphen", "url_encoding"]

describe("url_audit.json", () => {
  test("file exists", () => {
    expect(existsSync("url_audit.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadData()).not.toThrow()
  })

  test("has required top-level keys", () => {
    const d = loadData()
    expect(d).toHaveProperty("total_urls")
    expect(d).toHaveProperty("unique_canonical_pages")
    expect(d).toHaveProperty("issues")
    expect(d).toHaveProperty("issue_types_found")
    expect(d).toHaveProperty("overall_score")
    expect(d).toHaveProperty("canonical_recommendations")
  })

  test("total_urls is 9", () => {
    const d = loadData()
    expect(d.total_urls).toBe(9)
  })

  test("issues is a non-empty array", () => {
    const d = loadData()
    expect(Array.isArray(d.issues)).toBe(true)
    expect(d.issues.length).toBeGreaterThan(0)
  })

  test("each issue has type, urls, severity, recommendation fields", () => {
    const d = loadData()
    for (const issue of d.issues) {
      expect(typeof issue.type).toBe("string")
      expect(Array.isArray(issue.urls)).toBe(true)
      expect(issue.urls.length).toBeGreaterThan(0)
      expect(typeof issue.severity).toBe("string")
      expect(typeof issue.recommendation).toBe("string")
      expect(issue.recommendation.length).toBeGreaterThan(5)
    }
  })

  test("severity values are valid (low, medium, high, or critical)", () => {
    const d = loadData()
    for (const issue of d.issues) {
      expect(VALID_SEVERITIES).toContain(issue.severity)
    }
  })

  test("issue_types_found has at least 4 entries", () => {
    const d = loadData()
    expect(Array.isArray(d.issue_types_found)).toBe(true)
    expect(d.issue_types_found.length).toBeGreaterThanOrEqual(4)
  })

  test("issue_types_found entries are valid type strings", () => {
    const d = loadData()
    for (const t of d.issue_types_found) {
      expect(typeof t).toBe("string")
      expect(t.length).toBeGreaterThan(0)
    }
  })

  test("overall_score is an integer between 0 and 10", () => {
    const d = loadData()
    expect(typeof d.overall_score).toBe("number")
    expect(d.overall_score).toBeGreaterThanOrEqual(0)
    expect(d.overall_score).toBeLessThanOrEqual(10)
    expect(Number.isInteger(d.overall_score)).toBe(true)
  })

  test("canonical_recommendations has at least 3 entries with valid URLs", () => {
    const d = loadData()
    expect(Array.isArray(d.canonical_recommendations)).toBe(true)
    expect(d.canonical_recommendations.length).toBeGreaterThanOrEqual(3)
    for (const url of d.canonical_recommendations) {
      expect(typeof url).toBe("string")
      expect(url).toMatch(/^https?:\/\//)
    }
  })
})

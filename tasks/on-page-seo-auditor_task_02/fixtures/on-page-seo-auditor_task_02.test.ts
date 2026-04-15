import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadAudit(): any {
  return JSON.parse(readFileSync("header_audit.json", "utf-8"))
}

describe("header_audit.json", () => {
  test("file exists", () => {
    expect(existsSync("header_audit.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadAudit()).not.toThrow()
  })

  test("target_keyword is home office ergonomic chair", () => {
    const a = loadAudit()
    expect(a.target_keyword).toBe("home office ergonomic chair")
  })

  test("header_analysis has required fields", () => {
    const a = loadAudit()
    expect(a).toHaveProperty("header_analysis")
    const ha = a.header_analysis
    expect(ha).toHaveProperty("h1_count")
    expect(ha).toHaveProperty("h1_contains_keyword")
    expect(ha).toHaveProperty("h2_count")
    expect(ha).toHaveProperty("h2_keyword_count")
    expect(ha).toHaveProperty("hierarchy_valid")
    expect(ha).toHaveProperty("header_score")
  })

  test("h1_count is 1 and h2_count is 4", () => {
    const a = loadAudit()
    expect(a.header_analysis.h1_count).toBe(1)
    expect(a.header_analysis.h2_count).toBe(4)
  })

  test("h1_contains_keyword is false and hierarchy_valid is boolean", () => {
    const a = loadAudit()
    expect(a.header_analysis.h1_contains_keyword).toBe(false)
    expect(typeof a.header_analysis.hierarchy_valid).toBe("boolean")
  })

  test("header_score is integer 0-10", () => {
    const a = loadAudit()
    const s = a.header_analysis.header_score
    expect(Number.isInteger(s)).toBe(true)
    expect(s).toBeGreaterThanOrEqual(0)
    expect(s).toBeLessThanOrEqual(10)
  })

  test("keyword_placement has required fields", () => {
    const a = loadAudit()
    expect(a).toHaveProperty("keyword_placement")
    const kp = a.keyword_placement
    expect(kp).toHaveProperty("in_title")
    expect(kp).toHaveProperty("in_h1")
    expect(kp).toHaveProperty("in_meta")
    expect(kp).toHaveProperty("in_first_paragraph")
    expect(kp).toHaveProperty("keyword_score")
  })

  test("in_title and in_meta are false", () => {
    const a = loadAudit()
    expect(a.keyword_placement.in_title).toBe(false)
    expect(a.keyword_placement.in_meta).toBe(false)
  })

  test("at least 3 priority fixes", () => {
    const a = loadAudit()
    expect(Array.isArray(a.priority_fixes)).toBe(true)
    expect(a.priority_fixes.length).toBeGreaterThanOrEqual(3)
  })

  test("each fix has priority, element, current, and suggested fields", () => {
    const a = loadAudit()
    for (const fix of a.priority_fixes) {
      expect(fix).toHaveProperty("priority")
      expect(fix).toHaveProperty("element")
      expect(fix).toHaveProperty("current")
      expect(fix).toHaveProperty("suggested")
      expect(typeof fix.priority).toBe("number")
    }
  })

  test("fixes are sorted by priority ascending (1 = highest)", () => {
    const a = loadAudit()
    const priorities = a.priority_fixes.map((f: any) => f.priority)
    for (let i = 1; i < priorities.length; i++) {
      expect(priorities[i]).toBeGreaterThanOrEqual(priorities[i - 1])
    }
  })

  test("overall_score is integer 0-10", () => {
    const a = loadAudit()
    expect(a).toHaveProperty("overall_score")
    expect(Number.isInteger(a.overall_score)).toBe(true)
    expect(a.overall_score).toBeGreaterThanOrEqual(0)
    expect(a.overall_score).toBeLessThanOrEqual(10)
  })
})

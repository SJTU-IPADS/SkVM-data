import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadAnalysis(): any {
  return JSON.parse(readFileSync("copy_analysis.json", "utf-8"))
}

describe("copy_analysis.json", () => {
  test("file exists", () => {
    expect(existsSync("copy_analysis.json")).toBe(true)
  })

  test("parses as valid JSON", () => {
    expect(() => loadAnalysis()).not.toThrow()
  })

  test("has all required fields: ai_tone_issues, main_rewrite, alternative_version, risk_safe_swaps", () => {
    const d = loadAnalysis()
    expect(d).toHaveProperty("ai_tone_issues")
    expect(d).toHaveProperty("main_rewrite")
    expect(d).toHaveProperty("alternative_version")
    expect(d).toHaveProperty("risk_safe_swaps")
  })

  test("ai_tone_issues is an array with at least 2 entries", () => {
    const d = loadAnalysis()
    expect(Array.isArray(d.ai_tone_issues)).toBe(true)
    expect(d.ai_tone_issues.length).toBeGreaterThanOrEqual(2)
  })

  test("each ai_tone_issues entry is a non-empty string", () => {
    const d = loadAnalysis()
    for (const issue of d.ai_tone_issues) {
      expect(typeof issue).toBe("string")
      expect(issue.length).toBeGreaterThan(0)
    }
  })

  test("main_rewrite is a non-empty string", () => {
    const d = loadAnalysis()
    expect(typeof d.main_rewrite).toBe("string")
    expect(d.main_rewrite.length).toBeGreaterThan(10)
  })

  test("alternative_version is a non-empty string", () => {
    const d = loadAnalysis()
    expect(typeof d.alternative_version).toBe("string")
    expect(d.alternative_version.length).toBeGreaterThan(10)
  })

  test("risk_safe_swaps is an array with at least 1 entry", () => {
    const d = loadAnalysis()
    expect(Array.isArray(d.risk_safe_swaps)).toBe(true)
    expect(d.risk_safe_swaps.length).toBeGreaterThanOrEqual(1)
  })

  test("each risk_safe_swaps entry has 'original' and 'replacement' fields", () => {
    const d = loadAnalysis()
    for (const swap of d.risk_safe_swaps) {
      expect(swap).toHaveProperty("original")
      expect(swap).toHaveProperty("replacement")
      expect(typeof swap.original).toBe("string")
      expect(typeof swap.replacement).toBe("string")
    }
  })

  test("main_rewrite and alternative_version are different", () => {
    const d = loadAnalysis()
    expect(d.main_rewrite).not.toBe(d.alternative_version)
  })
})

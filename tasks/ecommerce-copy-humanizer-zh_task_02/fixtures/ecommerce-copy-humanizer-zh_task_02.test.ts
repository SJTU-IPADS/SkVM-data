import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadScript(): any {
  return JSON.parse(readFileSync("humanized_script.json", "utf-8"))
}

describe("humanized_script.json", () => {
  test("file exists", () => {
    expect(existsSync("humanized_script.json")).toBe(true)
  })

  test("parses as valid JSON", () => {
    expect(() => loadScript()).not.toThrow()
  })

  test("has all required fields: ai_tone_issues, main_rewrite, alternative_version, risk_safe_swaps", () => {
    const d = loadScript()
    expect(d).toHaveProperty("ai_tone_issues")
    expect(d).toHaveProperty("main_rewrite")
    expect(d).toHaveProperty("alternative_version")
    expect(d).toHaveProperty("risk_safe_swaps")
  })

  test("ai_tone_issues has at least 2 entries", () => {
    const d = loadScript()
    expect(Array.isArray(d.ai_tone_issues)).toBe(true)
    expect(d.ai_tone_issues.length).toBeGreaterThanOrEqual(2)
  })

  test("main_rewrite is at least 50 characters long", () => {
    const d = loadScript()
    expect(typeof d.main_rewrite).toBe("string")
    expect(d.main_rewrite.length).toBeGreaterThanOrEqual(50)
  })

  test("alternative_version is a non-empty string", () => {
    const d = loadScript()
    expect(typeof d.alternative_version).toBe("string")
    expect(d.alternative_version.length).toBeGreaterThan(10)
  })

  test("main_rewrite does not contain prohibited phrases (临床验证 or 医学证明)", () => {
    const d = loadScript()
    expect(d.main_rewrite).not.toContain("临床验证")
    expect(d.main_rewrite).not.toContain("医学证明")
  })

  test("alternative_version does not contain prohibited phrases", () => {
    const d = loadScript()
    expect(d.alternative_version).not.toContain("临床验证")
    expect(d.alternative_version).not.toContain("医学证明")
  })

  test("risk_safe_swaps has at least 2 entries", () => {
    const d = loadScript()
    expect(Array.isArray(d.risk_safe_swaps)).toBe(true)
    expect(d.risk_safe_swaps.length).toBeGreaterThanOrEqual(2)
  })

  test("each risk_safe_swaps entry has original, replacement, and reason fields", () => {
    const d = loadScript()
    for (const swap of d.risk_safe_swaps) {
      expect(swap).toHaveProperty("original")
      expect(swap).toHaveProperty("replacement")
      expect(swap).toHaveProperty("reason")
      expect(typeof swap.original).toBe("string")
      expect(typeof swap.replacement).toBe("string")
      expect(typeof swap.reason).toBe("string")
    }
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadComparison(): any {
  return JSON.parse(readFileSync("build_comparison.json", "utf-8"))
}

describe("build_comparison.json", () => {
  test("file exists", () => {
    expect(existsSync("build_comparison.json")).toBe(true)
  })

  test("parses as valid JSON", () => {
    expect(() => loadComparison()).not.toThrow()
  })

  test("has all required fields: winner, config_a_score, config_b_score, config_a_strengths, config_a_weaknesses, config_b_strengths, config_b_weaknesses, missing_in_both", () => {
    const r = loadComparison()
    expect(r).toHaveProperty("winner")
    expect(r).toHaveProperty("config_a_score")
    expect(r).toHaveProperty("config_b_score")
    expect(r).toHaveProperty("config_a_strengths")
    expect(r).toHaveProperty("config_a_weaknesses")
    expect(r).toHaveProperty("config_b_strengths")
    expect(r).toHaveProperty("config_b_weaknesses")
    expect(r).toHaveProperty("missing_in_both")
  })

  test("winner is 'B'", () => {
    const r = loadComparison()
    expect(r.winner).toBe("B")
  })

  test("config_a_score and config_b_score are integers in range 0-100", () => {
    const r = loadComparison()
    expect(typeof r.config_a_score).toBe("number")
    expect(typeof r.config_b_score).toBe("number")
    expect(r.config_a_score).toBeGreaterThanOrEqual(0)
    expect(r.config_a_score).toBeLessThanOrEqual(100)
    expect(r.config_b_score).toBeGreaterThanOrEqual(0)
    expect(r.config_b_score).toBeLessThanOrEqual(100)
  })

  test("config_b_score is higher than config_a_score", () => {
    const r = loadComparison()
    expect(r.config_b_score).toBeGreaterThan(r.config_a_score)
  })

  test("config_a_weaknesses has at least 2 entries", () => {
    const r = loadComparison()
    expect(Array.isArray(r.config_a_weaknesses)).toBe(true)
    expect(r.config_a_weaknesses.length).toBeGreaterThanOrEqual(2)
  })

  test("config_b_strengths has at least 3 entries", () => {
    const r = loadComparison()
    expect(Array.isArray(r.config_b_strengths)).toBe(true)
    expect(r.config_b_strengths.length).toBeGreaterThanOrEqual(3)
  })

  test("missing_in_both has at least 2 entries", () => {
    const r = loadComparison()
    expect(Array.isArray(r.missing_in_both)).toBe(true)
    expect(r.missing_in_both.length).toBeGreaterThanOrEqual(2)
  })

  test("all array entries are non-empty strings", () => {
    const r = loadComparison()
    const arrays = [r.config_a_strengths, r.config_a_weaknesses, r.config_b_strengths, r.config_b_weaknesses, r.missing_in_both]
    for (const arr of arrays) {
      expect(Array.isArray(arr)).toBe(true)
      for (const item of arr) {
        expect(typeof item).toBe("string")
        expect(item.length).toBeGreaterThan(0)
      }
    }
  })
})

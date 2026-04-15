import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadMatrix(): any {
  return JSON.parse(readFileSync("strategic_options_matrix.json", "utf-8"))
}

function loadSummary(): string {
  return readFileSync("ceo_decision_summary.md", "utf-8")
}

describe("strategic_options_matrix.json", () => {
  test("file exists", () => {
    expect(existsSync("strategic_options_matrix.json")).toBe(true)
  })

  test("is valid JSON with required top-level keys", () => {
    const m = loadMatrix()
    expect(m).toHaveProperty("company_snapshot")
    expect(m).toHaveProperty("options")
    expect(m).toHaveProperty("recommended_option")
    expect(m).toHaveProperty("rationale")
  })

  test("company_snapshot has correct values", () => {
    const m = loadMatrix()
    const cs = m.company_snapshot
    expect(typeof cs.arr).toBe("number")
    expect(typeof cs.runway_months).toBe("number")
    expect(typeof cs.headcount).toBe("number")
    expect(typeof cs.arr_growth_pct).toBe("number")
    // Values must reflect the prompt data
    expect(cs.runway_months).toBe(18)
    expect(cs.headcount).toBe(12)
  })

  test("options array has exactly 3 entries", () => {
    const m = loadMatrix()
    expect(Array.isArray(m.options)).toBe(true)
    expect(m.options.length).toBe(3)
  })

  test("each option has required fields with correct types", () => {
    const m = loadMatrix()
    const validLevels = ["low", "medium", "high"]
    for (const opt of m.options) {
      expect(typeof opt.name).toBe("string")
      expect(typeof opt.investment_usd).toBe("number")
      expect(typeof opt.payback_months).toBe("number")
      expect(validLevels).toContain(opt.risk_level)
      expect(validLevels).toContain(opt.upside)
      expect(typeof opt.recommendation_score).toBe("number")
      expect(opt.recommendation_score).toBeGreaterThanOrEqual(1)
      expect(opt.recommendation_score).toBeLessThanOrEqual(10)
    }
  })

  test("investment values match prompt data", () => {
    const m = loadMatrix()
    const investments = m.options.map((o: any) => o.investment_usd).sort((a: number, b: number) => a - b)
    expect(investments).toContain(200000)
    expect(investments).toContain(300000)
    expect(investments).toContain(500000)
  })

  test("recommended_option matches highest-scored option", () => {
    const m = loadMatrix()
    const maxScore = Math.max(...m.options.map((o: any) => o.recommendation_score))
    const topOption = m.options.find((o: any) => o.recommendation_score === maxScore)
    expect(m.recommended_option).toBe(topOption.name)
  })

  test("rationale is a non-empty string between 50 and 200 words", () => {
    const m = loadMatrix()
    expect(typeof m.rationale).toBe("string")
    const wordCount = m.rationale.trim().split(/\s+/).length
    expect(wordCount).toBeGreaterThanOrEqual(50)
    expect(wordCount).toBeLessThanOrEqual(200)
  })
})

describe("ceo_decision_summary.md", () => {
  test("file exists", () => {
    expect(existsSync("ceo_decision_summary.md")).toBe(true)
  })

  test("summary is at least 150 words", () => {
    const text = loadSummary()
    const wordCount = text.trim().split(/\s+/).length
    expect(wordCount).toBeGreaterThanOrEqual(150)
  })

  test("summary mentions all three options", () => {
    const text = loadSummary().toLowerCase()
    expect(text).toMatch(/european|europe/)
    expect(text).toMatch(/enterprise/)
    expect(text).toMatch(/marketplace|partner|ecosystem/)
  })
})

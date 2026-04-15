import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadAnalysis(): any {
  return JSON.parse(readFileSync("build_vs_buy_analysis.json", "utf-8"))
}

describe("build_vs_buy_analysis.json", () => {
  test("file exists", () => {
    expect(existsSync("build_vs_buy_analysis.json")).toBe(true)
  })

  test("is valid JSON with required top-level keys", () => {
    const a = loadAnalysis()
    expect(a).toHaveProperty("decision_context")
    expect(a).toHaveProperty("options")
    expect(a).toHaveProperty("scores")
    expect(a).toHaveProperty("recommendation")
    expect(a).toHaveProperty("rationale")
  })

  test("decision_context has correct values", () => {
    const a = loadAnalysis()
    const dc = a.decision_context
    expect(dc.current_users).toBe(50000)
    expect(dc.projected_users).toBe(200000)
    expect(dc.team_size).toBe(8)
    expect(dc.engineering_day_cost_usd).toBe(800)
  })

  test("options array has exactly 3 entries with required fields", () => {
    const a = loadAnalysis()
    expect(Array.isArray(a.options)).toBe(true)
    expect(a.options.length).toBe(3)
    const validRisks = ["none", "low", "medium", "high"]
    for (const opt of a.options) {
      expect(typeof opt.name).toBe("string")
      expect(typeof opt.initial_cost_usd).toBe("number")
      expect(typeof opt.annual_infra_cost_usd).toBe("number")
      expect(typeof opt.annual_maintenance_cost_usd).toBe("number")
      expect(typeof opt.three_year_tco_usd).toBe("number")
      expect(typeof opt.integration_effort_days).toBe("number")
      expect(validRisks).toContain(opt.vendor_dependency_risk)
    }
  })

  test("Option A (Build) 3-year TCO is approximately $100,800 (±5%)", () => {
    const a = loadAnalysis()
    const buildOpt = a.options.find((o: any) =>
      o.name.toLowerCase().includes("build") || o.name.toLowerCase().includes("in-house")
    )
    expect(buildOpt).toBeDefined()
    // Expected: $100,800
    expect(buildOpt.three_year_tco_usd).toBeGreaterThanOrEqual(95760)
    expect(buildOpt.three_year_tco_usd).toBeLessThanOrEqual(105840)
  })

  test("Option B (Vendor) 3-year TCO is approximately $50,400 (±5%)", () => {
    const a = loadAnalysis()
    const vendorOpt = a.options.find((o: any) =>
      o.name.toLowerCase().includes("vendor") ||
      o.name.toLowerCase().includes("sendgrid") ||
      o.name.toLowerCase().includes("twilio")
    )
    expect(vendorOpt).toBeDefined()
    // Expected: $50,400
    expect(vendorOpt.three_year_tco_usd).toBeGreaterThanOrEqual(47880)
    expect(vendorOpt.three_year_tco_usd).toBeLessThanOrEqual(52920)
  })

  test("Option C (Open source) 3-year TCO is approximately $43,200 (±5%)", () => {
    const a = loadAnalysis()
    const openSourceOpt = a.options.find((o: any) =>
      o.name.toLowerCase().includes("open source") ||
      o.name.toLowerCase().includes("novu") ||
      o.name.toLowerCase().includes("self-host")
    )
    expect(openSourceOpt).toBeDefined()
    // Expected: $43,200
    expect(openSourceOpt.three_year_tco_usd).toBeGreaterThanOrEqual(41040)
    expect(openSourceOpt.three_year_tco_usd).toBeLessThanOrEqual(45360)
  })

  test("scores array has 3 entries with weighted_score values 0-10", () => {
    const a = loadAnalysis()
    expect(Array.isArray(a.scores)).toBe(true)
    expect(a.scores.length).toBe(3)
    for (const s of a.scores) {
      expect(typeof s.name).toBe("string")
      expect(typeof s.weighted_score).toBe("number")
      expect(s.weighted_score).toBeGreaterThanOrEqual(0)
      expect(s.weighted_score).toBeLessThanOrEqual(10)
    }
  })

  test("recommendation matches highest weighted_score option", () => {
    const a = loadAnalysis()
    const maxScore = Math.max(...a.scores.map((s: any) => s.weighted_score))
    const topOption = a.scores.find((s: any) => s.weighted_score === maxScore)
    expect(typeof a.recommendation).toBe("string")
    expect(a.recommendation.toLowerCase()).toContain(topOption.name.toLowerCase().split(" ")[0])
  })

  test("rationale is a string of 50-150 words", () => {
    const a = loadAnalysis()
    expect(typeof a.rationale).toBe("string")
    const words = a.rationale.trim().split(/\s+/).length
    expect(words).toBeGreaterThanOrEqual(50)
    expect(words).toBeLessThanOrEqual(150)
  })
})

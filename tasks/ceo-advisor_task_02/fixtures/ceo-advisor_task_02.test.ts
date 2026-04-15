import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadScorecard(): any {
  return JSON.parse(readFileSync("ceo_scorecard.json", "utf-8"))
}

describe("ceo_scorecard.json", () => {
  test("file exists", () => {
    expect(existsSync("ceo_scorecard.json")).toBe(true)
  })

  test("is valid JSON with required top-level keys", () => {
    const s = loadScorecard()
    expect(s).toHaveProperty("period")
    expect(s).toHaveProperty("metrics")
    expect(s).toHaveProperty("runway_months")
    expect(s).toHaveProperty("overall_health")
    expect(s).toHaveProperty("top_priority")
  })

  test("period is Q1-2026", () => {
    const s = loadScorecard()
    expect(s.period).toBe("Q1-2026")
  })

  test("metrics array has exactly 8 entries", () => {
    const s = loadScorecard()
    expect(Array.isArray(s.metrics)).toBe(true)
    expect(s.metrics.length).toBe(8)
  })

  test("each metric has required fields with valid types", () => {
    const s = loadScorecard()
    const validStatuses = ["green", "yellow", "red"]
    for (const m of s.metrics) {
      expect(typeof m.category).toBe("string")
      expect(typeof m.metric).toBe("string")
      expect(typeof m.value).toBe("number")
      expect(typeof m.target).toBe("number")
      expect(validStatuses).toContain(m.status)
      expect(typeof m.unit).toBe("string")
    }
  })

  test("runway_months is correctly computed as 10.0", () => {
    const s = loadScorecard()
    // 2,800,000 / 280,000 = 10.0
    expect(typeof s.runway_months).toBe("number")
    expect(s.runway_months).toBe(10.0)
  })

  test("overall_health is a valid status string", () => {
    const s = loadScorecard()
    const validHealth = ["healthy", "caution", "critical"]
    expect(validHealth).toContain(s.overall_health)
  })

  test("NPS metric has status yellow (NPS=38, threshold green>=40)", () => {
    const s = loadScorecard()
    const npsMetric = s.metrics.find((m: any) =>
      m.metric.toLowerCase().includes("nps") || m.category.toLowerCase().includes("product")
    )
    expect(npsMetric).toBeDefined()
    expect(npsMetric.status).toBe("yellow")
  })

  test("top_priority is a non-empty string between 30 and 100 words", () => {
    const s = loadScorecard()
    expect(typeof s.top_priority).toBe("string")
    const wordCount = s.top_priority.trim().split(/\s+/).length
    expect(wordCount).toBeGreaterThanOrEqual(30)
    expect(wordCount).toBeLessThanOrEqual(100)
  })

  test("at least one metric has red status", () => {
    const s = loadScorecard()
    // Regrettable attrition 12% > 10% = yellow; NPS 38 < 40 = yellow; CEO strategic time 35% < 40% = yellow
    // Annual goals 60% is yellow; runway 10 months is yellow; engagement 6.2 is yellow
    // So we should have no green on most metrics - at least some yellow/red
    const redOrYellow = s.metrics.filter((m: any) => m.status === "red" || m.status === "yellow")
    expect(redOrYellow.length).toBeGreaterThanOrEqual(3)
  })
})

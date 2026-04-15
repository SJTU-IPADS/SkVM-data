import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadLandscape(): any {
  return JSON.parse(readFileSync("competitor_landscape.json", "utf-8"))
}

describe("competitor_landscape.json", () => {
  test("file exists", () => {
    expect(existsSync("competitor_landscape.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const l = loadLandscape()
    expect(l).toHaveProperty("market")
    expect(l).toHaveProperty("competitors")
    expect(l).toHaveProperty("positioning_gaps")
    expect(l).toHaveProperty("pricing_summary")
    expect(l).toHaveProperty("go_no_go")
  })

  test("competitors is an array of exactly 5 entries", () => {
    const l = loadLandscape()
    expect(Array.isArray(l.competitors)).toBe(true)
    expect(l.competitors.length).toBe(5)
  })

  test("each competitor has required fields with valid types", () => {
    const validTypes = new Set(["direct", "indirect", "substitute"])
    const l = loadLandscape()
    for (const c of l.competitors) {
      expect(c).toHaveProperty("name")
      expect(c).toHaveProperty("type")
      expect(c).toHaveProperty("price_per_serving_usd")
      expect(c).toHaveProperty("target_segment")
      expect(c).toHaveProperty("strengths")
      expect(c).toHaveProperty("weaknesses")
      expect(validTypes.has(c.type)).toBe(true)
      expect(typeof c.price_per_serving_usd).toBe("number")
      expect(c.price_per_serving_usd).toBeGreaterThan(0)
    }
  })

  test("each competitor has at least 2 strengths and 2 weaknesses", () => {
    const l = loadLandscape()
    for (const c of l.competitors) {
      expect(Array.isArray(c.strengths)).toBe(true)
      expect(c.strengths.length).toBeGreaterThanOrEqual(2)
      expect(Array.isArray(c.weaknesses)).toBe(true)
      expect(c.weaknesses.length).toBeGreaterThanOrEqual(2)
    }
  })

  test("positioning_gaps has at least 3 entries with required fields", () => {
    const validSizes = new Set(["small", "medium", "large"])
    const l = loadLandscape()
    expect(Array.isArray(l.positioning_gaps)).toBe(true)
    expect(l.positioning_gaps.length).toBeGreaterThanOrEqual(3)
    for (const g of l.positioning_gaps) {
      expect(g).toHaveProperty("gap")
      expect(g).toHaveProperty("evidence")
      expect(g).toHaveProperty("opportunity_size")
      expect(validSizes.has(g.opportunity_size)).toBe(true)
    }
  })

  test("pricing_summary has all required fields with positive numbers", () => {
    const ps = loadLandscape().pricing_summary
    expect(ps).toHaveProperty("market_low_usd")
    expect(ps).toHaveProperty("market_high_usd")
    expect(ps).toHaveProperty("recommended_entry_price_usd")
    expect(ps).toHaveProperty("pricing_rationale")
    expect(ps.market_low_usd).toBeGreaterThan(0)
    expect(ps.market_high_usd).toBeGreaterThan(ps.market_low_usd)
  })

  test("recommended_entry_price is within market range", () => {
    const ps = loadLandscape().pricing_summary
    expect(ps.recommended_entry_price_usd).toBeGreaterThanOrEqual(ps.market_low_usd)
    expect(ps.recommended_entry_price_usd).toBeLessThanOrEqual(ps.market_high_usd)
  })

  test("go_no_go has decision, conditions, and key_risk", () => {
    const gng = loadLandscape().go_no_go
    expect(gng).toHaveProperty("decision")
    expect(gng).toHaveProperty("conditions")
    expect(gng).toHaveProperty("key_risk")
    expect(["go", "no-go", "conditional"]).toContain(gng.decision)
    expect(Array.isArray(gng.conditions)).toBe(true)
    expect(typeof gng.key_risk).toBe("string")
    expect(gng.key_risk.length).toBeGreaterThan(10)
  })
})

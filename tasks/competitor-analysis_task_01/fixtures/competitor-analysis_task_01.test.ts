import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("competitor_analysis.json", "utf-8"))
}

describe("competitor_analysis.json", () => {
  test("file exists", () => {
    expect(existsSync("competitor_analysis.json")).toBe(true)
  })

  test("valid JSON with required top-level fields", () => {
    const r = loadReport()
    expect(r).toHaveProperty("my_site")
    expect(r).toHaveProperty("competitors")
    expect(r).toHaveProperty("traffic_leader")
    expect(r).toHaveProperty("keyword_opportunities")
    expect(r).toHaveProperty("strengths")
    expect(r).toHaveProperty("weaknesses")
    expect(r).toHaveProperty("action_plan")
  })

  test("my_site is techblog.example.com", () => {
    const r = loadReport()
    expect(r.my_site).toBe("techblog.example.com")
  })

  test("competitors array has exactly 2 entries", () => {
    const r = loadReport()
    expect(Array.isArray(r.competitors)).toBe(true)
    expect(r.competitors.length).toBe(2)
  })

  test("each competitor has domain, traffic_gap, keyword_gap, da_gap, top_content_topics", () => {
    const r = loadReport()
    for (const c of r.competitors) {
      expect(c).toHaveProperty("domain")
      expect(c).toHaveProperty("traffic_gap")
      expect(c).toHaveProperty("keyword_gap")
      expect(c).toHaveProperty("da_gap")
      expect(c).toHaveProperty("top_content_topics")
      expect(Array.isArray(c.top_content_topics)).toBe(true)
    }
  })

  test("devhints competitor has correct traffic_gap of 36800", () => {
    const r = loadReport()
    const devhints = r.competitors.find((c: any) => c.domain.includes("devhints"))
    expect(devhints).toBeDefined()
    expect(devhints.traffic_gap).toBe(36800)
  })

  test("devhints competitor has correct keyword_gap of 1510", () => {
    const r = loadReport()
    const devhints = r.competitors.find((c: any) => c.domain.includes("devhints"))
    expect(devhints).toBeDefined()
    expect(devhints.keyword_gap).toBe(1510)
  })

  test("codelearn competitor has correct traffic_gap of 13800", () => {
    const r = loadReport()
    const codelearn = r.competitors.find((c: any) => c.domain.includes("codelearn"))
    expect(codelearn).toBeDefined()
    expect(codelearn.traffic_gap).toBe(13800)
  })

  test("traffic_leader is devhints.example.com (highest traffic site)", () => {
    const r = loadReport()
    expect(r.traffic_leader).toContain("devhints")
  })

  test("keyword_opportunities has at least 4 entries", () => {
    const r = loadReport()
    expect(Array.isArray(r.keyword_opportunities)).toBe(true)
    expect(r.keyword_opportunities.length).toBeGreaterThanOrEqual(4)
  })

  test("action_plan has immediate, short_term, and long_term arrays", () => {
    const r = loadReport()
    expect(r.action_plan).toHaveProperty("immediate")
    expect(r.action_plan).toHaveProperty("short_term")
    expect(r.action_plan).toHaveProperty("long_term")
    expect(Array.isArray(r.action_plan.immediate)).toBe(true)
    expect(Array.isArray(r.action_plan.short_term)).toBe(true)
    expect(Array.isArray(r.action_plan.long_term)).toBe(true)
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("format_gap_report.json", "utf-8"))
}

// Expected data for exact value checks
const MY_COUNTS: Record<string, number> = {
  "Blog posts": 45, "How-to guides": 8, "Case studies": 2,
  "Comparison pages": 1, "Templates": 0, "Video tutorials": 0,
  "Webinars": 3, "Whitepapers": 1, "Calculators/Tools": 0
}

const INDUSTRY_AVG: Record<string, number> = {
  "Blog posts": 38, "How-to guides": 22, "Case studies": 14,
  "Comparison pages": 8, "Templates": 18, "Video tutorials": 12,
  "Webinars": 6, "Whitepapers": 9, "Calculators/Tools": 5
}

describe("format_gap_report.json", () => {
  test("file exists", () => {
    expect(existsSync("format_gap_report.json")).toBe(true)
  })

  test("valid JSON with required top-level fields", () => {
    const r = loadReport()
    expect(r).toHaveProperty("site")
    expect(r).toHaveProperty("format_analysis")
    expect(r).toHaveProperty("critical_gaps")
    expect(r).toHaveProperty("missing_formats")
    expect(r).toHaveProperty("strengths")
    expect(r).toHaveProperty("top_priority_recommendation")
    expect(r).toHaveProperty("audience_journey_gaps")
  })

  test("site is accountpro.example.com", () => {
    const r = loadReport()
    expect(r.site).toBe("accountpro.example.com")
  })

  test("format_analysis has exactly 9 entries for all format types", () => {
    const r = loadReport()
    expect(Array.isArray(r.format_analysis)).toBe(true)
    expect(r.format_analysis.length).toBe(9)
  })

  test("each format entry has format, my_count, industry_avg, gap, gap_pct, status fields", () => {
    const r = loadReport()
    const validStatuses = new Set(["above_average", "at_average", "below_average", "missing"])
    for (const f of r.format_analysis) {
      expect(f).toHaveProperty("format")
      expect(f).toHaveProperty("my_count")
      expect(f).toHaveProperty("industry_avg")
      expect(f).toHaveProperty("gap")
      expect(f).toHaveProperty("gap_pct")
      expect(f).toHaveProperty("status")
      expect(validStatuses.has(f.status)).toBe(true)
    }
  })

  test("blog posts are marked above_average (45 vs industry avg 38)", () => {
    const r = loadReport()
    const blogEntry = r.format_analysis.find((f: any) =>
      f.format.toLowerCase().includes("blog"))
    expect(blogEntry).toBeDefined()
    expect(blogEntry.status).toBe("above_average")
    expect(blogEntry.gap).toBeLessThan(0)
  })

  test("missing formats include templates, video tutorials, and calculators", () => {
    const r = loadReport()
    expect(Array.isArray(r.missing_formats)).toBe(true)
    const missingLower = r.missing_formats.map((m: string) => m.toLowerCase())
    const hasTemplates = missingLower.some((m: string) => m.includes("template"))
    const hasVideo = missingLower.some((m: string) => m.includes("video"))
    const hasCalc = missingLower.some((m: string) => m.includes("calculat"))
    expect(hasTemplates).toBe(true)
    expect(hasVideo).toBe(true)
    expect(hasCalc).toBe(true)
  })

  test("critical_gaps includes formats with gap >= 10 (how-to guides gap=14, case studies gap=12, templates gap=18, video tutorials gap=12)", () => {
    const r = loadReport()
    expect(Array.isArray(r.critical_gaps)).toBe(true)
    const critLower = r.critical_gaps.map((c: string) => c.toLowerCase())
    const hasTemplates = critLower.some((c: string) => c.includes("template"))
    expect(hasTemplates).toBe(true)
    expect(r.critical_gaps.length).toBeGreaterThanOrEqual(3)
  })

  test("strengths includes blog posts", () => {
    const r = loadReport()
    expect(Array.isArray(r.strengths)).toBe(true)
    const strengthsLower = r.strengths.map((s: string) => s.toLowerCase())
    const hasBlog = strengthsLower.some((s: string) => s.includes("blog"))
    expect(hasBlog).toBe(true)
  })

  test("audience_journey_gaps has awareness, consideration, decision keys with arrays", () => {
    const r = loadReport()
    expect(r.audience_journey_gaps).toHaveProperty("awareness")
    expect(r.audience_journey_gaps).toHaveProperty("consideration")
    expect(r.audience_journey_gaps).toHaveProperty("decision")
    expect(Array.isArray(r.audience_journey_gaps.awareness)).toBe(true)
    expect(Array.isArray(r.audience_journey_gaps.consideration)).toBe(true)
    expect(Array.isArray(r.audience_journey_gaps.decision)).toBe(true)
  })

  test("top_priority_recommendation is a non-empty string", () => {
    const r = loadReport()
    expect(typeof r.top_priority_recommendation).toBe("string")
    expect(r.top_priority_recommendation.length).toBeGreaterThan(20)
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("audit_report.json", "utf-8"))
}

function loadSummary(): string {
  return readFileSync("audit_summary.md", "utf-8")
}

describe("audit_report.json", () => {
  test("file exists", () => {
    expect(existsSync("audit_report.json")).toBe(true)
  })

  test("is valid JSON with required top-level keys", () => {
    const r = loadReport()
    expect(r).toHaveProperty("content_title")
    expect(r).toHaveProperty("content_type")
    expect(r).toHaveProperty("veto_check")
    expect(r).toHaveProperty("dimension_scores")
    expect(r).toHaveProperty("geo_score")
    expect(r).toHaveProperty("seo_score")
    expect(r).toHaveProperty("total_score")
    expect(r).toHaveProperty("top_improvements")
    expect(r).toHaveProperty("rating")
  })

  test("content_type is Blog Post", () => {
    const r = loadReport()
    expect(r.content_type).toBe("Blog Post")
  })

  test("veto_check has correct structure and valid values", () => {
    const r = loadReport()
    const vc = r.veto_check
    const valid = ["Pass", "Partial", "Fail"]
    expect(valid).toContain(vc.T04_disclosure)
    expect(valid).toContain(vc.C01_intent_alignment)
    expect(valid).toContain(vc.R10_content_consistency)
    expect(typeof vc.any_veto_triggered).toBe("boolean")
  })

  test("dimension_scores has all 8 required keys with values 0-100", () => {
    const r = loadReport()
    const ds = r.dimension_scores
    const dims = ["C", "O", "R", "E", "Exp", "Ept", "A", "T"]
    for (const d of dims) {
      expect(ds).toHaveProperty(d)
      expect(typeof ds[d]).toBe("number")
      expect(ds[d]).toBeGreaterThanOrEqual(0)
      expect(ds[d]).toBeLessThanOrEqual(100)
    }
  })

  test("geo_score is average of C, O, R, E (within 1 point tolerance)", () => {
    const r = loadReport()
    const ds = r.dimension_scores
    const expected = (ds.C + ds.O + ds.R + ds.E) / 4
    expect(Math.abs(r.geo_score - expected)).toBeLessThanOrEqual(1)
  })

  test("seo_score is average of Exp, Ept, A, T (within 1 point tolerance)", () => {
    const r = loadReport()
    const ds = r.dimension_scores
    const expected = (ds.Exp + ds.Ept + ds.A + ds.T) / 4
    expect(Math.abs(r.seo_score - expected)).toBeLessThanOrEqual(1)
  })

  test("total_score is a number between 0 and 100", () => {
    const r = loadReport()
    expect(typeof r.total_score).toBe("number")
    expect(r.total_score).toBeGreaterThanOrEqual(0)
    expect(r.total_score).toBeLessThanOrEqual(100)
  })

  test("rating matches total_score range", () => {
    const r = loadReport()
    const score = r.total_score
    const validRatings = ["Excellent", "Good", "Medium", "Low", "Poor"]
    expect(validRatings).toContain(r.rating)
    if (score >= 90) expect(r.rating).toBe("Excellent")
    else if (score >= 75) expect(r.rating).toBe("Good")
    else if (score >= 60) expect(r.rating).toBe("Medium")
    else if (score >= 40) expect(r.rating).toBe("Low")
    else expect(r.rating).toBe("Poor")
  })

  test("top_improvements has exactly 5 entries with required fields", () => {
    const r = loadReport()
    expect(Array.isArray(r.top_improvements)).toBe(true)
    expect(r.top_improvements.length).toBe(5)
    for (const imp of r.top_improvements) {
      expect(typeof imp.id).toBe("string")
      expect(typeof imp.name).toBe("string")
      expect(["Fail", "Partial"]).toContain(imp.current_status)
      expect(typeof imp.action).toBe("string")
      expect(imp.action.length).toBeGreaterThan(10)
    }
  })
})

describe("audit_summary.md", () => {
  test("file exists", () => {
    expect(existsSync("audit_summary.md")).toBe(true)
  })

  test("contains quick wins section with at least 3 items", () => {
    const text = loadSummary().toLowerCase()
    expect(text).toMatch(/quick win/)
    const quickWinsSection = text.split(/medium effort|strategic/i)[0]
    const bulletCount = (quickWinsSection.match(/^[\s]*[-*\d]/gm) || []).length
    expect(bulletCount).toBeGreaterThanOrEqual(3)
  })

  test("contains medium effort section", () => {
    const text = loadSummary().toLowerCase()
    expect(text).toMatch(/medium effort|medium-effort/)
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadAudit(): any {
  return JSON.parse(readFileSync("product_review_audit.json", "utf-8"))
}

describe("product_review_audit.json", () => {
  test("file exists", () => {
    expect(existsSync("product_review_audit.json")).toBe(true)
  })

  test("is valid JSON with required top-level keys", () => {
    const a = loadAudit()
    expect(a).toHaveProperty("content_title")
    expect(a).toHaveProperty("content_type")
    expect(a).toHaveProperty("veto_check")
    expect(a).toHaveProperty("dimension_scores")
    expect(a).toHaveProperty("geo_score")
    expect(a).toHaveProperty("seo_score")
    expect(a).toHaveProperty("total_score")
    expect(a).toHaveProperty("rating")
    expect(a).toHaveProperty("critical_issues")
    expect(a).toHaveProperty("top_improvements")
  })

  test("content_type is Product Review", () => {
    const a = loadAudit()
    expect(a.content_type).toBe("Product Review")
  })

  test("veto_check has valid structure and at least one veto triggered", () => {
    const a = loadAudit()
    const vc = a.veto_check
    const valid = ["Pass", "Partial", "Fail"]
    expect(valid).toContain(vc.T04_disclosure)
    expect(valid).toContain(vc.C01_intent_alignment)
    expect(valid).toContain(vc.R10_content_consistency)
    expect(typeof vc.any_veto_triggered).toBe("boolean")
    // This low-quality promotional content should trigger at least one veto
    expect(vc.any_veto_triggered).toBe(true)
  })

  test("dimension_scores has all 8 dimensions with values 0-100", () => {
    const a = loadAudit()
    const ds = a.dimension_scores
    const dims = ["C", "O", "R", "E", "Exp", "Ept", "A", "T"]
    for (const d of dims) {
      expect(ds).toHaveProperty(d)
      expect(typeof ds[d]).toBe("number")
      expect(ds[d]).toBeGreaterThanOrEqual(0)
      expect(ds[d]).toBeLessThanOrEqual(100)
    }
  })

  test("geo_score is average of C, O, R, E (within 1 point tolerance)", () => {
    const a = loadAudit()
    const ds = a.dimension_scores
    const expected = (ds.C + ds.O + ds.R + ds.E) / 4
    expect(Math.abs(a.geo_score - expected)).toBeLessThanOrEqual(1)
  })

  test("seo_score is average of Exp, Ept, A, T (within 1 point tolerance)", () => {
    const a = loadAudit()
    const ds = a.dimension_scores
    const expected = (ds.Exp + ds.Ept + ds.A + ds.T) / 4
    expect(Math.abs(a.seo_score - expected)).toBeLessThanOrEqual(1)
  })

  test("total_score reflects low quality content (below 60)", () => {
    const a = loadAudit()
    expect(typeof a.total_score).toBe("number")
    expect(a.total_score).toBeGreaterThanOrEqual(0)
    expect(a.total_score).toBeLessThan(60)
  })

  test("rating is Low or Poor consistent with low total_score", () => {
    const a = loadAudit()
    expect(["Low", "Poor"]).toContain(a.rating)
  })

  test("critical_issues is an array (non-empty given triggered veto)", () => {
    const a = loadAudit()
    expect(Array.isArray(a.critical_issues)).toBe(true)
    expect(a.critical_issues.length).toBeGreaterThan(0)
  })

  test("top_improvements has exactly 5 entries with required fields", () => {
    const a = loadAudit()
    expect(Array.isArray(a.top_improvements)).toBe(true)
    expect(a.top_improvements.length).toBe(5)
    for (const imp of a.top_improvements) {
      expect(typeof imp.id).toBe("string")
      expect(typeof imp.name).toBe("string")
      expect(["Fail", "Partial"]).toContain(imp.current_status)
      expect(typeof imp.action).toBe("string")
      expect(imp.action.length).toBeGreaterThan(10)
    }
  })
})

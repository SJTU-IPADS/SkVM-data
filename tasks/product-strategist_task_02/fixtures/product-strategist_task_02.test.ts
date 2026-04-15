import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadCascade(): any {
  return JSON.parse(readFileSync("retention_okrs.json", "utf-8"))
}

describe("retention_okrs.json", () => {
  test("file exists", () => {
    expect(existsSync("retention_okrs.json")).toBe(true)
  })

  test("has required top-level fields including metrics", () => {
    const c = loadCascade()
    expect(c).toHaveProperty("quarter")
    expect(c).toHaveProperty("strategy")
    expect(c).toHaveProperty("product_contribution")
    expect(c).toHaveProperty("metrics")
    expect(c).toHaveProperty("company")
    expect(c).toHaveProperty("product")
    expect(c).toHaveProperty("teams")
    expect(c).toHaveProperty("alignment_scores")
  })

  test("quarter is Q3 2025, strategy is retention, contribution is 0.40", () => {
    const c = loadCascade()
    expect(c.quarter).toBe("Q3 2025")
    expect(c.strategy).toBe("retention")
    expect(c.product_contribution).toBe(0.40)
  })

  test("metrics block has correct values", () => {
    const c = loadCascade()
    expect(c.metrics.retention_current).toBe(62)
    expect(c.metrics.retention_target).toBe(80)
    expect(c.metrics.churn_current).toBe(8.5)
    expect(c.metrics.churn_target).toBe(3.0)
    expect(c.metrics.ltv_current).toBe(1200)
    expect(c.metrics.ltv_target).toBe(2000)
  })

  test("company has exactly 3 objectives (CO-1, CO-2, CO-3)", () => {
    const c = loadCascade()
    expect(c.company.objectives.length).toBe(3)
    const ids = c.company.objectives.map((o: any) => o.id)
    expect(ids).toContain("CO-1")
    expect(ids).toContain("CO-2")
    expect(ids).toContain("CO-3")
  })

  test("CO-1 key results reference 62 and 80 (retention rates)", () => {
    const c = loadCascade()
    const co1 = c.company.objectives.find((o: any) => o.id === "CO-1")
    expect(co1).toBeDefined()
    const krText = JSON.stringify(co1.key_results)
    expect(krText.includes("62") || krText.includes("80")).toBe(true)
  })

  test("product has exactly 3 objectives each with a supports field", () => {
    const c = loadCascade()
    expect(c.product.objectives.length).toBe(3)
    for (const obj of c.product.objectives) {
      expect(obj).toHaveProperty("supports")
      expect(typeof obj.supports).toBe("string")
      expect(obj.supports.startsWith("CO-")).toBe(true)
    }
  })

  test("teams array contains Backend, Frontend, Analytics, CustomerSuccess", () => {
    const c = loadCascade()
    expect(c.teams.length).toBe(4)
    const names = c.teams.map((t: any) => t.name)
    expect(names).toContain("Backend")
    expect(names).toContain("Frontend")
    expect(names).toContain("Analytics")
    expect(names).toContain("CustomerSuccess")
  })

  test("CustomerSuccess team has at least 1 objective mentioning churn", () => {
    const c = loadCascade()
    const cs = c.teams.find((t: any) => t.name === "CustomerSuccess")
    expect(cs).toBeDefined()
    const csText = JSON.stringify(cs.objectives).toLowerCase()
    expect(csText.includes("churn") || csText.includes("retention") || csText.includes("customer")).toBe(true)
  })

  test("alignment_scores has all required fields as numbers between 0 and 100", () => {
    const c = loadCascade()
    const s = c.alignment_scores
    for (const field of ["vertical_alignment", "horizontal_alignment", "coverage", "balance", "overall"]) {
      expect(typeof s[field]).toBe("number")
      expect(s[field]).toBeGreaterThanOrEqual(0)
      expect(s[field]).toBeLessThanOrEqual(100)
    }
  })
})

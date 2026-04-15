import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadCascade(): any {
  return JSON.parse(readFileSync("okr_cascade.json", "utf-8"))
}

describe("okr_cascade.json", () => {
  test("file exists", () => {
    expect(existsSync("okr_cascade.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const c = loadCascade()
    expect(c).toHaveProperty("quarter")
    expect(c).toHaveProperty("strategy")
    expect(c).toHaveProperty("product_contribution")
    expect(c).toHaveProperty("company")
    expect(c).toHaveProperty("product")
    expect(c).toHaveProperty("teams")
    expect(c).toHaveProperty("alignment_scores")
  })

  test("quarter is Q2 2025, strategy is growth, contribution is 0.35", () => {
    const c = loadCascade()
    expect(c.quarter).toBe("Q2 2025")
    expect(c.strategy).toBe("growth")
    expect(c.product_contribution).toBe(0.35)
  })

  test("company has exactly 3 objectives (CO-1, CO-2, CO-3)", () => {
    const c = loadCascade()
    expect(Array.isArray(c.company.objectives)).toBe(true)
    expect(c.company.objectives.length).toBe(3)
    const ids = c.company.objectives.map((o: any) => o.id)
    expect(ids).toContain("CO-1")
    expect(ids).toContain("CO-2")
    expect(ids).toContain("CO-3")
  })

  test("each company objective has 2 or 3 key results", () => {
    const c = loadCascade()
    for (const obj of c.company.objectives) {
      expect(Array.isArray(obj.key_results)).toBe(true)
      expect(obj.key_results.length).toBeGreaterThanOrEqual(2)
      expect(obj.key_results.length).toBeLessThanOrEqual(3)
    }
  })

  test("product has exactly 3 objectives (PO-1, PO-2, PO-3) each with a supports field", () => {
    const c = loadCascade()
    expect(Array.isArray(c.product.objectives)).toBe(true)
    expect(c.product.objectives.length).toBe(3)
    const ids = c.product.objectives.map((o: any) => o.id)
    expect(ids).toContain("PO-1")
    expect(ids).toContain("PO-2")
    expect(ids).toContain("PO-3")
    for (const obj of c.product.objectives) {
      expect(obj).toHaveProperty("supports")
    }
  })

  test("teams array has exactly 4 teams: Engineering, Design, Growth, Data", () => {
    const c = loadCascade()
    expect(Array.isArray(c.teams)).toBe(true)
    expect(c.teams.length).toBe(4)
    const names = c.teams.map((t: any) => t.name)
    expect(names).toContain("Engineering")
    expect(names).toContain("Design")
    expect(names).toContain("Growth")
    expect(names).toContain("Data")
  })

  test("each team has at least 1 objective with key_results", () => {
    const c = loadCascade()
    for (const team of c.teams) {
      expect(Array.isArray(team.objectives)).toBe(true)
      expect(team.objectives.length).toBeGreaterThanOrEqual(1)
      for (const obj of team.objectives) {
        expect(Array.isArray(obj.key_results)).toBe(true)
        expect(obj.key_results.length).toBeGreaterThanOrEqual(1)
      }
    }
  })

  test("at least one key result references MAU values 80000 and 120000", () => {
    const c = loadCascade()
    const allKRTitles: string[] = []
    const collectKRs = (objs: any[]) => {
      for (const obj of objs) {
        for (const kr of obj.key_results || []) {
          allKRTitles.push(JSON.stringify(kr))
        }
      }
    }
    collectKRs(c.company.objectives)
    collectKRs(c.product.objectives)
    const combined = allKRTitles.join(" ")
    expect(combined.includes("80000") || combined.includes("80,000")).toBe(true)
    expect(combined.includes("120000") || combined.includes("120,000")).toBe(true)
  })

  test("alignment_scores.overall is between 60 and 100", () => {
    const c = loadCascade()
    const scores = c.alignment_scores
    expect(typeof scores.overall).toBe("number")
    expect(scores.overall).toBeGreaterThanOrEqual(60)
    expect(scores.overall).toBeLessThanOrEqual(100)
  })

  test("all alignment score fields are present and numeric", () => {
    const c = loadCascade()
    const s = c.alignment_scores
    for (const field of ["vertical_alignment", "horizontal_alignment", "coverage", "balance", "overall"]) {
      expect(typeof s[field]).toBe("number")
    }
  })
})

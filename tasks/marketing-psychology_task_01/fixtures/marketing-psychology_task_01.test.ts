import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadAudit(): any {
  return JSON.parse(readFileSync("pricing_audit.json", "utf-8"))
}

describe("pricing_audit.json", () => {
  test("file exists", () => {
    expect(existsSync("pricing_audit.json")).toBe(true)
  })

  test("valid JSON and parseable", () => {
    expect(() => loadAudit()).not.toThrow()
  })

  test("has required top-level fields", () => {
    const a = loadAudit()
    expect(a).toHaveProperty("issues")
    expect(a).toHaveProperty("recommended_prices")
    expect(a).toHaveProperty("recommended_tier")
    expect(a).toHaveProperty("decoy_explanation")
  })

  test("issues is an array with at least 4 issues", () => {
    const a = loadAudit()
    expect(Array.isArray(a.issues)).toBe(true)
    expect(a.issues.length).toBeGreaterThanOrEqual(4)
  })

  test("each issue has principle, problem, and fix fields", () => {
    const a = loadAudit()
    for (const issue of a.issues) {
      expect(typeof issue.principle).toBe("string")
      expect(issue.principle.length).toBeGreaterThan(0)
      expect(typeof issue.problem).toBe("string")
      expect(issue.problem.length).toBeGreaterThan(0)
      expect(typeof issue.fix).toBe("string")
      expect(issue.fix.length).toBeGreaterThan(0)
    }
  })

  test("recommended_prices has basic, pro, and enterprise fields as numbers", () => {
    const a = loadAudit()
    expect(typeof a.recommended_prices.basic).toBe("number")
    expect(typeof a.recommended_prices.pro).toBe("number")
    expect(typeof a.recommended_prices.enterprise).toBe("number")
  })

  test("charm pricing: all recommended prices end in 9", () => {
    const a = loadAudit()
    expect(a.recommended_prices.basic % 10).toBe(9)
    expect(a.recommended_prices.pro % 10).toBe(9)
    expect(a.recommended_prices.enterprise % 10).toBe(9)
  })

  test("price reduction at most 2 dollars below original prices", () => {
    const a = loadAudit()
    // Originals: basic=50, pro=51, enterprise=200
    expect(a.recommended_prices.basic).toBeGreaterThanOrEqual(48)
    expect(a.recommended_prices.basic).toBeLessThanOrEqual(50)
    expect(a.recommended_prices.pro).toBeGreaterThanOrEqual(49)
    expect(a.recommended_prices.pro).toBeLessThanOrEqual(51)
    expect(a.recommended_prices.enterprise).toBeGreaterThanOrEqual(198)
    expect(a.recommended_prices.enterprise).toBeLessThanOrEqual(200)
  })

  test("recommended_tier is one of basic, pro, or enterprise", () => {
    const a = loadAudit()
    const valid = new Set(["basic", "pro", "enterprise"])
    expect(valid.has(a.recommended_tier)).toBe(true)
  })

  test("decoy_explanation is a non-empty string", () => {
    const a = loadAudit()
    expect(typeof a.decoy_explanation).toBe("string")
    expect(a.decoy_explanation.length).toBeGreaterThan(10)
  })
})

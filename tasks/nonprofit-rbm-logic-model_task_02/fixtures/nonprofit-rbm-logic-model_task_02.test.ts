import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadRiskMatrix(): any {
  return JSON.parse(readFileSync("risk_matrix.json", "utf-8"))
}

function loadCompliance(): any {
  return JSON.parse(readFileSync("compliance_score.json", "utf-8"))
}

describe("risk_matrix.json", () => {
  test("risk matrix file exists", () => {
    expect(existsSync("risk_matrix.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadRiskMatrix()).not.toThrow()
  })

  test("has risks array with at least 5 risks", () => {
    const r = loadRiskMatrix()
    expect(r).toHaveProperty("risks")
    expect(Array.isArray(r.risks)).toBe(true)
    expect(r.risks.length).toBeGreaterThanOrEqual(5)
  })

  test("each risk has required fields: id, description, category, likelihood, impact, mitigation, owner", () => {
    const r = loadRiskMatrix()
    for (const risk of r.risks) {
      expect(typeof risk.id).toBe("string")
      expect(typeof risk.description).toBe("string")
      expect(typeof risk.category).toBe("string")
      expect(typeof risk.likelihood).toBe("string")
      expect(typeof risk.impact).toBe("string")
      expect(typeof risk.mitigation).toBe("string")
      expect(typeof risk.owner).toBe("string")
    }
  })

  test("likelihood and impact values are High, Medium, or Low", () => {
    const r = loadRiskMatrix()
    const valid = new Set(["High", "Medium", "Low"])
    for (const risk of r.risks) {
      expect(valid.has(risk.likelihood)).toBe(true)
      expect(valid.has(risk.impact)).toBe(true)
    }
  })

  test("risks span at least 3 different categories", () => {
    const r = loadRiskMatrix()
    const categories = new Set(r.risks.map((risk: any) => risk.category))
    expect(categories.size).toBeGreaterThanOrEqual(3)
  })

  test("at least one risk has High likelihood", () => {
    const r = loadRiskMatrix()
    const hasHighLikelihood = r.risks.some((risk: any) => risk.likelihood === "High")
    expect(hasHighLikelihood).toBe(true)
  })
})

describe("compliance_score.json", () => {
  test("compliance file exists", () => {
    expect(existsSync("compliance_score.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadCompliance()).not.toThrow()
  })

  test("has score, checks, and overall_recommendation fields", () => {
    const c = loadCompliance()
    expect(c).toHaveProperty("score")
    expect(c).toHaveProperty("checks")
    expect(c).toHaveProperty("overall_recommendation")
  })

  test("compliance score is between 55 and 85 (inclusive)", () => {
    const c = loadCompliance()
    expect(typeof c.score).toBe("number")
    expect(c.score).toBeGreaterThanOrEqual(55)
    expect(c.score).toBeLessThanOrEqual(85)
  })

  test("checks array has at least 6 compliance checks with item, status, and note fields", () => {
    const c = loadCompliance()
    expect(Array.isArray(c.checks)).toBe(true)
    expect(c.checks.length).toBeGreaterThanOrEqual(6)
    for (const check of c.checks) {
      expect(typeof check.item).toBe("string")
      expect(typeof check.status).toBe("string")
      expect(typeof check.note).toBe("string")
    }
  })

  test("check statuses are pass, conditional, or fail", () => {
    const c = loadCompliance()
    const valid = new Set(["pass", "conditional", "fail"])
    for (const check of c.checks) {
      expect(valid.has(check.status)).toBe(true)
    }
  })

  test("overall_recommendation is Go, Conditional Go, or No-Go", () => {
    const c = loadCompliance()
    const valid = new Set(["Go", "Conditional Go", "No-Go"])
    expect(valid.has(c.overall_recommendation)).toBe(true)
  })
})

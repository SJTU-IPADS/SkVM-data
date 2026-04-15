import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadFormulas(): any {
  return JSON.parse(readFileSync("formulas.json", "utf-8"))
}

describe("formulas.json", () => {
  test("file exists", () => {
    expect(existsSync("formulas.json")).toBe(true)
  })

  test("has a top-level 'formulas' array", () => {
    const d = loadFormulas()
    expect(d).toHaveProperty("formulas")
    expect(Array.isArray(d.formulas)).toBe(true)
  })

  test("contains exactly 5 formula entries", () => {
    const d = loadFormulas()
    expect(d.formulas.length).toBe(5)
  })

  test("each entry has required fields: task_id, description, formula, explanation", () => {
    const d = loadFormulas()
    for (const f of d.formulas) {
      expect(f).toHaveProperty("task_id")
      expect(f).toHaveProperty("description")
      expect(f).toHaveProperty("formula")
      expect(f).toHaveProperty("explanation")
    }
  })

  test("task IDs are F1, F2, F3, F4, F5", () => {
    const d = loadFormulas()
    const ids = d.formulas.map((f: any) => f.task_id).sort()
    expect(ids).toContain("F1")
    expect(ids).toContain("F2")
    expect(ids).toContain("F3")
    expect(ids).toContain("F4")
    expect(ids).toContain("F5")
  })

  test("each formula field starts with '='", () => {
    const d = loadFormulas()
    for (const f of d.formulas) {
      expect(typeof f.formula).toBe("string")
      expect(f.formula.startsWith("=")).toBe(true)
    }
  })

  test("each explanation is at least 20 characters", () => {
    const d = loadFormulas()
    for (const f of d.formulas) {
      expect(typeof f.explanation).toBe("string")
      expect(f.explanation.length).toBeGreaterThanOrEqual(20)
    }
  })

  test("F2 formula contains COUNTIF (for counting North region rows)", () => {
    const d = loadFormulas()
    const f2 = d.formulas.find((f: any) => f.task_id === "F2")
    expect(f2).toBeDefined()
    expect(f2.formula.toUpperCase()).toContain("COUNTIF")
  })

  test("F3 formula contains AVERAGEIF (for conditional average)", () => {
    const d = loadFormulas()
    const f3 = d.formulas.find((f: any) => f.task_id === "F3")
    expect(f3).toBeDefined()
    expect(f3.formula.toUpperCase()).toContain("AVERAGEIF")
  })

  test("formulas reference column ranges within rows 2-100", () => {
    const d = loadFormulas()
    const formulas = d.formulas.map((f: any) => f.formula).join(" ")
    // Should reference B2, C2, D2 etc.
    expect(formulas).toMatch(/[BCD]\d/i)
  })
})

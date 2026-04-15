import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadData(): any {
  return JSON.parse(readFileSync("formula_practice.json", "utf-8"))
}

function approxEqual(a: number, b: number, tol = 0.01): boolean {
  return Math.abs(a - b) <= tol
}

describe("formula_practice.json", () => {
  test("file exists", () => {
    expect(existsSync("formula_practice.json")).toBe(true)
  })

  test("valid JSON and parseable", () => {
    expect(() => loadData()).not.toThrow()
  })

  test("has formulas, calculations, and practice_problems fields", () => {
    const d = loadData()
    expect(d).toHaveProperty("formulas")
    expect(d).toHaveProperty("calculations")
    expect(d).toHaveProperty("practice_problems")
  })

  test("formulas array contains exactly 4 entries", () => {
    const d = loadData()
    expect(Array.isArray(d.formulas)).toBe(true)
    expect(d.formulas.length).toBe(4)
  })

  test("each formula has topic, formula, and variables fields", () => {
    const d = loadData()
    for (const f of d.formulas) {
      expect(typeof f.topic).toBe("string")
      expect(f.topic.length).toBeGreaterThan(0)
      expect(typeof f.formula).toBe("string")
      expect(f.formula.length).toBeGreaterThan(0)
      expect(typeof f.variables).toBe("object")
      expect(f.variables).not.toBeNull()
    }
  })

  test("circle area calculation is correct (π × 7² ≈ 153.9380)", () => {
    const d = loadData()
    // π * 7^2 = 3.14159265 * 49 = 153.9380...
    expect(approxEqual(d.calculations.circle_area, 153.938, 0.01)).toBe(true)
  })

  test("cylinder volume calculation is correct (π × 3² × 10 ≈ 282.7433)", () => {
    const d = loadData()
    // π * 9 * 10 = 282.743...
    expect(approxEqual(d.calculations.cylinder_volume, 282.743, 0.01)).toBe(true)
  })

  test("sphere surface area calculation is correct (4π × 5² ≈ 314.1593)", () => {
    const d = loadData()
    // 4 * π * 25 = 314.159...
    expect(approxEqual(d.calculations.sphere_surface_area, 314.159, 0.01)).toBe(true)
  })

  test("triangle hypotenuse is 10 (a=6, b=8, c=√(36+64)=10)", () => {
    const d = loadData()
    expect(approxEqual(d.calculations.triangle_hypotenuse, 10.0, 0.001)).toBe(true)
  })

  test("practice_problems contains exactly 3 problems with id, problem, and answer", () => {
    const d = loadData()
    expect(Array.isArray(d.practice_problems)).toBe(true)
    expect(d.practice_problems.length).toBe(3)
    for (const pp of d.practice_problems) {
      expect(typeof pp.id).toBe("number")
      expect(typeof pp.problem).toBe("string")
      expect(pp.problem.length).toBeGreaterThan(0)
      expect(typeof pp.answer).toBe("string")
      expect(pp.answer.length).toBeGreaterThan(0)
    }
  })
})

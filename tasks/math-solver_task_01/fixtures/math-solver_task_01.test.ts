import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadResults(): any {
  return JSON.parse(readFileSync("math_results.json", "utf-8"))
}

function approxEqual(a: number, b: number, tol = 0.001): boolean {
  return Math.abs(a - b) <= tol
}

describe("math_results.json", () => {
  test("file exists", () => {
    expect(existsSync("math_results.json")).toBe(true)
  })

  test("valid JSON and parseable", () => {
    expect(() => loadResults()).not.toThrow()
  })

  test("has quadratic, unit_conversion, and linear_system sections", () => {
    const r = loadResults()
    expect(r).toHaveProperty("quadratic")
    expect(r).toHaveProperty("unit_conversion")
    expect(r).toHaveProperty("linear_system")
  })

  test("quadratic roots array contains exactly 2 numbers", () => {
    const r = loadResults()
    expect(Array.isArray(r.quadratic.roots)).toBe(true)
    expect(r.quadratic.roots.length).toBe(2)
    for (const root of r.quadratic.roots) {
      expect(typeof root).toBe("number")
    }
  })

  test("quadratic roots are correct values (3 and 0.5)", () => {
    const r = loadResults()
    const roots: number[] = [...r.quadratic.roots].sort((a, b) => a - b)
    expect(approxEqual(roots[0], 0.5)).toBe(true)
    expect(approxEqual(roots[1], 3.0)).toBe(true)
  })

  test("quadratic steps array has at least 3 entries", () => {
    const r = loadResults()
    expect(Array.isArray(r.quadratic.steps)).toBe(true)
    expect(r.quadratic.steps.length).toBeGreaterThanOrEqual(3)
  })

  test("unit conversion result is 150 km/h to meters per second (41.6667)", () => {
    const r = loadResults()
    // 150 * 1000 / 3600 = 41.6667 m/s
    expect(approxEqual(r.unit_conversion.result, 41.6667, 0.001)).toBe(true)
  })

  test("unit conversion steps array has at least 2 entries", () => {
    const r = loadResults()
    expect(Array.isArray(r.unit_conversion.steps)).toBe(true)
    expect(r.unit_conversion.steps.length).toBeGreaterThanOrEqual(2)
  })

  test("linear system: x equals correct value (18/5 = 3.6)", () => {
    const r = loadResults()
    // 3x + 2y = 16, x - y = 1 → y = x-1 → 3x + 2(x-1) = 16 → 5x = 18 → x = 3.6
    expect(approxEqual(r.linear_system.x, 3.6, 0.01)).toBe(true)
  })

  test("linear system: y equals correct value (2.6)", () => {
    const r = loadResults()
    // y = x - 1 = 2.6
    expect(approxEqual(r.linear_system.y, 2.6, 0.01)).toBe(true)
  })

  test("linear system steps array has at least 3 entries", () => {
    const r = loadResults()
    expect(Array.isArray(r.linear_system.steps)).toBe(true)
    expect(r.linear_system.steps.length).toBeGreaterThanOrEqual(3)
  })
})

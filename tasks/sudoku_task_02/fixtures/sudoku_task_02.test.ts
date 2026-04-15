import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadData(): any {
  return JSON.parse(readFileSync("kids_sudoku.json", "utf-8"))
}

describe("kids_sudoku.json", () => {
  test("file exists", () => {
    expect(existsSync("kids_sudoku.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadData()).not.toThrow()
  })

  test("has required top-level keys", () => {
    const d = loadData()
    expect(d).toHaveProperty("grid_size")
    expect(d).toHaveProperty("puzzle")
    expect(d).toHaveProperty("solution")
    expect(d).toHaveProperty("empty_cells")
    expect(d).toHaveProperty("difficulty")
    expect(d).toHaveProperty("valid")
    expect(d).toHaveProperty("validation")
  })

  test("grid_size is 4", () => {
    const d = loadData()
    expect(d.grid_size).toBe(4)
  })

  test("puzzle is a 4x4 array", () => {
    const d = loadData()
    expect(Array.isArray(d.puzzle)).toBe(true)
    expect(d.puzzle.length).toBe(4)
    for (const row of d.puzzle) {
      expect(Array.isArray(row)).toBe(true)
      expect(row.length).toBe(4)
    }
  })

  test("solution is a 4x4 array", () => {
    const d = loadData()
    expect(Array.isArray(d.solution)).toBe(true)
    expect(d.solution.length).toBe(4)
    for (const row of d.solution) {
      expect(Array.isArray(row)).toBe(true)
      expect(row.length).toBe(4)
    }
  })

  test("empty_cells is at least 4 and matches actual zero count in puzzle", () => {
    const d = loadData()
    expect(d.empty_cells).toBeGreaterThanOrEqual(4)
    let zeroes = 0
    for (const row of d.puzzle) {
      for (const cell of row) {
        if (cell === 0) zeroes++
      }
    }
    expect(d.empty_cells).toBe(zeroes)
  })

  test("solution has no zeros", () => {
    const d = loadData()
    for (const row of d.solution) {
      for (const cell of row) {
        expect(cell).not.toBe(0)
        expect(cell).toBeGreaterThanOrEqual(1)
        expect(cell).toBeLessThanOrEqual(4)
      }
    }
  })

  test("valid is true", () => {
    const d = loadData()
    expect(d.valid).toBe(true)
  })

  test("all validation flags are true", () => {
    const d = loadData()
    expect(d.validation.rows_valid).toBe(true)
    expect(d.validation.cols_valid).toBe(true)
    expect(d.validation.boxes_valid).toBe(true)
  })

  test("solution rows each contain digits 1-4 exactly once", () => {
    const d = loadData()
    for (const row of d.solution) {
      const sorted = [...row].sort()
      expect(sorted).toEqual([1, 2, 3, 4])
    }
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadData(): any {
  return JSON.parse(readFileSync("sudoku_result.json", "utf-8"))
}

describe("sudoku_result.json", () => {
  test("file exists", () => {
    expect(existsSync("sudoku_result.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadData()).not.toThrow()
  })

  test("has required top-level keys", () => {
    const d = loadData()
    expect(d).toHaveProperty("puzzle")
    expect(d).toHaveProperty("solution")
    expect(d).toHaveProperty("solved")
    expect(d).toHaveProperty("validation")
  })

  test("puzzle is a 9x9 array", () => {
    const d = loadData()
    expect(Array.isArray(d.puzzle)).toBe(true)
    expect(d.puzzle.length).toBe(9)
    for (const row of d.puzzle) {
      expect(Array.isArray(row)).toBe(true)
      expect(row.length).toBe(9)
    }
  })

  test("solution is a 9x9 array", () => {
    const d = loadData()
    expect(Array.isArray(d.solution)).toBe(true)
    expect(d.solution.length).toBe(9)
    for (const row of d.solution) {
      expect(Array.isArray(row)).toBe(true)
      expect(row.length).toBe(9)
    }
  })

  test("solved is true", () => {
    const d = loadData()
    expect(d.solved).toBe(true)
  })

  test("solution has no zeros", () => {
    const d = loadData()
    for (const row of d.solution) {
      for (const cell of row) {
        expect(cell).not.toBe(0)
      }
    }
  })

  test("all solution digits are between 1 and 9", () => {
    const d = loadData()
    for (const row of d.solution) {
      for (const cell of row) {
        expect(cell).toBeGreaterThanOrEqual(1)
        expect(cell).toBeLessThanOrEqual(9)
      }
    }
  })

  test("known cells match expected values from the puzzle", () => {
    const d = loadData()
    // Row 0, col 2 must be 4; row 0, col 5 must be 6
    expect(d.solution[0][2]).toBe(4)
    expect(d.solution[0][5]).toBe(6)
    // Original given cells must be preserved
    expect(d.solution[0][0]).toBe(5)
    expect(d.solution[0][1]).toBe(3)
    expect(d.solution[0][4]).toBe(7)
    expect(d.solution[1][0]).toBe(6)
    expect(d.solution[1][3]).toBe(1)
    expect(d.solution[1][4]).toBe(9)
    expect(d.solution[1][5]).toBe(5)
  })

  test("validation flags are all true", () => {
    const d = loadData()
    expect(d.validation).toHaveProperty("rows_valid")
    expect(d.validation).toHaveProperty("cols_valid")
    expect(d.validation).toHaveProperty("boxes_valid")
    expect(d.validation.rows_valid).toBe(true)
    expect(d.validation.cols_valid).toBe(true)
    expect(d.validation.boxes_valid).toBe(true)
  })
})

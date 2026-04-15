import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadResults(): any[] {
  return JSON.parse(readFileSync("match_results.json", "utf-8"))
}

function loadSummary(): any {
  return JSON.parse(readFileSync("match_summary.json", "utf-8"))
}

describe("match_results.json", () => {
  test("file exists", () => {
    expect(existsSync("match_results.json")).toBe(true)
  })

  test("is an array of exactly 8 entries", () => {
    const r = loadResults()
    expect(Array.isArray(r)).toBe(true)
    expect(r.length).toBe(8)
  })

  test("each entry has case_id, value, pattern, expected, actual, passed", () => {
    const r = loadResults()
    for (const entry of r) {
      expect(entry).toHaveProperty("case_id")
      expect(entry).toHaveProperty("value")
      expect(entry).toHaveProperty("pattern")
      expect(entry).toHaveProperty("expected")
      expect(entry).toHaveProperty("actual")
      expect(entry).toHaveProperty("passed")
    }
  })

  test("case 1: starts-with pattern discord* matches discord-BOT-token", () => {
    const r = loadResults()
    const c = r.find((e: any) => Number(e.case_id) === 1)
    expect(c).toBeDefined()
    expect(c.actual).toBe(true)
    expect(c.passed).toBe(true)
  })

  test("case 3: starts-and-ends pattern discord*token matches correctly", () => {
    const r = loadResults()
    const c = r.find((e: any) => Number(e.case_id) === 3)
    expect(c).toBeDefined()
    expect(c.actual).toBe(true)
    expect(c.passed).toBe(true)
  })

  test("case 4: starts-with pattern slack* does not match discord-BOT-token", () => {
    const r = loadResults()
    const c = r.find((e: any) => Number(e.case_id) === 4)
    expect(c).toBeDefined()
    expect(c.actual).toBe(false)
    expect(c.passed).toBe(true)
  })

  test("case 5: contains pattern k7Qm9x matches value with that substring", () => {
    const r = loadResults()
    const c = r.find((e: any) => Number(e.case_id) === 5)
    expect(c).toBeDefined()
    expect(c.actual).toBe(true)
    expect(c.passed).toBe(true)
  })

  test("case 6: empty pattern never matches", () => {
    const r = loadResults()
    const c = r.find((e: any) => Number(e.case_id) === 6)
    expect(c).toBeDefined()
    expect(c.actual).toBe(false)
    expect(c.passed).toBe(true)
  })

  test("all 8 cases have passed=true", () => {
    const r = loadResults()
    const allPassed = r.every((e: any) => e.passed === true)
    expect(allPassed).toBe(true)
  })
})

describe("match_summary.json", () => {
  test("file exists", () => {
    expect(existsSync("match_summary.json")).toBe(true)
  })

  test("total is 8, passed is 8, failed is 0", () => {
    const s = loadSummary()
    expect(Number(s.total)).toBe(8)
    expect(Number(s.passed)).toBe(8)
    expect(Number(s.failed)).toBe(0)
  })
})

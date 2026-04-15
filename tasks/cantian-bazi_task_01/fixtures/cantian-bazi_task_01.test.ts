import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadResult(): any {
  return JSON.parse(readFileSync("bazi_result.json", "utf-8"))
}

// Helper: check if a string contains at least some CJK characters
function hasChinese(s: string): boolean {
  return /[\u4e00-\u9fff]/.test(s)
}

// Each pillar should be 2 Chinese characters (heavenly stem + earthly branch)
function isValidPillar(s: string): boolean {
  if (typeof s !== "string") return false
  const cjkChars = s.match(/[\u4e00-\u9fff]/g) || []
  return cjkChars.length >= 2
}

describe("bazi_result.json", () => {
  test("file exists", () => {
    expect(existsSync("bazi_result.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadResult()).not.toThrow()
  })

  test("has all required fields", () => {
    const r = loadResult()
    expect(r).toHaveProperty("solar_datetime")
    expect(r).toHaveProperty("gender")
    expect(r).toHaveProperty("year_pillar")
    expect(r).toHaveProperty("month_pillar")
    expect(r).toHaveProperty("day_pillar")
    expect(r).toHaveProperty("hour_pillar")
    expect(r).toHaveProperty("raw_output")
  })

  test("solar_datetime is '1985-08-15T13:45:00'", () => {
    const r = loadResult()
    expect(r.solar_datetime).toBe("1985-08-15T13:45:00")
  })

  test("gender is 'male'", () => {
    const r = loadResult()
    expect(r.gender.toLowerCase()).toBe("male")
  })

  test("year_pillar contains 2 or more Chinese characters", () => {
    const r = loadResult()
    expect(isValidPillar(r.year_pillar)).toBe(true)
  })

  test("month_pillar contains 2 or more Chinese characters", () => {
    const r = loadResult()
    expect(isValidPillar(r.month_pillar)).toBe(true)
  })

  test("day_pillar contains 2 or more Chinese characters", () => {
    const r = loadResult()
    expect(isValidPillar(r.day_pillar)).toBe(true)
  })

  test("hour_pillar contains 2 or more Chinese characters", () => {
    const r = loadResult()
    expect(isValidPillar(r.hour_pillar)).toBe(true)
  })

  test("raw_output is a non-empty string with Chinese content", () => {
    const r = loadResult()
    expect(typeof r.raw_output).toBe("string")
    expect(r.raw_output.length).toBeGreaterThan(10)
    expect(hasChinese(r.raw_output)).toBe(true)
  })
})

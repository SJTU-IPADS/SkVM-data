import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadResult(): any {
  return JSON.parse(readFileSync("chinese_calendar.json", "utf-8"))
}

function hasChinese(s: string): boolean {
  return /[\u4e00-\u9fff]/.test(s)
}

function isValidGanzhi(s: string): boolean {
  if (typeof s !== "string") return false
  const cjkChars = s.match(/[\u4e00-\u9fff]/g) || []
  return cjkChars.length >= 2
}

describe("chinese_calendar.json", () => {
  test("file exists", () => {
    expect(existsSync("chinese_calendar.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadResult()).not.toThrow()
  })

  test("has all required fields", () => {
    const r = loadResult()
    expect(r).toHaveProperty("date")
    expect(r).toHaveProperty("lunar_month")
    expect(r).toHaveProperty("lunar_day")
    expect(r).toHaveProperty("year_ganzhi")
    expect(r).toHaveProperty("day_ganzhi")
    expect(r).toHaveProperty("yi")
    expect(r).toHaveProperty("ji")
    expect(r).toHaveProperty("raw_output")
  })

  test("date is '2025-10-01'", () => {
    const r = loadResult()
    expect(r.date).toBe("2025-10-01")
  })

  test("lunar_month is a non-empty string", () => {
    const r = loadResult()
    expect(typeof r.lunar_month).toBe("string")
    expect(r.lunar_month.length).toBeGreaterThan(0)
  })

  test("lunar_day is a non-empty string", () => {
    const r = loadResult()
    expect(typeof r.lunar_day).toBe("string")
    expect(r.lunar_day.length).toBeGreaterThan(0)
  })

  test("year_ganzhi contains at least 2 Chinese characters", () => {
    const r = loadResult()
    expect(isValidGanzhi(r.year_ganzhi)).toBe(true)
  })

  test("day_ganzhi contains at least 2 Chinese characters", () => {
    const r = loadResult()
    expect(isValidGanzhi(r.day_ganzhi)).toBe(true)
  })

  test("yi is an array", () => {
    const r = loadResult()
    expect(Array.isArray(r.yi)).toBe(true)
  })

  test("ji is an array", () => {
    const r = loadResult()
    expect(Array.isArray(r.ji)).toBe(true)
  })

  test("raw_output is a non-empty string with Chinese characters", () => {
    const r = loadResult()
    expect(typeof r.raw_output).toBe("string")
    expect(r.raw_output.length).toBeGreaterThan(10)
    expect(hasChinese(r.raw_output)).toBe(true)
  })
})

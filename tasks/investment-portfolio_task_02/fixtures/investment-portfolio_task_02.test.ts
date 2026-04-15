import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadDCA(): any {
  return JSON.parse(readFileSync("dca_result.json", "utf-8"))
}

function loadDividend(): any {
  return JSON.parse(readFileSync("dividend_result.json", "utf-8"))
}

describe("dca_result.json", () => {
  test("file exists", () => {
    expect(existsSync("dca_result.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const d = loadDCA()
    expect(d).toHaveProperty("ticker")
    expect(d).toHaveProperty("monthly_investment")
    expect(d).toHaveProperty("initial_price")
    expect(d).toHaveProperty("months")
    expect(d).toHaveProperty("total_invested")
    expect(d).toHaveProperty("schedule")
  })

  test("top-level scalar values are correct", () => {
    const d = loadDCA()
    expect(d.ticker).toBe("NVDA")
    expect(Number(d.monthly_investment)).toBe(400)
    expect(Number(d.initial_price)).toBe(200.0)
    expect(Number(d.months)).toBe(12)
    expect(Number(d.total_invested)).toBe(4800)
  })

  test("schedule has 12 entries", () => {
    const d = loadDCA()
    expect(Array.isArray(d.schedule)).toBe(true)
    expect(d.schedule.length).toBe(12)
  })

  test("each schedule entry has month, price, shares_bought, cumulative_shares", () => {
    const d = loadDCA()
    for (const entry of d.schedule) {
      expect(entry).toHaveProperty("month")
      expect(entry).toHaveProperty("price")
      expect(entry).toHaveProperty("shares_bought")
      expect(entry).toHaveProperty("cumulative_shares")
    }
  })

  test("schedule month 1 has correct shares_bought and cumulative_shares", () => {
    const d = loadDCA()
    const m1 = d.schedule.find((e: any) => Number(e.month) === 1)
    expect(m1).toBeDefined()
    expect(Math.abs(Number(m1.shares_bought) - 2.0)).toBeLessThan(0.01)
    expect(Math.abs(Number(m1.cumulative_shares) - 2.0)).toBeLessThan(0.01)
  })

  test("schedule month 12 has correct cumulative_shares", () => {
    const d = loadDCA()
    const m12 = d.schedule.find((e: any) => Number(e.month) === 12)
    expect(m12).toBeDefined()
    expect(Math.abs(Number(m12.cumulative_shares) - 24.0)).toBeLessThan(0.01)
  })
})

describe("dividend_result.json", () => {
  test("file exists", () => {
    expect(existsSync("dividend_result.json")).toBe(true)
  })

  test("has required fields", () => {
    const d = loadDividend()
    expect(d).toHaveProperty("ticker")
    expect(d).toHaveProperty("annual_dividend")
    expect(d).toHaveProperty("current_price")
    expect(d).toHaveProperty("yield_percent")
  })

  test("ticker and input values are correct", () => {
    const d = loadDividend()
    expect(d.ticker).toBe("JNJ")
    expect(Math.abs(Number(d.annual_dividend) - 5.20)).toBeLessThan(0.001)
    expect(Math.abs(Number(d.current_price) - 260.0)).toBeLessThan(0.001)
  })

  test("yield_percent is exactly 2.0", () => {
    const d = loadDividend()
    expect(Math.abs(Number(d.yield_percent) - 2.0)).toBeLessThan(0.01)
  })
})

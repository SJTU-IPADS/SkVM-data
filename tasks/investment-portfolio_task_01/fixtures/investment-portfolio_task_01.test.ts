import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync, statSync } from "fs"

function loadSummary(): any {
  return JSON.parse(readFileSync("portfolio_summary.json", "utf-8"))
}

describe("portfolio_summary.json", () => {
  test("file exists", () => {
    expect(existsSync("portfolio_summary.json")).toBe(true)
  })

  test("is valid JSON with required top-level fields", () => {
    const s = loadSummary()
    expect(s).toHaveProperty("holdings")
    expect(s).toHaveProperty("total_cost")
    expect(s).toHaveProperty("total_value")
    expect(s).toHaveProperty("total_pl")
  })

  test("holdings is an array of 3 entries", () => {
    const s = loadSummary()
    expect(Array.isArray(s.holdings)).toBe(true)
    expect(s.holdings.length).toBe(3)
  })

  test("each holding has required fields", () => {
    const s = loadSummary()
    for (const h of s.holdings) {
      expect(h).toHaveProperty("ticker")
      expect(h).toHaveProperty("shares")
      expect(h).toHaveProperty("buy_price")
      expect(h).toHaveProperty("current_price")
      expect(h).toHaveProperty("cost_basis")
      expect(h).toHaveProperty("current_value")
      expect(h).toHaveProperty("pl")
    }
  })

  test("AAPL holding has correct values", () => {
    const s = loadSummary()
    const aapl = s.holdings.find((h: any) => h.ticker === "AAPL")
    expect(aapl).toBeDefined()
    expect(Number(aapl.shares)).toBe(20)
    expect(Number(aapl.cost_basis)).toBe(3000)
    expect(Number(aapl.current_value)).toBe(3500)
    expect(Number(aapl.pl)).toBe(500)
  })

  test("MSFT holding has correct values", () => {
    const s = loadSummary()
    const msft = s.holdings.find((h: any) => h.ticker === "MSFT")
    expect(msft).toBeDefined()
    expect(Number(msft.cost_basis)).toBe(2800)
    expect(Number(msft.current_value)).toBe(3100)
    expect(Number(msft.pl)).toBe(300)
  })

  test("GOOGL holding has correct values", () => {
    const s = loadSummary()
    const googl = s.holdings.find((h: any) => h.ticker === "GOOGL")
    expect(googl).toBeDefined()
    expect(Number(googl.cost_basis)).toBe(600)
    expect(Number(googl.current_value)).toBe(700)
    expect(Number(googl.pl)).toBe(100)
  })

  test("portfolio totals are correct", () => {
    const s = loadSummary()
    expect(Number(s.total_cost)).toBe(6400)
    expect(Number(s.total_value)).toBe(7300)
    expect(Number(s.total_pl)).toBe(900)
  })
})

describe("portfolio_export.csv", () => {
  test("file exists", () => {
    expect(existsSync("portfolio_export.csv")).toBe(true)
  })

  test("CSV file has non-trivial content", () => {
    const stat = statSync("portfolio_export.csv")
    expect(stat.size).toBeGreaterThan(30)
  })

  test("CSV contains all three ticker symbols", () => {
    const csv = readFileSync("portfolio_export.csv", "utf-8")
    expect(csv).toContain("AAPL")
    expect(csv).toContain("MSFT")
    expect(csv).toContain("GOOGL")
  })
})

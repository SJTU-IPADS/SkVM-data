import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadStats(): any {
  return JSON.parse(readFileSync("trend_stats.json", "utf-8"))
}

function loadSparkline(): string {
  return readFileSync("sparkline_output.txt", "utf-8").trim()
}

function loadStatsCheck(): string {
  return readFileSync("stats_check.txt", "utf-8").trim()
}

describe("sparkline_output.txt", () => {
  test("file exists", () => {
    expect(existsSync("sparkline_output.txt")).toBe(true)
  })

  test("sparkline is exactly 12 characters long", () => {
    const line = loadSparkline()
    // Count Unicode code points (block chars are single codepoints)
    const chars = [...line]
    expect(chars.length).toBe(12)
  })

  test("sparkline uses Unicode block characters", () => {
    const line = loadSparkline()
    // Block chars: ▁▂▃▄▅▆▇█ (U+2581 to U+2588)
    expect(line).toMatch(/[▁▂▃▄▅▆▇█]{12}/)
  })
})

describe("trend_stats.json", () => {
  test("file exists", () => {
    expect(existsSync("trend_stats.json")).toBe(true)
  })

  test("has all required keys", () => {
    const s = loadStats()
    expect(s).toHaveProperty("data")
    expect(s).toHaveProperty("min")
    expect(s).toHaveProperty("max")
    expect(s).toHaveProperty("mean")
    expect(s).toHaveProperty("total")
    expect(s).toHaveProperty("growth_pct")
    expect(s).toHaveProperty("trend")
  })

  test("data array has 12 values in correct order", () => {
    const s = loadStats()
    expect(Array.isArray(s.data)).toBe(true)
    expect(s.data.length).toBe(12)
    expect(s.data[0]).toBe(45000)
    expect(s.data[11]).toBe(78100)
  })

  test("min and max are correct", () => {
    const s = loadStats()
    expect(s.min).toBe(45000)
    expect(s.max).toBe(78100)
  })

  test("total is correct (708000)", () => {
    const s = loadStats()
    expect(s.total).toBe(708000)
  })

  test("mean is correct (59000.0)", () => {
    const s = loadStats()
    expect(s.mean).toBe(59000.0)
  })

  test("growth_pct is correct (73.56)", () => {
    const s = loadStats()
    // (78100 - 45000) / 45000 * 100 = 73.5555... ≈ 73.56
    expect(s.growth_pct).toBe(73.56)
  })

  test("trend is increasing", () => {
    const s = loadStats()
    expect(s.trend).toBe("increasing")
  })
})

describe("stats_check.txt", () => {
  test("file exists", () => {
    expect(existsSync("stats_check.txt")).toBe(true)
  })

  test("contains PASS", () => {
    const content = loadStatsCheck()
    expect(content).toContain("PASS")
  })
})

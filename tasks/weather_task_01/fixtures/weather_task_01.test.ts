import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  const raw = readFileSync("weather_report.json", "utf-8")
  return JSON.parse(raw)
}

describe("weather_report.json", () => {
  test("file exists", () => {
    expect(existsSync("weather_report.json")).toBe(true)
  })

  test("is valid JSON with an object at top level", () => {
    const data = loadReport()
    expect(typeof data).toBe("object")
    expect(data).not.toBeNull()
    expect(Array.isArray(data)).toBe(false)
  })

  test("has all required fields", () => {
    const data = loadReport()
    expect(data).toHaveProperty("city")
    expect(data).toHaveProperty("country")
    expect(data).toHaveProperty("temperature_c")
    expect(data).toHaveProperty("condition")
    expect(data).toHaveProperty("humidity_pct")
    expect(data).toHaveProperty("wind_kph")
    expect(data).toHaveProperty("fetched_at")
  })

  test("fields have correct types", () => {
    const data = loadReport()
    expect(typeof data.city).toBe("string")
    expect(typeof data.country).toBe("string")
    expect(typeof data.temperature_c).toBe("number")
    expect(typeof data.condition).toBe("string")
    expect(typeof data.humidity_pct).toBe("number")
    expect(typeof data.wind_kph).toBe("number")
    expect(typeof data.fetched_at).toBe("string")
  })

  test("values are within reasonable ranges", () => {
    const data = loadReport()
    // Temperature: -50 to 60 C covers all Earth conditions
    expect(data.temperature_c).toBeGreaterThanOrEqual(-50)
    expect(data.temperature_c).toBeLessThanOrEqual(60)
    // Humidity: 0-100%
    expect(data.humidity_pct).toBeGreaterThanOrEqual(0)
    expect(data.humidity_pct).toBeLessThanOrEqual(100)
    // Wind: 0-300 kph (even extreme storms)
    expect(data.wind_kph).toBeGreaterThanOrEqual(0)
    expect(data.wind_kph).toBeLessThanOrEqual(300)
    // City should mention Tokyo
    expect(data.city.toLowerCase()).toContain("tokyo")
    // Condition should be a non-empty string
    expect(data.condition.length).toBeGreaterThan(0)
  })

  test("fetched_at is a valid ISO 8601 timestamp", () => {
    const data = loadReport()
    const date = new Date(data.fetched_at)
    expect(date.toString()).not.toBe("Invalid Date")
    // Should be a recent timestamp (within the last 24 hours)
    const now = Date.now()
    const fetchedTime = date.getTime()
    expect(fetchedTime).toBeGreaterThan(now - 24 * 60 * 60 * 1000)
    expect(fetchedTime).toBeLessThanOrEqual(now + 60 * 60 * 1000) // allow 1h clock drift
  })
})

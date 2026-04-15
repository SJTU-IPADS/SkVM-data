import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadComparison(): any {
  const raw = readFileSync("weather_comparison.json", "utf-8")
  return JSON.parse(raw)
}

const EXPECTED_CITIES = ["london", "barcelona", "berlin"]

describe("weather_comparison.json", () => {
  test("file exists", () => {
    expect(existsSync("weather_comparison.json")).toBe(true)
  })

  test("has cities array with 3 entries", () => {
    const data = loadComparison()
    expect(Array.isArray(data.cities)).toBe(true)
    expect(data.cities.length).toBe(3)
    const names = data.cities.map((c: any) => c.name.toLowerCase())
    for (const expected of EXPECTED_CITIES) {
      expect(names.some((n: string) => n.includes(expected))).toBe(true)
    }
  })

  test("each city has required fields per city", () => {
    const data = loadComparison()
    for (const city of data.cities) {
      expect(typeof city.name).toBe("string")
      expect(typeof city.temperature_c).toBe("number")
      expect(typeof city.condition).toBe("string")
      expect(typeof city.humidity_pct).toBe("number")
      expect(typeof city.wind_kph).toBe("number")
      expect(typeof city.outdoor_score).toBe("number")
    }
  })

  test("weather values are within reasonable value ranges", () => {
    const data = loadComparison()
    for (const city of data.cities) {
      expect(city.temperature_c).toBeGreaterThanOrEqual(-50)
      expect(city.temperature_c).toBeLessThanOrEqual(60)
      expect(city.humidity_pct).toBeGreaterThanOrEqual(0)
      expect(city.humidity_pct).toBeLessThanOrEqual(100)
      expect(city.wind_kph).toBeGreaterThanOrEqual(0)
      expect(city.wind_kph).toBeLessThanOrEqual(300)
      expect(city.condition.length).toBeGreaterThan(0)
    }
  })

  test("outdoor_score values are 0-100 for each city", () => {
    const data = loadComparison()
    for (const city of data.cities) {
      expect(city.outdoor_score).toBeGreaterThanOrEqual(0)
      expect(city.outdoor_score).toBeLessThanOrEqual(100)
    }
    // Scores should not all be identical (would indicate fabrication)
    const scores = data.cities.map((c: any) => c.outdoor_score)
    const unique = new Set(scores)
    expect(unique.size).toBeGreaterThanOrEqual(2)
  })

  test("recommendation structure is complete", () => {
    const data = loadComparison()
    expect(typeof data.recommendation).toBe("object")
    expect(typeof data.recommendation.best_city).toBe("string")
    expect(data.recommendation.best_city.length).toBeGreaterThan(0)
    expect(typeof data.recommendation.reason).toBe("string")
    expect(data.recommendation.reason.length).toBeGreaterThan(30)
    expect(Array.isArray(data.recommendation.warnings)).toBe(true)
    // best_city should be one of the 3 cities
    const names = data.cities.map((c: any) => c.name.toLowerCase())
    expect(names.some((n: string) => n.includes(data.recommendation.best_city.toLowerCase()) ||
      data.recommendation.best_city.toLowerCase().includes(n))).toBe(true)
    // best_city should have the highest outdoor_score
    const bestEntry = data.cities.find((c: any) =>
      c.name.toLowerCase().includes(data.recommendation.best_city.toLowerCase()) ||
      data.recommendation.best_city.toLowerCase().includes(c.name.toLowerCase())
    )
    if (bestEntry) {
      for (const city of data.cities) {
        expect(bestEntry.outdoor_score).toBeGreaterThanOrEqual(city.outdoor_score)
      }
    }
  })

  test("has valid timestamp", () => {
    const data = loadComparison()
    expect(typeof data.fetched_at).toBe("string")
    const date = new Date(data.fetched_at)
    expect(date.toString()).not.toBe("Invalid Date")
    const now = Date.now()
    expect(date.getTime()).toBeGreaterThan(now - 24 * 60 * 60 * 1000)
    expect(date.getTime()).toBeLessThanOrEqual(now + 60 * 60 * 1000)
  })
})

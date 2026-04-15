import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("weather_report.json", "utf-8"))
}

function loadSummary(): string {
  return readFileSync("weather_summary.txt", "utf-8")
}

describe("weather_report.json", () => {
  test("file exists", () => {
    expect(existsSync("weather_report.json")).toBe(true)
  })

  test("has cities array, hottest_city, coldest_city, fetched_count", () => {
    const r = loadReport()
    expect(r).toHaveProperty("cities")
    expect(r).toHaveProperty("hottest_city")
    expect(r).toHaveProperty("coldest_city")
    expect(r).toHaveProperty("fetched_count")
    expect(Array.isArray(r.cities)).toBe(true)
  })

  test("contains exactly 3 cities", () => {
    const r = loadReport()
    expect(r.cities.length).toBe(3)
  })

  test("city names are London, Tokyo, Sydney", () => {
    const r = loadReport()
    const names = r.cities.map((c: any) => c.city)
    expect(names).toContain("London")
    expect(names).toContain("Tokyo")
    expect(names).toContain("Sydney")
  })

  test("each city has required fields: temp_C, weatherDesc, humidity, windspeedKmph", () => {
    const r = loadReport()
    for (const c of r.cities) {
      expect(c).toHaveProperty("temp_C")
      expect(c).toHaveProperty("weatherDesc")
      expect(c).toHaveProperty("humidity")
      expect(c).toHaveProperty("windspeedKmph")
    }
  })

  test("temp_C is a number for each city", () => {
    const r = loadReport()
    for (const c of r.cities) {
      expect(typeof c.temp_C).toBe("number")
      expect(c.temp_C).toBeGreaterThan(-80)
      expect(c.temp_C).toBeLessThan(60)
    }
  })

  test("humidity and windspeedKmph are numbers", () => {
    const r = loadReport()
    for (const c of r.cities) {
      expect(typeof c.humidity).toBe("number")
      expect(typeof c.windspeedKmph).toBe("number")
      expect(c.humidity).toBeGreaterThanOrEqual(0)
      expect(c.humidity).toBeLessThanOrEqual(100)
    }
  })

  test("fetched_count is 3", () => {
    const r = loadReport()
    expect(r.fetched_count).toBe(3)
  })

  test("hottest_city and coldest_city are valid city names", () => {
    const r = loadReport()
    const names = new Set(["London", "Tokyo", "Sydney"])
    expect(names.has(r.hottest_city)).toBe(true)
    expect(names.has(r.coldest_city)).toBe(true)
  })

  test("hottest_city has the highest temp_C and coldest_city has the lowest", () => {
    const r = loadReport()
    const maxTemp = Math.max(...r.cities.map((c: any) => c.temp_C))
    const minTemp = Math.min(...r.cities.map((c: any) => c.temp_C))
    const hottestCity = r.cities.find((c: any) => c.city === r.hottest_city)
    const coldestCity = r.cities.find((c: any) => c.city === r.coldest_city)
    expect(hottestCity.temp_C).toBe(maxTemp)
    expect(coldestCity.temp_C).toBe(minTemp)
  })

  test("data_source field is present and valid", () => {
    const r = loadReport()
    expect(r).toHaveProperty("data_source")
    expect(["live", "fallback"]).toContain(r.data_source)
  })
})

describe("weather_summary.txt", () => {
  test("file exists", () => {
    expect(existsSync("weather_summary.txt")).toBe(true)
  })

  test("has exactly 3 non-empty lines", () => {
    const txt = loadSummary()
    const lines = txt.trim().split("\n").filter((l: string) => l.trim().length > 0)
    expect(lines.length).toBe(3)
  })

  test("each line contains city name, temperature symbol, and wind speed info", () => {
    const txt = loadSummary()
    const lines = txt.trim().split("\n").filter((l: string) => l.trim().length > 0)
    for (const line of lines) {
      expect(line).toMatch(/°C/)
      expect(line.toLowerCase()).toMatch(/wind|km\/h/)
    }
  })
})

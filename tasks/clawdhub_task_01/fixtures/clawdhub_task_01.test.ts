import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("skill_report.json", "utf-8"))
}

describe("skill_report.json", () => {
  test("skill_report.json exists", () => {
    expect(existsSync("skill_report.json")).toBe(true)
  })

  test("has search_query string", () => {
    const data = loadReport()
    expect(typeof data.search_query).toBe("string")
    expect(data.search_query.length).toBeGreaterThan(0)
  })

  test("search_results is a non-empty array", () => {
    const data = loadReport()
    expect(Array.isArray(data.search_results)).toBe(true)
    expect(data.search_results.length).toBeGreaterThanOrEqual(1)
  })

  test("each search result has name and description", () => {
    const data = loadReport()
    for (const result of data.search_results) {
      expect(typeof result.name).toBe("string")
      expect(result.name.length).toBeGreaterThan(0)
      expect(typeof result.description).toBe("string")
      expect(result.description.length).toBeGreaterThan(0)
    }
  })

  test("installed_skills is an array", () => {
    const data = loadReport()
    expect(Array.isArray(data.installed_skills)).toBe(true)
    for (const skill of data.installed_skills) {
      expect(typeof skill.name).toBe("string")
    }
  })

  test("total_found is a number matching search_results length", () => {
    const data = loadReport()
    expect(typeof data.total_found).toBe("number")
    expect(data.total_found).toBe(data.search_results.length)
  })

  test("summary is at least 80 characters", () => {
    const data = loadReport()
    expect(typeof data.summary).toBe("string")
    expect(data.summary.length).toBeGreaterThanOrEqual(80)
  })
})

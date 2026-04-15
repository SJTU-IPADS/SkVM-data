import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadAnalysis(): any {
  return JSON.parse(readFileSync("skill_analysis.json", "utf-8"))
}

describe("skill_analysis.json", () => {
  test("skill_analysis.json exists", () => {
    expect(existsSync("skill_analysis.json")).toBe(true)
  })

  test("search_results is a non-empty array", () => {
    const data = loadAnalysis()
    expect(Array.isArray(data.search_results)).toBe(true)
    expect(data.search_results.length).toBeGreaterThanOrEqual(1)
    for (const r of data.search_results) {
      expect(typeof r.name).toBe("string")
      expect(typeof r.description).toBe("string")
    }
  })

  test("installed_skill has name and reason", () => {
    const data = loadAnalysis()
    expect(data.installed_skill).toBeDefined()
    expect(typeof data.installed_skill.name).toBe("string")
    expect(data.installed_skill.name.length).toBeGreaterThan(0)
    expect(typeof data.installed_skill.reason).toBe("string")
    expect(data.installed_skill.reason.length).toBeGreaterThanOrEqual(30)
  })

  test("skill_contents has files array", () => {
    const data = loadAnalysis()
    expect(data.skill_contents).toBeDefined()
    expect(Array.isArray(data.skill_contents.files)).toBe(true)
    expect(data.skill_contents.files.length).toBeGreaterThanOrEqual(1)
    expect(typeof data.skill_contents.has_readme).toBe("boolean")
  })

  test("capabilities array with at least 2 entries", () => {
    const data = loadAnalysis()
    expect(Array.isArray(data.capabilities)).toBe(true)
    expect(data.capabilities.length).toBeGreaterThanOrEqual(2)
    for (const cap of data.capabilities) {
      expect(typeof cap).toBe("string")
      expect(cap.length).toBeGreaterThan(10)
    }
  })

  test("install_verified is true", () => {
    const data = loadAnalysis()
    expect(data.install_verified).toBe(true)
  })
})

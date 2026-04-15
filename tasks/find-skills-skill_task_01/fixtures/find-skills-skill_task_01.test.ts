import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadCatalog(): any {
  const raw = readFileSync("skill_catalog.json", "utf-8")
  return JSON.parse(raw)
}

describe("skill_catalog.json", () => {
  test("file exists", () => {
    expect(existsSync("skill_catalog.json")).toBe(true)
  })

  test("has valid JSON structure with top-level fields", () => {
    const data = loadCatalog()
    expect(typeof data).toBe("object")
    expect(data).not.toBeNull()
    expect(typeof data.search_query).toBe("string")
    expect(data.search_query.length).toBeGreaterThan(0)
    expect(typeof data.skill_count).toBe("number")
    expect(Array.isArray(data.skills)).toBe(true)
  })

  test("has at least 1 skill found", () => {
    const data = loadCatalog()
    expect(data.skills.length).toBeGreaterThanOrEqual(1)
    expect(data.skill_count).toBeGreaterThanOrEqual(1)
    expect(data.skill_count).toBe(data.skills.length)
  })

  test("each skill has required skill fields", () => {
    const data = loadCatalog()
    for (const skill of data.skills) {
      expect(typeof skill.name).toBe("string")
      expect(skill.name.length).toBeGreaterThan(0)
      expect(typeof skill.description).toBe("string")
      expect(typeof skill.source).toBe("string")
      expect(skill.source.length).toBeGreaterThan(0)
    }
  })

  test("skill descriptions are substantial", () => {
    const data = loadCatalog()
    for (const skill of data.skills) {
      expect(skill.description.length).toBeGreaterThanOrEqual(20)
    }
  })

  test("has summary of sufficient length", () => {
    const data = loadCatalog()
    expect(typeof data.summary).toBe("string")
    expect(data.summary.length).toBeGreaterThanOrEqual(100)
  })
})

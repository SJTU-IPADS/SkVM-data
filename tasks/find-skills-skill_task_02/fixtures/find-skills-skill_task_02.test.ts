import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadRecommendations(): any {
  const raw = readFileSync("skill_recommendations.json", "utf-8")
  return JSON.parse(raw)
}

describe("skill_recommendations.json", () => {
  test("file exists", () => {
    expect(existsSync("skill_recommendations.json")).toBe(true)
  })

  test("has at least 2 searches recorded", () => {
    const data = loadRecommendations()
    expect(Array.isArray(data.searches)).toBe(true)
    expect(data.searches.length).toBeGreaterThanOrEqual(2)
    for (const search of data.searches) {
      expect(typeof search.query).toBe("string")
      expect(search.query.length).toBeGreaterThan(0)
      expect(typeof search.results_found).toBe("number")
      expect(search.results_found).toBeGreaterThanOrEqual(0)
    }
  })

  test("all_skills array structure is valid", () => {
    const data = loadRecommendations()
    expect(Array.isArray(data.all_skills)).toBe(true)
    expect(data.all_skills.length).toBeGreaterThanOrEqual(1)
    for (const skill of data.all_skills) {
      expect(typeof skill.name).toBe("string")
      expect(skill.name.length).toBeGreaterThan(0)
      expect(typeof skill.description).toBe("string")
      expect(skill.description.length).toBeGreaterThanOrEqual(20)
      expect(typeof skill.category).toBe("string")
    }
  })

  test("skills have valid categories from multiple domains", () => {
    const data = loadRecommendations()
    const categories = new Set(data.all_skills.map((s: any) => s.category.toLowerCase()))
    // Should have at least 2 different categories representing the two search domains
    expect(categories.size).toBeGreaterThanOrEqual(2)
  })

  test("has at least 2 recommendation entries", () => {
    const data = loadRecommendations()
    expect(Array.isArray(data.recommendations)).toBe(true)
    expect(data.recommendations.length).toBeGreaterThanOrEqual(2)
    for (const rec of data.recommendations) {
      expect(typeof rec.skill_name).toBe("string")
      expect(rec.skill_name.length).toBeGreaterThan(0)
      expect(typeof rec.use_case).toBe("string")
      expect(rec.use_case.length).toBeGreaterThanOrEqual(30)
      expect(typeof rec.priority).toBe("string")
    }
  })

  test("recommendations have valid priority levels", () => {
    const data = loadRecommendations()
    const validPriorities = ["high", "medium", "low"]
    for (const rec of data.recommendations) {
      expect(validPriorities).toContain(rec.priority.toLowerCase())
    }
  })

  test("has compatibility notes of sufficient length", () => {
    const data = loadRecommendations()
    expect(typeof data.compatibility_notes).toBe("string")
    expect(data.compatibility_notes.length).toBeGreaterThanOrEqual(100)
  })

  test("total unique skills count matches all_skills length", () => {
    const data = loadRecommendations()
    expect(typeof data.total_unique_skills).toBe("number")
    expect(data.total_unique_skills).toBe(data.all_skills.length)
    // Verify uniqueness by name
    const names = data.all_skills.map((s: any) => s.name.toLowerCase())
    const unique = new Set(names)
    expect(unique.size).toBe(names.length)
  })
})

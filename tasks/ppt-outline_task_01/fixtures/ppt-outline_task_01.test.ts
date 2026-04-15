import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadOutline(): any {
  return JSON.parse(readFileSync("pitch_outline.json", "utf-8"))
}

const REQUIRED_SECTIONS = ["problem", "solution", "market", "product", "business model", "traction", "team", "ask"]

describe("pitch_outline.json", () => {
  test("file exists", () => {
    expect(existsSync("pitch_outline.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const o = loadOutline()
    expect(o).toHaveProperty("company")
    expect(o).toHaveProperty("deck_type")
    expect(o).toHaveProperty("total_slides")
    expect(o).toHaveProperty("sections")
  })

  test("company is FlowSync and deck_type is pitch", () => {
    const o = loadOutline()
    expect(o.company).toBe("FlowSync")
    expect(o.deck_type).toBe("pitch")
  })

  test("sections is an array of exactly 8 elements", () => {
    const o = loadOutline()
    expect(Array.isArray(o.sections)).toBe(true)
    expect(o.sections.length).toBe(8)
  })

  test("each section has title, slide_count, and talking_points", () => {
    const o = loadOutline()
    for (const s of o.sections) {
      expect(s).toHaveProperty("title")
      expect(s).toHaveProperty("slide_count")
      expect(s).toHaveProperty("talking_points")
    }
  })

  test("each slide_count is 1 or 2", () => {
    const o = loadOutline()
    for (const s of o.sections) {
      expect(typeof s.slide_count).toBe("number")
      expect(s.slide_count).toBeGreaterThanOrEqual(1)
      expect(s.slide_count).toBeLessThanOrEqual(2)
    }
  })

  test("total_slides equals sum of section slide_count values", () => {
    const o = loadOutline()
    const sum = o.sections.reduce((acc: number, s: any) => acc + s.slide_count, 0)
    expect(o.total_slides).toBe(sum)
  })

  test("each section has 2 to 4 talking points", () => {
    const o = loadOutline()
    for (const s of o.sections) {
      expect(Array.isArray(s.talking_points)).toBe(true)
      expect(s.talking_points.length).toBeGreaterThanOrEqual(2)
      expect(s.talking_points.length).toBeLessThanOrEqual(4)
    }
  })

  test("all talking points are non-empty strings", () => {
    const o = loadOutline()
    for (const s of o.sections) {
      for (const tp of s.talking_points) {
        expect(typeof tp).toBe("string")
        expect(tp.trim().length).toBeGreaterThan(5)
      }
    }
  })

  test("covers required pitch sections (problem, solution, team, ask present in titles)", () => {
    const o = loadOutline()
    const titles = o.sections.map((s: any) => s.title.toLowerCase())
    const requiredKeywords = ["problem", "solution", "team", "ask"]
    for (const kw of requiredKeywords) {
      expect(titles.some((t: string) => t.includes(kw))).toBe(true)
    }
  })
})

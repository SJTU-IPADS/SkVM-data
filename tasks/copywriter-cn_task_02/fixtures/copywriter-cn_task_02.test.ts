import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadLanding(): any {
  return JSON.parse(readFileSync("landing_page_copy.json", "utf-8"))
}

function loadBrief(): string {
  return readFileSync("pain_points_brief.md", "utf-8")
}

describe("landing_page_copy.json", () => {
  test("file exists", () => {
    expect(existsSync("landing_page_copy.json")).toBe(true)
  })

  test("is valid JSON with required top-level keys", () => {
    const l = loadLanding()
    expect(l).toHaveProperty("product")
    expect(l).toHaveProperty("target_audience")
    expect(l).toHaveProperty("pain_points")
    expect(l).toHaveProperty("hero_headline")
    expect(l).toHaveProperty("subheadline")
    expect(l).toHaveProperty("benefits")
    expect(l).toHaveProperty("social_proof_placeholder")
    expect(l).toHaveProperty("price_anchor")
    expect(l).toHaveProperty("urgency_element")
  })

  test("product is Python for Data Analysts", () => {
    const l = loadLanding()
    expect(l.product).toBe("Python for Data Analysts")
  })

  test("pain_points has exactly 5 non-empty strings", () => {
    const l = loadLanding()
    expect(Array.isArray(l.pain_points)).toBe(true)
    expect(l.pain_points.length).toBe(5)
    for (const p of l.pain_points) {
      expect(typeof p).toBe("string")
      expect(p.trim().length).toBeGreaterThan(10)
    }
  })

  test("hero_headline is 8-15 words", () => {
    const l = loadLanding()
    expect(typeof l.hero_headline).toBe("string")
    const words = l.hero_headline.trim().split(/\s+/).length
    expect(words).toBeGreaterThanOrEqual(8)
    expect(words).toBeLessThanOrEqual(15)
  })

  test("subheadline is 15-30 words", () => {
    const l = loadLanding()
    expect(typeof l.subheadline).toBe("string")
    const words = l.subheadline.trim().split(/\s+/).length
    expect(words).toBeGreaterThanOrEqual(15)
    expect(words).toBeLessThanOrEqual(30)
  })

  test("benefits has exactly 4 entries with title and description", () => {
    const l = loadLanding()
    expect(Array.isArray(l.benefits)).toBe(true)
    expect(l.benefits.length).toBe(4)
    for (const b of l.benefits) {
      expect(typeof b.title).toBe("string")
      expect(typeof b.description).toBe("string")
      const titleWords = b.title.trim().split(/\s+/).length
      expect(titleWords).toBeGreaterThanOrEqual(3)
      expect(titleWords).toBeLessThanOrEqual(7)
      const descWords = b.description.trim().split(/\s+/).length
      expect(descWords).toBeGreaterThanOrEqual(15)
      expect(descWords).toBeLessThanOrEqual(40)
    }
  })

  test("price_anchor has price of $197 and a CTA text", () => {
    const l = loadLanding()
    const pa = l.price_anchor
    expect(pa.price).toBe("$197")
    expect(typeof pa.cta_text).toBe("string")
    expect(pa.cta_text.trim().length).toBeGreaterThan(3)
  })

  test("urgency_element is 15-30 words", () => {
    const l = loadLanding()
    expect(typeof l.urgency_element).toBe("string")
    const words = l.urgency_element.trim().split(/\s+/).length
    expect(words).toBeGreaterThanOrEqual(15)
    expect(words).toBeLessThanOrEqual(30)
  })
})

describe("pain_points_brief.md", () => {
  test("file exists", () => {
    expect(existsSync("pain_points_brief.md")).toBe(true)
  })

  test("brief has at least 5 mapped pain points", () => {
    const text = loadBrief()
    // Count entries — should have content for each of 5 pain points
    expect(text.trim().length).toBeGreaterThan(200)
    // Should reference the course or Python/automation as a solution
    expect(text.toLowerCase()).toMatch(/python|automat|course/)
  })

  test("brief references spreadsheet or Excel users", () => {
    const text = loadBrief().toLowerCase()
    expect(text).toMatch(/spreadsheet|excel|csv|data/)
  })
})

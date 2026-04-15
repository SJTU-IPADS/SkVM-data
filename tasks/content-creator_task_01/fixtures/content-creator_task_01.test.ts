import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadPost(): any {
  return JSON.parse(readFileSync("blog_post.json", "utf-8"))
}

describe("blog_post.json", () => {
  test("file exists", () => {
    expect(existsSync("blog_post.json")).toBe(true)
  })

  test("valid JSON with required top-level fields", () => {
    const p = loadPost()
    expect(p).toHaveProperty("task_type")
    expect(p).toHaveProperty("title")
    expect(p).toHaveProperty("meta_description")
    expect(p).toHaveProperty("word_count")
    expect(p).toHaveProperty("sections")
    expect(p).toHaveProperty("tools_covered")
    expect(p).toHaveProperty("target_keyword")
    expect(p).toHaveProperty("cta")
  })

  test("task_type is writing", () => {
    const p = loadPost()
    expect(p.task_type).toBe("writing")
  })

  test("target_keyword is exactly 'productivity tools for remote teams'", () => {
    const p = loadPost()
    expect(p.target_keyword).toBe("productivity tools for remote teams")
  })

  test("tools_covered has exactly 5 tool names", () => {
    const p = loadPost()
    expect(Array.isArray(p.tools_covered)).toBe(true)
    expect(p.tools_covered.length).toBe(5)
    for (const tool of p.tools_covered) {
      expect(typeof tool).toBe("string")
      expect(tool.length).toBeGreaterThan(0)
    }
  })

  test("sections array has at least 7 entries", () => {
    const p = loadPost()
    expect(Array.isArray(p.sections)).toBe(true)
    expect(p.sections.length).toBeGreaterThanOrEqual(7)
  })

  test("each section has heading and content fields", () => {
    const p = loadPost()
    for (const s of p.sections) {
      expect(s).toHaveProperty("heading")
      expect(s).toHaveProperty("content")
      expect(typeof s.heading).toBe("string")
      expect(typeof s.content).toBe("string")
      expect(s.heading.length).toBeGreaterThan(0)
      expect(s.content.length).toBeGreaterThan(0)
    }
  })

  test("meta_description is between 100 and 200 characters", () => {
    const p = loadPost()
    expect(typeof p.meta_description).toBe("string")
    expect(p.meta_description.length).toBeGreaterThanOrEqual(100)
    expect(p.meta_description.length).toBeLessThanOrEqual(200)
  })

  test("word_count is a positive integer", () => {
    const p = loadPost()
    expect(typeof p.word_count).toBe("number")
    expect(Number.isInteger(p.word_count)).toBe(true)
    expect(p.word_count).toBeGreaterThan(0)
  })

  test("word_count is at least 400 words (substantive content)", () => {
    const p = loadPost()
    expect(p.word_count).toBeGreaterThanOrEqual(400)
  })

  test("cta is a non-empty string", () => {
    const p = loadPost()
    expect(typeof p.cta).toBe("string")
    expect(p.cta.length).toBeGreaterThan(10)
  })
})

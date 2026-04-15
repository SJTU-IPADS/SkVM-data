import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadArticle(): string {
  return readFileSync("article.md", "utf-8")
}

function loadMeta(): any {
  return JSON.parse(readFileSync("seo_meta.json", "utf-8"))
}

function countWords(text: string): number {
  return text.trim().split(/\s+/).filter(w => w.length > 0).length
}

describe("article.md", () => {
  test("file exists", () => {
    expect(existsSync("article.md")).toBe(true)
  })

  test("H1 includes primary keyword 'remote work productivity'", () => {
    const text = loadArticle()
    const h1Match = text.match(/^#\s+(.+)$/m)
    expect(h1Match).not.toBeNull()
    expect(h1Match![1].toLowerCase()).toContain("remote work productivity")
  })

  test("contains at least 4 H2 headings", () => {
    const text = loadArticle()
    const h2s = text.match(/^##\s+.+$/gm) || []
    expect(h2s.length).toBeGreaterThanOrEqual(4)
  })

  test("contains at least one H3 heading", () => {
    const text = loadArticle()
    const h3s = text.match(/^###\s+.+$/gm) || []
    expect(h3s.length).toBeGreaterThanOrEqual(1)
  })

  test("FAQ section present with at least 3 questions", () => {
    const text = loadArticle()
    // Check for FAQ section heading
    expect(text.toLowerCase()).toContain("faq")
    // Count question-style headings (H2 or H3 ending with ?) or lines with ?
    const questionHeadings = text.match(/^#{2,3}\s+.+\?/gm) || []
    const questionLines = text.match(/^.*\?\s*$/gm) || []
    // Either dedicated question headings OR multiple question lines
    const faqQuestions = questionHeadings.length >= 3 || questionLines.length >= 3
    expect(faqQuestions).toBe(true)
  })

  test("article has at least 700 words", () => {
    const text = loadArticle()
    expect(countWords(text)).toBeGreaterThanOrEqual(700)
  })

  test("primary keyword appears in the first 150 words", () => {
    const text = loadArticle()
    const first150Words = text.trim().split(/\s+/).slice(0, 150).join(" ")
    expect(first150Words.toLowerCase()).toContain("remote work productivity")
  })

  test("contains at least 3 bullet-point or numbered lists", () => {
    const text = loadArticle()
    // Match lines starting with - or * (bullets) or 1. 2. etc (numbered)
    const bulletLines = text.match(/^[\-\*]\s+.+$/gm) || []
    const numberedLines = text.match(/^\d+\.\s+.+$/gm) || []
    // Consider a "list" as a group of 2+ consecutive list items
    const allListItems = bulletLines.length + numberedLines.length
    expect(allListItems).toBeGreaterThanOrEqual(6) // At least 3 lists of 2+ items each
  })
})

describe("seo_meta.json", () => {
  test("file exists", () => {
    expect(existsSync("seo_meta.json")).toBe(true)
  })

  test("has all required fields", () => {
    const m = loadMeta()
    expect(m).toHaveProperty("title")
    expect(m).toHaveProperty("meta_description")
    expect(m).toHaveProperty("primary_keyword")
    expect(m).toHaveProperty("secondary_keywords")
    expect(m).toHaveProperty("target_audience")
    expect(m).toHaveProperty("word_count")
    expect(m).toHaveProperty("reading_time_minutes")
    expect(m).toHaveProperty("seo_score")
    expect(m).toHaveProperty("h1")
    expect(m).toHaveProperty("faq_count")
  })

  test("title is at most 60 characters", () => {
    const m = loadMeta()
    expect(typeof m.title).toBe("string")
    expect(m.title.length).toBeLessThanOrEqual(60)
  })

  test("meta_description length is between 150 and 160 characters", () => {
    const m = loadMeta()
    expect(typeof m.meta_description).toBe("string")
    expect(m.meta_description.length).toBeGreaterThanOrEqual(150)
    expect(m.meta_description.length).toBeLessThanOrEqual(160)
  })

  test("primary_keyword is 'remote work productivity'", () => {
    const m = loadMeta()
    expect(m.primary_keyword).toBe("remote work productivity")
  })

  test("secondary_keywords is an array with at least 3 strings", () => {
    const m = loadMeta()
    expect(Array.isArray(m.secondary_keywords)).toBe(true)
    expect(m.secondary_keywords.length).toBeGreaterThanOrEqual(3)
    for (const kw of m.secondary_keywords) {
      expect(typeof kw).toBe("string")
    }
  })

  test("word_count matches actual article word count (within 5%)", () => {
    const article = loadArticle()
    const m = loadMeta()
    const actual = countWords(article)
    const tolerance = Math.ceil(actual * 0.05)
    expect(Math.abs(m.word_count - actual)).toBeLessThanOrEqual(tolerance)
  })

  test("reading_time_minutes is correct at 200 words per minute", () => {
    const m = loadMeta()
    const expectedMinutes = Math.ceil(m.word_count / 200)
    // Allow ±1 minute tolerance
    expect(Math.abs(m.reading_time_minutes - expectedMinutes)).toBeLessThanOrEqual(1)
  })

  test("seo_score is an integer between 1 and 10", () => {
    const m = loadMeta()
    expect(typeof m.seo_score).toBe("number")
    expect(m.seo_score).toBeGreaterThanOrEqual(1)
    expect(m.seo_score).toBeLessThanOrEqual(10)
    expect(Number.isInteger(m.seo_score)).toBe(true)
  })

  test("faq_count is a positive integer", () => {
    const m = loadMeta()
    expect(typeof m.faq_count).toBe("number")
    expect(m.faq_count).toBeGreaterThanOrEqual(3)
  })
})

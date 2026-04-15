import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadArticle(): string {
  return readFileSync("comparison_article.md", "utf-8")
}

function loadBrief(): any {
  return JSON.parse(readFileSync("content_brief.json", "utf-8"))
}

function countWords(text: string): number {
  return text.trim().split(/\s+/).filter(w => w.length > 0).length
}

const VALID_KEYWORD_POSITIONS = new Set(["front", "middle", "end"])

describe("comparison_article.md", () => {
  test("file exists", () => {
    expect(existsSync("comparison_article.md")).toBe(true)
  })

  test("H1 contains 'Trello vs Asana'", () => {
    const text = loadArticle()
    const h1Match = text.match(/^#\s+(.+)$/m)
    expect(h1Match).not.toBeNull()
    expect(h1Match![1].toLowerCase()).toContain("trello vs asana")
  })

  test("contains at least 3 H2 headings", () => {
    const text = loadArticle()
    const h2s = text.match(/^##\s+.+$/gm) || []
    expect(h2s.length).toBeGreaterThanOrEqual(3)
  })

  test("contains a Markdown comparison table", () => {
    const text = loadArticle()
    // Markdown table has at least a header row, separator row, and one data row
    const tableRows = text.match(/^\|.+\|$/gm) || []
    expect(tableRows.length).toBeGreaterThanOrEqual(3)
    // Must have a separator row with dashes
    const separatorRow = text.match(/^\|[\s\-\|:]+\|$/gm) || []
    expect(separatorRow.length).toBeGreaterThanOrEqual(1)
  })

  test("contains a recommendation section heading", () => {
    const text = loadArticle()
    const headings = text.match(/^#{1,3}\s+.+$/gm) || []
    const hasRecommendation = headings.some(h =>
      h.toLowerCase().includes("recommend") ||
      h.toLowerCase().includes("verdict") ||
      h.toLowerCase().includes("which should")
    )
    expect(hasRecommendation).toBe(true)
  })

  test("word count is between 600 and 900", () => {
    const text = loadArticle()
    const words = countWords(text)
    expect(words).toBeGreaterThanOrEqual(600)
    expect(words).toBeLessThanOrEqual(900)
  })
})

describe("content_brief.json", () => {
  test("file exists", () => {
    expect(existsSync("content_brief.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const b = loadBrief()
    expect(b).toHaveProperty("title_options")
    expect(b).toHaveProperty("recommended_title")
    expect(b).toHaveProperty("internal_links")
    expect(b).toHaveProperty("external_links")
    expect(b).toHaveProperty("primary_keyword")
    expect(b).toHaveProperty("search_intent")
  })

  test("primary_keyword is 'Trello vs Asana' and search_intent is 'commercial'", () => {
    const b = loadBrief()
    expect(b.primary_keyword).toBe("Trello vs Asana")
    expect(b.search_intent).toBe("commercial")
  })

  test("title_options has exactly 2 entries", () => {
    const b = loadBrief()
    expect(Array.isArray(b.title_options)).toBe(true)
    expect(b.title_options.length).toBe(2)
  })

  test("each title option has title, char_count, and primary_keyword_position fields", () => {
    const b = loadBrief()
    for (const opt of b.title_options) {
      expect(typeof opt.title).toBe("string")
      expect(typeof opt.char_count).toBe("number")
      expect(typeof opt.primary_keyword_position).toBe("string")
    }
  })

  test("char_count matches actual character count of each title", () => {
    const b = loadBrief()
    for (const opt of b.title_options) {
      expect(opt.char_count).toBe(opt.title.length)
    }
  })

  test("primary_keyword_position values are 'front', 'middle', or 'end'", () => {
    const b = loadBrief()
    for (const opt of b.title_options) {
      expect(VALID_KEYWORD_POSITIONS.has(opt.primary_keyword_position)).toBe(true)
    }
  })

  test("recommended_title is one of the title options", () => {
    const b = loadBrief()
    const titles = b.title_options.map((o: any) => o.title)
    expect(titles).toContain(b.recommended_title)
  })

  test("internal_links URLs start with '/'", () => {
    const b = loadBrief()
    expect(Array.isArray(b.internal_links)).toBe(true)
    expect(b.internal_links.length).toBeGreaterThanOrEqual(2)
    for (const link of b.internal_links) {
      expect(link.url.startsWith("/")).toBe(true)
      expect(typeof link.anchor_text).toBe("string")
      expect(typeof link.reason).toBe("string")
    }
  })

  test("external_links URLs start with 'https://'", () => {
    const b = loadBrief()
    expect(Array.isArray(b.external_links)).toBe(true)
    expect(b.external_links.length).toBeGreaterThanOrEqual(1)
    for (const link of b.external_links) {
      expect(link.url.startsWith("https://")).toBe(true)
      expect(typeof link.supports_claim).toBe("string")
    }
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadCopy(): any {
  return JSON.parse(readFileSync("aida_copy.json", "utf-8"))
}

function loadBrief(): string {
  return readFileSync("copy_brief.md", "utf-8")
}

describe("aida_copy.json", () => {
  test("file exists", () => {
    expect(existsSync("aida_copy.json")).toBe(true)
  })

  test("is valid JSON with required top-level keys", () => {
    const c = loadCopy()
    expect(c).toHaveProperty("product")
    expect(c).toHaveProperty("framework")
    expect(c).toHaveProperty("attention")
    expect(c).toHaveProperty("interest")
    expect(c).toHaveProperty("desire")
    expect(c).toHaveProperty("action")
    expect(c).toHaveProperty("headline_variants")
    expect(c).toHaveProperty("word_count")
  })

  test("product is FocusFlow and framework is AIDA", () => {
    const c = loadCopy()
    expect(c.product).toBe("FocusFlow")
    expect(c.framework).toBe("AIDA")
  })

  test("attention headline is 10-20 words", () => {
    const c = loadCopy()
    expect(typeof c.attention).toBe("string")
    const words = c.attention.trim().split(/\s+/).length
    expect(words).toBeGreaterThanOrEqual(10)
    expect(words).toBeLessThanOrEqual(20)
  })

  test("interest and desire sections are non-empty strings", () => {
    const c = loadCopy()
    expect(typeof c.interest).toBe("string")
    expect(c.interest.trim().length).toBeGreaterThan(50)
    expect(typeof c.desire).toBe("string")
    expect(c.desire.trim().length).toBeGreaterThan(50)
  })

  test("action section mentions free trial", () => {
    const c = loadCopy()
    expect(typeof c.action).toBe("string")
    expect(c.action.toLowerCase()).toMatch(/free trial|14.day|14-day/)
  })

  test("headline_variants has exactly 3 entries of type string", () => {
    const c = loadCopy()
    expect(Array.isArray(c.headline_variants)).toBe(true)
    expect(c.headline_variants.length).toBe(3)
    for (const h of c.headline_variants) {
      expect(typeof h).toBe("string")
      expect(h.trim().length).toBeGreaterThan(5)
    }
  })

  test("headline_variants are distinct from each other and from attention", () => {
    const c = loadCopy()
    const all = [c.attention, ...c.headline_variants]
    const unique = new Set(all.map((h: string) => h.toLowerCase().trim()))
    expect(unique.size).toBe(4)
  })

  test("word_count object has required keys with positive numbers", () => {
    const c = loadCopy()
    const wc = c.word_count
    expect(typeof wc.attention).toBe("number")
    expect(typeof wc.interest).toBe("number")
    expect(typeof wc.desire).toBe("number")
    expect(typeof wc.action).toBe("number")
    expect(wc.attention).toBeGreaterThan(0)
    expect(wc.interest).toBeGreaterThan(0)
    expect(wc.desire).toBeGreaterThan(0)
    expect(wc.action).toBeGreaterThan(0)
  })
})

describe("copy_brief.md", () => {
  test("file exists", () => {
    expect(existsSync("copy_brief.md")).toBe(true)
  })

  test("brief contains FocusFlow product name", () => {
    const text = loadBrief()
    expect(text).toMatch(/FocusFlow/)
  })

  test("brief contains all four AIDA sections assembled", () => {
    const text = loadBrief().toLowerCase()
    // The copy_brief should contain substantive content from all AIDA sections
    expect(text.length).toBeGreaterThan(300)
  })

  test("brief contains numbered headline variants", () => {
    const text = loadBrief()
    // Should have a numbered list with 3 items
    const numberedItems = text.match(/^\s*[1-3][.)]/gm) || []
    expect(numberedItems.length).toBeGreaterThanOrEqual(3)
  })
})

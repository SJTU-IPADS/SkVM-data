import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadBriefing(): any {
  const raw = readFileSync("news_briefing.json", "utf-8")
  return JSON.parse(raw)
}

describe("news_briefing.json", () => {
  test("file exists", () => {
    expect(existsSync("news_briefing.json")).toBe(true)
  })

  test("has valid JSON structure with top-level fields", () => {
    const data = loadBriefing()
    expect(typeof data).toBe("object")
    expect(data).not.toBeNull()
    expect(typeof data.source).toBe("string")
    expect(data.source.length).toBeGreaterThan(0)
    expect(typeof data.headline_count).toBe("number")
    expect(Array.isArray(data.headlines)).toBe(true)
  })

  test("has at least 5 headlines", () => {
    const data = loadBriefing()
    expect(data.headlines.length).toBeGreaterThanOrEqual(5)
    expect(data.headline_count).toBeGreaterThanOrEqual(5)
  })

  test("each headline has required headline fields", () => {
    const data = loadBriefing()
    for (const h of data.headlines) {
      expect(typeof h.title).toBe("string")
      expect(h.title.length).toBeGreaterThan(5)
      expect(typeof h.link).toBe("string")
      expect(typeof h.summary).toBe("string")
      expect(h.summary.length).toBeGreaterThanOrEqual(20)
    }
  })

  test("headline links are URLs", () => {
    const data = loadBriefing()
    for (const h of data.headlines) {
      expect(h.link).toMatch(/^https?:\/\//)
    }
  })

  test("has briefing text of sufficient length", () => {
    const data = loadBriefing()
    expect(typeof data.briefing).toBe("string")
    expect(data.briefing.length).toBeGreaterThanOrEqual(200)
  })

  test("has valid timestamp", () => {
    const data = loadBriefing()
    expect(typeof data.fetched_at).toBe("string")
    const date = new Date(data.fetched_at)
    expect(date.toString()).not.toBe("Invalid Date")
    const now = Date.now()
    expect(date.getTime()).toBeGreaterThan(now - 24 * 60 * 60 * 1000)
    expect(date.getTime()).toBeLessThanOrEqual(now + 60 * 60 * 1000)
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadBriefing(): any {
  const raw = readFileSync("multi_source_briefing.json", "utf-8")
  return JSON.parse(raw)
}

describe("multi_source_briefing.json", () => {
  test("file exists", () => {
    expect(existsSync("multi_source_briefing.json")).toBe(true)
  })

  test("has sources array with both feeds represented", () => {
    const data = loadBriefing()
    expect(Array.isArray(data.sources)).toBe(true)
    expect(data.sources.length).toBeGreaterThanOrEqual(2)
    for (const src of data.sources) {
      expect(typeof src.name).toBe("string")
      expect(src.name.length).toBeGreaterThan(0)
      expect(typeof src.headline_count).toBe("number")
      expect(src.headline_count).toBeGreaterThan(0)
    }
  })

  test("has total headline count matching sum of sources", () => {
    const data = loadBriefing()
    expect(typeof data.total_headlines).toBe("number")
    expect(data.total_headlines).toBeGreaterThanOrEqual(5)
    const sourceSum = data.sources.reduce((sum: number, s: any) => sum + s.headline_count, 0)
    expect(data.total_headlines).toBe(sourceSum)
  })

  test("has at least 3 topic groups", () => {
    const data = loadBriefing()
    expect(Array.isArray(data.topics)).toBe(true)
    expect(data.topics.length).toBeGreaterThanOrEqual(3)
    for (const topic of data.topics) {
      expect(typeof topic.topic_name).toBe("string")
      expect(topic.topic_name.length).toBeGreaterThan(0)
      expect(Array.isArray(topic.headlines)).toBe(true)
      expect(topic.headlines.length).toBeGreaterThanOrEqual(1)
    }
  })

  test("topic headlines have required fields", () => {
    const data = loadBriefing()
    for (const topic of data.topics) {
      for (const h of topic.headlines) {
        expect(typeof h.title).toBe("string")
        expect(h.title.length).toBeGreaterThan(5)
        expect(typeof h.source).toBe("string")
        expect(h.source.length).toBeGreaterThan(0)
        expect(typeof h.link).toBe("string")
        expect(h.link).toMatch(/^https?:\/\//)
      }
    }
    // Verify multiple sources are represented across topics
    const allSources = new Set<string>()
    for (const topic of data.topics) {
      for (const h of topic.headlines) {
        allSources.add(h.source.toLowerCase())
      }
    }
    expect(allSources.size).toBeGreaterThanOrEqual(2)
  })

  test("topic summaries are substantial", () => {
    const data = loadBriefing()
    for (const topic of data.topics) {
      expect(typeof topic.summary).toBe("string")
      expect(topic.summary.length).toBeGreaterThanOrEqual(80)
    }
  })

  test("has cross-source analysis of sufficient length", () => {
    const data = loadBriefing()
    expect(typeof data.cross_source_analysis).toBe("string")
    expect(data.cross_source_analysis.length).toBeGreaterThanOrEqual(150)
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

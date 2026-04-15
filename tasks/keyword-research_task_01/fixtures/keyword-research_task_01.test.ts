import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadKeywords(): any[] {
  return JSON.parse(readFileSync("keywords.json", "utf-8"))
}

function loadReport(): any {
  return JSON.parse(readFileSync("keyword_report.json", "utf-8"))
}

describe("keywords.json", () => {
  test("file exists", () => {
    expect(existsSync("keywords.json")).toBe(true)
  })

  test("is a JSON array with at least 15 entries", () => {
    const kws = loadKeywords()
    expect(Array.isArray(kws)).toBe(true)
    expect(kws.length).toBeGreaterThanOrEqual(15)
  })

  test("each entry has required fields", () => {
    const kws = loadKeywords()
    for (const kw of kws) {
      expect(kw).toHaveProperty("keyword")
      expect(kw).toHaveProperty("intent")
      expect(kw).toHaveProperty("difficulty")
      expect(kw).toHaveProperty("volume_estimate")
      expect(kw).toHaveProperty("opportunity_score")
      expect(kw).toHaveProperty("geo_potential")
    }
  })

  test("intent values are valid", () => {
    const validIntents = new Set(["informational", "navigational", "commercial", "transactional"])
    const kws = loadKeywords()
    for (const kw of kws) {
      expect(validIntents.has(kw.intent)).toBe(true)
    }
  })

  test("difficulty is an integer between 1 and 100", () => {
    const kws = loadKeywords()
    for (const kw of kws) {
      expect(Number.isInteger(kw.difficulty)).toBe(true)
      expect(kw.difficulty).toBeGreaterThanOrEqual(1)
      expect(kw.difficulty).toBeLessThanOrEqual(100)
    }
  })

  test("volume_estimate is one of low, medium, high", () => {
    const valid = new Set(["low", "medium", "high"])
    const kws = loadKeywords()
    for (const kw of kws) {
      expect(valid.has(kw.volume_estimate)).toBe(true)
    }
  })

  test("opportunity_score is a number between 0 and 10", () => {
    const kws = loadKeywords()
    for (const kw of kws) {
      expect(typeof kw.opportunity_score).toBe("number")
      expect(kw.opportunity_score).toBeGreaterThanOrEqual(0)
      expect(kw.opportunity_score).toBeLessThanOrEqual(10)
    }
  })

  test("geo_potential is boolean", () => {
    const kws = loadKeywords()
    for (const kw of kws) {
      expect(typeof kw.geo_potential).toBe("boolean")
    }
  })
})

describe("keyword_report.json", () => {
  test("file exists", () => {
    expect(existsSync("keyword_report.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const r = loadReport()
    expect(r).toHaveProperty("topic")
    expect(r).toHaveProperty("total_keywords")
    expect(r).toHaveProperty("quick_wins")
    expect(r).toHaveProperty("top_geo_keywords")
    expect(r).toHaveProperty("intent_breakdown")
    expect(r).toHaveProperty("recommendation")
  })

  test("total_keywords matches keywords.json length", () => {
    const kws = loadKeywords()
    const r = loadReport()
    expect(Number(r.total_keywords)).toBe(kws.length)
  })

  test("intent_breakdown has all four intent keys", () => {
    const r = loadReport()
    expect(r.intent_breakdown).toHaveProperty("informational")
    expect(r.intent_breakdown).toHaveProperty("navigational")
    expect(r.intent_breakdown).toHaveProperty("commercial")
    expect(r.intent_breakdown).toHaveProperty("transactional")
  })

  test("recommendation is a non-empty string", () => {
    const r = loadReport()
    expect(typeof r.recommendation).toBe("string")
    expect(r.recommendation.length).toBeGreaterThan(20)
  })
})

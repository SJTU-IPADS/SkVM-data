import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadPlan(): any {
  return JSON.parse(readFileSync("cluster_plan.json", "utf-8"))
}

describe("cluster_plan.json", () => {
  test("file exists", () => {
    expect(existsSync("cluster_plan.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const p = loadPlan()
    expect(p).toHaveProperty("niche")
    expect(p).toHaveProperty("clusters")
    expect(p).toHaveProperty("content_calendar")
  })

  test("niche field is correct", () => {
    const p = loadPlan()
    expect(p.niche).toBe("home fitness for beginners")
  })

  test("clusters is an array of exactly 3 entries", () => {
    const p = loadPlan()
    expect(Array.isArray(p.clusters)).toBe(true)
    expect(p.clusters.length).toBe(3)
  })

  test("each cluster has required fields with correct types", () => {
    const validIntents = new Set(["informational", "navigational", "commercial", "transactional"])
    const p = loadPlan()
    for (const c of p.clusters) {
      expect(c).toHaveProperty("pillar_keyword")
      expect(c).toHaveProperty("pillar_intent")
      expect(c).toHaveProperty("pillar_difficulty")
      expect(c).toHaveProperty("cluster_keywords")
      expect(typeof c.pillar_keyword).toBe("string")
      expect(validIntents.has(c.pillar_intent)).toBe(true)
      expect(Number.isInteger(c.pillar_difficulty)).toBe(true)
      expect(c.pillar_difficulty).toBeGreaterThanOrEqual(1)
      expect(c.pillar_difficulty).toBeLessThanOrEqual(100)
    }
  })

  test("each cluster has at least 4 cluster_keywords", () => {
    const p = loadPlan()
    for (const c of p.clusters) {
      expect(Array.isArray(c.cluster_keywords)).toBe(true)
      expect(c.cluster_keywords.length).toBeGreaterThanOrEqual(4)
    }
  })

  test("each cluster_keyword entry has required fields", () => {
    const validIntents = new Set(["informational", "navigational", "commercial", "transactional"])
    const p = loadPlan()
    for (const c of p.clusters) {
      for (const kw of c.cluster_keywords) {
        expect(kw).toHaveProperty("keyword")
        expect(kw).toHaveProperty("intent")
        expect(kw).toHaveProperty("difficulty")
        expect(kw).toHaveProperty("content_type")
        expect(validIntents.has(kw.intent)).toBe(true)
        expect(Number.isInteger(kw.difficulty)).toBe(true)
      }
    }
  })

  test("content_calendar is an array of exactly 6 entries", () => {
    const p = loadPlan()
    expect(Array.isArray(p.content_calendar)).toBe(true)
    expect(p.content_calendar.length).toBe(6)
  })

  test("each calendar entry has week, keyword, content_type, and priority", () => {
    const validPriorities = new Set(["high", "medium", "low"])
    const p = loadPlan()
    for (const entry of p.content_calendar) {
      expect(entry).toHaveProperty("week")
      expect(entry).toHaveProperty("keyword")
      expect(entry).toHaveProperty("content_type")
      expect(entry).toHaveProperty("priority")
      expect(validPriorities.has(entry.priority)).toBe(true)
    }
  })

  test("calendar week numbers cover 1 through 6", () => {
    const p = loadPlan()
    const weeks = p.content_calendar.map((e: any) => Number(e.week)).sort((a: number, b: number) => a - b)
    expect(weeks).toEqual([1, 2, 3, 4, 5, 6])
  })
})

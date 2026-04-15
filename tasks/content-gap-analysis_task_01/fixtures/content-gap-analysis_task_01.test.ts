import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadGaps(): any {
  return JSON.parse(readFileSync("content_gaps.json", "utf-8"))
}

// My 5 topics that should NOT appear in gap_topics
const MY_TOPICS = new Set([
  "beginner workout routines",
  "protein intake guide",
  "running tips for beginners",
  "home gym equipment basics",
  "weight loss meal plan",
])

describe("content_gaps.json", () => {
  test("file exists", () => {
    expect(existsSync("content_gaps.json")).toBe(true)
  })

  test("valid JSON with required top-level fields", () => {
    const g = loadGaps()
    expect(g).toHaveProperty("my_site")
    expect(g).toHaveProperty("my_topic_count")
    expect(g).toHaveProperty("competitor_topic_counts")
    expect(g).toHaveProperty("gap_topics")
    expect(g).toHaveProperty("total_gaps_found")
    expect(g).toHaveProperty("tier1_count")
    expect(g).toHaveProperty("quick_wins")
    expect(g).toHaveProperty("coverage_score")
  })

  test("my_site is fitnessblog.example.com and my_topic_count is 5", () => {
    const g = loadGaps()
    expect(g.my_site).toBe("fitnessblog.example.com")
    expect(g.my_topic_count).toBe(5)
  })

  test("competitor_topic_counts has correct counts for both competitors", () => {
    const g = loadGaps()
    expect(g.competitor_topic_counts).toHaveProperty("fitnessworld.example.com")
    expect(g.competitor_topic_counts).toHaveProperty("healthpeak.example.com")
    // fitnessworld has 12 topics, healthpeak has 12 topics
    expect(g.competitor_topic_counts["fitnessworld.example.com"]).toBe(12)
    expect(g.competitor_topic_counts["healthpeak.example.com"]).toBe(12)
  })

  test("gap_topics is array with at least 10 entries", () => {
    const g = loadGaps()
    expect(Array.isArray(g.gap_topics)).toBe(true)
    expect(g.gap_topics.length).toBeGreaterThanOrEqual(10)
  })

  test("each gap topic has required fields with valid values", () => {
    const g = loadGaps()
    const validPriorities = new Set(["tier1", "tier2", "tier3"])
    const validPotentials = new Set(["high", "medium", "low"])
    for (const t of g.gap_topics) {
      expect(t).toHaveProperty("topic")
      expect(t).toHaveProperty("covered_by")
      expect(t).toHaveProperty("priority")
      expect(t).toHaveProperty("estimated_traffic_potential")
      expect(t).toHaveProperty("content_type_recommendation")
      expect(Array.isArray(t.covered_by)).toBe(true)
      expect(validPriorities.has(t.priority)).toBe(true)
      expect(validPotentials.has(t.estimated_traffic_potential)).toBe(true)
    }
  })

  test("gap topics do not include topics already on my site", () => {
    const g = loadGaps()
    for (const t of g.gap_topics) {
      const topicLower = t.topic.toLowerCase()
      expect(MY_TOPICS.has(topicLower)).toBe(false)
    }
  })

  test("total_gaps_found matches length of gap_topics array", () => {
    const g = loadGaps()
    expect(g.total_gaps_found).toBe(g.gap_topics.length)
  })

  test("tier1_count matches count of tier1 items in gap_topics", () => {
    const g = loadGaps()
    const tier1 = g.gap_topics.filter((t: any) => t.priority === "tier1")
    expect(g.tier1_count).toBe(tier1.length)
  })

  test("quick_wins array is non-empty and contains strings", () => {
    const g = loadGaps()
    expect(Array.isArray(g.quick_wins)).toBe(true)
    expect(g.quick_wins.length).toBeGreaterThanOrEqual(1)
    for (const w of g.quick_wins) {
      expect(typeof w).toBe("string")
    }
  })

  test("coverage_score is a number between 0 and 100", () => {
    const g = loadGaps()
    expect(typeof g.coverage_score).toBe("number")
    expect(g.coverage_score).toBeGreaterThan(0)
    expect(g.coverage_score).toBeLessThanOrEqual(100)
  })
})

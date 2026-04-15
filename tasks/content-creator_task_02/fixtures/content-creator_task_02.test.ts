import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadPlan(): any {
  return JSON.parse(readFileSync("content_plan.json", "utf-8"))
}

describe("content_plan.json", () => {
  test("file exists", () => {
    expect(existsSync("content_plan.json")).toBe(true)
  })

  test("valid JSON with required top-level fields", () => {
    const p = loadPlan()
    expect(p).toHaveProperty("task_type")
    expect(p).toHaveProperty("pillar_topic")
    expect(p).toHaveProperty("target_audience")
    expect(p).toHaveProperty("cluster_topics")
    expect(p).toHaveProperty("content_calendar")
    expect(p).toHaveProperty("success_metrics")
  })

  test("task_type is planning", () => {
    const p = loadPlan()
    expect(p.task_type).toBe("planning")
  })

  test("target_audience is exactly 'small business owners'", () => {
    const p = loadPlan()
    expect(p.target_audience).toBe("small business owners")
  })

  test("cluster_topics has at least 8 entries", () => {
    const p = loadPlan()
    expect(Array.isArray(p.cluster_topics)).toBe(true)
    expect(p.cluster_topics.length).toBeGreaterThanOrEqual(8)
  })

  test("each cluster topic has all required fields", () => {
    const p = loadPlan()
    const validTypes = new Set(["blog", "guide", "case_study", "comparison", "tutorial", "checklist"])
    const validStages = new Set(["awareness", "consideration", "decision"])
    const validPriorities = new Set(["high", "medium", "low"])
    for (const t of p.cluster_topics) {
      expect(t).toHaveProperty("title")
      expect(t).toHaveProperty("content_type")
      expect(t).toHaveProperty("target_keyword")
      expect(t).toHaveProperty("estimated_word_count")
      expect(t).toHaveProperty("funnel_stage")
      expect(t).toHaveProperty("priority")
      expect(validTypes.has(t.content_type)).toBe(true)
      expect(validStages.has(t.funnel_stage)).toBe(true)
      expect(validPriorities.has(t.priority)).toBe(true)
    }
  })

  test("all three funnel stages are represented", () => {
    const p = loadPlan()
    const stages = new Set(p.cluster_topics.map((t: any) => t.funnel_stage))
    expect(stages.has("awareness")).toBe(true)
    expect(stages.has("consideration")).toBe(true)
    expect(stages.has("decision")).toBe(true)
  })

  test("at least 2 topics have high priority", () => {
    const p = loadPlan()
    const highPriority = p.cluster_topics.filter((t: any) => t.priority === "high")
    expect(highPriority.length).toBeGreaterThanOrEqual(2)
  })

  test("estimated_word_count values are between 300 and 5000", () => {
    const p = loadPlan()
    for (const t of p.cluster_topics) {
      expect(t.estimated_word_count).toBeGreaterThanOrEqual(300)
      expect(t.estimated_word_count).toBeLessThanOrEqual(5000)
    }
  })

  test("content_calendar has at least 8 entries within weeks 1-12", () => {
    const p = loadPlan()
    expect(Array.isArray(p.content_calendar)).toBe(true)
    expect(p.content_calendar.length).toBeGreaterThanOrEqual(8)
    for (const entry of p.content_calendar) {
      expect(entry).toHaveProperty("week")
      expect(entry).toHaveProperty("topic_title")
      expect(entry).toHaveProperty("content_type")
      expect(entry.week).toBeGreaterThanOrEqual(1)
      expect(entry.week).toBeLessThanOrEqual(12)
    }
  })

  test("success_metrics has at least 3 entries", () => {
    const p = loadPlan()
    expect(Array.isArray(p.success_metrics)).toBe(true)
    expect(p.success_metrics.length).toBeGreaterThanOrEqual(3)
    for (const m of p.success_metrics) {
      expect(typeof m).toBe("string")
      expect(m.length).toBeGreaterThan(5)
    }
  })
})

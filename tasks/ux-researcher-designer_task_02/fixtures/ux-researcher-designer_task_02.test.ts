import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadPlan(): any {
  return JSON.parse(readFileSync("usability_plan.json", "utf-8"))
}

function loadSynthesis(): any {
  return JSON.parse(readFileSync("synthesis.json", "utf-8"))
}

describe("usability_plan.json", () => {
  test("file exists", () => {
    expect(existsSync("usability_plan.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const p = loadPlan()
    for (const f of ["research_questions", "method", "participant_count", "session_duration_minutes", "tasks", "success_metrics"]) {
      expect(p).toHaveProperty(f)
    }
  })

  test("method is moderated_remote", () => {
    const p = loadPlan()
    expect(p.method).toBe("moderated_remote")
  })

  test("participant_count between 5 and 8", () => {
    const p = loadPlan()
    expect(typeof p.participant_count).toBe("number")
    expect(p.participant_count).toBeGreaterThanOrEqual(5)
    expect(p.participant_count).toBeLessThanOrEqual(8)
  })

  test("session_duration between 45 and 60 minutes", () => {
    const p = loadPlan()
    expect(typeof p.session_duration_minutes).toBe("number")
    expect(p.session_duration_minutes).toBeGreaterThanOrEqual(45)
    expect(p.session_duration_minutes).toBeLessThanOrEqual(60)
  })

  test("has exactly 3 tasks", () => {
    const p = loadPlan()
    expect(Array.isArray(p.tasks)).toBe(true)
    expect(p.tasks.length).toBe(3)
  })

  test("each task has scenario, goal, success_criteria fields", () => {
    const p = loadPlan()
    for (const t of p.tasks) {
      expect(t).toHaveProperty("id")
      expect(t).toHaveProperty("scenario")
      expect(t).toHaveProperty("goal")
      expect(t).toHaveProperty("success_criteria")
      expect(typeof t.scenario).toBe("string")
      expect(t.scenario.length).toBeGreaterThan(10)
    }
  })

  test("research_questions has 3 strings", () => {
    const p = loadPlan()
    expect(Array.isArray(p.research_questions)).toBe(true)
    expect(p.research_questions.length).toBe(3)
    for (const q of p.research_questions) {
      expect(typeof q).toBe("string")
      expect(q.length).toBeGreaterThan(10)
    }
  })

  test("success_metrics has completion_rate_target, error_rate_max, satisfaction_min", () => {
    const p = loadPlan()
    const sm = p.success_metrics
    expect(sm).toHaveProperty("completion_rate_target")
    expect(sm).toHaveProperty("error_rate_max")
    expect(sm).toHaveProperty("satisfaction_min")
    expect(sm.completion_rate_target).toBeGreaterThan(0)
    expect(sm.completion_rate_target).toBeLessThanOrEqual(1)
  })
})

describe("synthesis.json", () => {
  test("file exists", () => {
    expect(existsSync("synthesis.json")).toBe(true)
  })

  test("has findings array and top_priority_theme", () => {
    const s = loadSynthesis()
    expect(s).toHaveProperty("findings")
    expect(s).toHaveProperty("top_priority_theme")
    expect(Array.isArray(s.findings)).toBe(true)
  })

  test("synthesis has 5 findings matching the 5 observation clusters", () => {
    const s = loadSynthesis()
    expect(s.findings.length).toBe(5)
  })

  test("each finding has theme, frequency, severity, recommendation", () => {
    const s = loadSynthesis()
    for (const f of s.findings) {
      expect(f).toHaveProperty("theme")
      expect(f).toHaveProperty("frequency")
      expect(f).toHaveProperty("severity")
      expect(f).toHaveProperty("recommendation")
      expect(typeof f.frequency).toBe("number")
      expect(f.severity).toBeGreaterThanOrEqual(1)
      expect(f.severity).toBeLessThanOrEqual(4)
    }
  })

  test("finding frequencies match source data: one finding per cluster with correct counts", () => {
    const s = loadSynthesis()
    const freqs = s.findings.map((f: any) => f.frequency).sort((a: number, b: number) => a - b)
    // Expected frequencies: 4, 4, 4, 4, 2 (from observation clusters)
    expect(freqs.filter((f: number) => f === 4).length).toBeGreaterThanOrEqual(3)
    expect(freqs.some((f: number) => f === 2)).toBe(true)
  })

  test("top_priority_theme is set and is a non-empty string", () => {
    const s = loadSynthesis()
    expect(typeof s.top_priority_theme).toBe("string")
    expect(s.top_priority_theme.length).toBeGreaterThan(0)
  })
})

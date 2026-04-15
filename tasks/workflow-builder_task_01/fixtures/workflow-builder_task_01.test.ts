import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadWorkflow(): any {
  return JSON.parse(readFileSync("onboarding_workflow.json", "utf-8"))
}

const VALID_AUTOMATION = new Set(["high", "medium", "low"])

describe("onboarding_workflow.json", () => {
  test("file exists", () => {
    expect(existsSync("onboarding_workflow.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const w = loadWorkflow()
    for (const f of ["name", "description", "trigger", "total_duration_days", "steps", "total_steps", "automation_summary"]) {
      expect(w).toHaveProperty(f)
    }
  })

  test("trigger is offer_accepted", () => {
    const w = loadWorkflow()
    expect(w.trigger).toBe("offer_accepted")
  })

  test("total_steps is 6", () => {
    const w = loadWorkflow()
    expect(w.total_steps).toBe(6)
  })

  test("steps array has exactly 6 steps", () => {
    const w = loadWorkflow()
    expect(Array.isArray(w.steps)).toBe(true)
    expect(w.steps.length).toBe(6)
  })

  test("step IDs are S1 through S6", () => {
    const w = loadWorkflow()
    const ids = w.steps.map((s: any) => s.id).sort()
    expect(ids).toContain("S1")
    expect(ids).toContain("S2")
    expect(ids).toContain("S3")
    expect(ids).toContain("S4")
    expect(ids).toContain("S5")
    expect(ids).toContain("S6")
  })

  test("each step has owner, inputs, outputs, and duration_hours fields", () => {
    const w = loadWorkflow()
    for (const s of w.steps) {
      expect(s).toHaveProperty("name")
      expect(s).toHaveProperty("owner")
      expect(s).toHaveProperty("duration_hours")
      expect(s).toHaveProperty("inputs")
      expect(s).toHaveProperty("outputs")
      expect(Array.isArray(s.inputs)).toBe(true)
      expect(Array.isArray(s.outputs)).toBe(true)
      expect(s.inputs.length).toBeGreaterThanOrEqual(1)
      expect(s.outputs.length).toBeGreaterThanOrEqual(1)
    }
  })

  test("duration_hours is a positive number for each step", () => {
    const w = loadWorkflow()
    for (const s of w.steps) {
      expect(typeof s.duration_hours).toBe("number")
      expect(s.duration_hours).toBeGreaterThan(0)
    }
  })

  test("automation_potential values are high, medium, or low for each step", () => {
    const w = loadWorkflow()
    for (const s of w.steps) {
      expect(s).toHaveProperty("automation_potential")
      expect(VALID_AUTOMATION.has(s.automation_potential)).toBe(true)
    }
  })

  test("automation_summary high+medium+low counts sum to 6", () => {
    const w = loadWorkflow()
    const sum = (w.automation_summary.high ?? 0) + (w.automation_summary.medium ?? 0) + (w.automation_summary.low ?? 0)
    expect(sum).toBe(6)
  })

  test("automation_summary counts match actual step distribution", () => {
    const w = loadWorkflow()
    const actual = { high: 0, medium: 0, low: 0 }
    for (const s of w.steps) {
      actual[s.automation_potential as "high"|"medium"|"low"]++
    }
    expect(w.automation_summary.high).toBe(actual.high)
    expect(w.automation_summary.medium).toBe(actual.medium)
    expect(w.automation_summary.low).toBe(actual.low)
  })
})

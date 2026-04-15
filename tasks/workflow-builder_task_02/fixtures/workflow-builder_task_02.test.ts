import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadWorkflow(): any {
  return JSON.parse(readFileSync("approval_workflow.json", "utf-8"))
}

function loadSummary(): string {
  return readFileSync("approval_summary.txt", "utf-8")
}

describe("approval_workflow.json", () => {
  test("file exists", () => {
    expect(existsSync("approval_workflow.json")).toBe(true)
  })

  test("has required fields: name, trigger, decision_points, approval_tiers, escalation_days, total_tiers", () => {
    const w = loadWorkflow()
    for (const f of ["name", "trigger", "decision_points", "approval_tiers", "escalation_days", "total_tiers"]) {
      expect(w).toHaveProperty(f)
    }
  })

  test("trigger is purchase_request_submitted", () => {
    const w = loadWorkflow()
    expect(w.trigger).toBe("purchase_request_submitted")
  })

  test("escalation_days is 5", () => {
    const w = loadWorkflow()
    expect(w.escalation_days).toBe(5)
  })

  test("approval_tiers has exactly 4 tiers", () => {
    const w = loadWorkflow()
    expect(Array.isArray(w.approval_tiers)).toBe(true)
    expect(w.approval_tiers.length).toBe(4)
    expect(w.total_tiers).toBe(4)
  })

  test("tier 1 is auto_approved with empty approvers array", () => {
    const w = loadWorkflow()
    const t1 = w.approval_tiers.find((t: any) => t.tier === 1)
    expect(t1).toBeDefined()
    expect(t1.auto_approved).toBe(true)
    expect(Array.isArray(t1.approvers)).toBe(true)
    expect(t1.approvers.length).toBe(0)
  })

  test("tier amount boundaries match business rules: 0-499, 500-4999, 5000-19999, 20000+", () => {
    const w = loadWorkflow()
    const sorted = [...w.approval_tiers].sort((a: any, b: any) => a.tier - b.tier)
    expect(sorted[0].min_amount).toBe(0)
    expect(sorted[0].max_amount).toBe(499)
    expect(sorted[1].min_amount).toBe(500)
    expect(sorted[1].max_amount).toBe(4999)
    expect(sorted[2].min_amount).toBe(5000)
    expect(sorted[2].max_amount).toBe(19999)
    expect(sorted[3].min_amount).toBe(20000)
  })

  test("tier 4 max_amount is null (no upper limit)", () => {
    const w = loadWorkflow()
    const t4 = w.approval_tiers.find((t: any) => t.tier === 4)
    expect(t4).toBeDefined()
    expect(t4.max_amount).toBeNull()
  })

  test("tiers 2, 3, 4 have auto_approved=false and non-empty approvers arrays", () => {
    const w = loadWorkflow()
    for (const tier of [2, 3, 4]) {
      const t = w.approval_tiers.find((t: any) => t.tier === tier)
      expect(t).toBeDefined()
      expect(t.auto_approved).toBe(false)
      expect(Array.isArray(t.approvers)).toBe(true)
      expect(t.approvers.length).toBeGreaterThanOrEqual(1)
    }
  })

  test("decision_points has at least 2 entries with id, condition, true_path, false_path", () => {
    const w = loadWorkflow()
    expect(Array.isArray(w.decision_points)).toBe(true)
    expect(w.decision_points.length).toBeGreaterThanOrEqual(2)
    for (const dp of w.decision_points) {
      expect(dp).toHaveProperty("id")
      expect(dp).toHaveProperty("condition")
      expect(dp).toHaveProperty("true_path")
      expect(dp).toHaveProperty("false_path")
    }
  })
})

describe("approval_summary.txt", () => {
  test("file exists", () => {
    expect(existsSync("approval_summary.txt")).toBe(true)
  })

  test("has exactly 4 non-empty lines (one per tier)", () => {
    const txt = loadSummary()
    const lines = txt.trim().split("\n").filter((l: string) => l.trim().length > 0)
    expect(lines.length).toBe(4)
  })

  test("each line contains Tier label and dollar amount", () => {
    const txt = loadSummary()
    const lines = txt.trim().split("\n").filter((l: string) => l.trim().length > 0)
    for (const line of lines) {
      expect(line.toLowerCase()).toMatch(/tier \d/)
      expect(line).toMatch(/\$\d+/)
    }
  })
})

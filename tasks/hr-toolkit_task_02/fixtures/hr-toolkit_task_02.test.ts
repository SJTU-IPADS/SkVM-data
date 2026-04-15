import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadOnboard(): any {
  return JSON.parse(readFileSync("onboarding_checklist.json", "utf-8"))
}

function loadOffboard(): any {
  return JSON.parse(readFileSync("offboarding_summary.json", "utf-8"))
}

const VALID_OWNERS = new Set(["HR", "Manager", "IT", "Finance"])
const VALID_DEADLINES = new Set(["last_day", "1_week_before", "day_after"])

describe("onboarding_checklist.json", () => {
  test("file exists", () => {
    expect(existsSync("onboarding_checklist.json")).toBe(true)
  })

  test("onboarding employee fields: name is Sarah Kim, title is Product Manager", () => {
    const d = loadOnboard()
    expect(d).toHaveProperty("employee")
    expect(d.employee.name).toBe("Sarah Kim")
    expect(d.employee.title).toBe("Product Manager")
    expect(d.employee.department).toBe("Product")
  })

  test("phases array has exactly 3 phases", () => {
    const d = loadOnboard()
    expect(Array.isArray(d.phases)).toBe(true)
    expect(d.phases.length).toBe(3)
  })

  test("phase names are Day 1, Week 1, Month 1", () => {
    const d = loadOnboard()
    const names = d.phases.map((p: any) => p.phase)
    expect(names).toContain("Day 1")
    expect(names).toContain("Week 1")
    expect(names).toContain("Month 1")
  })

  test("each phase has at least 4 tasks", () => {
    const d = loadOnboard()
    for (const phase of d.phases) {
      expect(Array.isArray(phase.tasks)).toBe(true)
      expect(phase.tasks.length).toBeGreaterThanOrEqual(4)
    }
  })

  test("each task has task, owner, required, and completed fields", () => {
    const d = loadOnboard()
    for (const phase of d.phases) {
      for (const t of phase.tasks) {
        expect(t).toHaveProperty("task")
        expect(t).toHaveProperty("owner")
        expect(t).toHaveProperty("required")
        expect(t).toHaveProperty("completed")
        expect(VALID_OWNERS.has(t.owner)).toBe(true)
        expect(typeof t.required).toBe("boolean")
        expect(typeof t.completed).toBe("boolean")
      }
    }
  })

  test("total_tasks and required_tasks are accurate integers", () => {
    const d = loadOnboard()
    expect(typeof d.total_tasks).toBe("number")
    expect(typeof d.required_tasks).toBe("number")
    // Verify total_tasks matches actual count
    const actualTotal = d.phases.reduce((sum: number, p: any) => sum + p.tasks.length, 0)
    expect(d.total_tasks).toBe(actualTotal)
    // Verify required_tasks matches actual count
    const actualRequired = d.phases.reduce((sum: number, p: any) =>
      sum + p.tasks.filter((t: any) => t.required === true).length, 0)
    expect(d.required_tasks).toBe(actualRequired)
  })
})

describe("offboarding_summary.json", () => {
  test("file exists", () => {
    expect(existsSync("offboarding_summary.json")).toBe(true)
  })

  test("offboarding employee fields: name is James Torres", () => {
    const d = loadOffboard()
    expect(d).toHaveProperty("employee")
    expect(d.employee.name).toBe("James Torres")
    expect(d.employee.department).toBe("Engineering")
    expect(d.employee.reason).toBe("voluntary_resignation")
  })

  test("checklist has at least 6 offboarding action items", () => {
    const d = loadOffboard()
    expect(Array.isArray(d.checklist)).toBe(true)
    expect(d.checklist.length).toBeGreaterThanOrEqual(6)
  })

  test("each checklist item has action, owner, deadline, completed with valid values", () => {
    const d = loadOffboard()
    for (const item of d.checklist) {
      expect(item).toHaveProperty("action")
      expect(item).toHaveProperty("owner")
      expect(item).toHaveProperty("deadline")
      expect(item).toHaveProperty("completed")
      expect(VALID_OWNERS.has(item.owner)).toBe(true)
      expect(VALID_DEADLINES.has(item.deadline)).toBe(true)
      expect(typeof item.completed).toBe("boolean")
    }
  })

  test("knowledge_transfer has topics array with at least 3 items and estimated_hours", () => {
    const d = loadOffboard()
    expect(d).toHaveProperty("knowledge_transfer")
    expect(Array.isArray(d.knowledge_transfer.topics)).toBe(true)
    expect(d.knowledge_transfer.topics.length).toBeGreaterThanOrEqual(3)
    expect(typeof d.knowledge_transfer.estimated_hours).toBe("number")
    expect(d.knowledge_transfer.estimated_hours).toBeGreaterThan(0)
    expect(d.knowledge_transfer).toHaveProperty("assigned_to")
  })

  test("exit_interview has scheduled, date, and format fields with valid values", () => {
    const d = loadOffboard()
    expect(d).toHaveProperty("exit_interview")
    expect(typeof d.exit_interview.scheduled).toBe("boolean")
    expect(d.exit_interview).toHaveProperty("date")
    expect(["in_person", "video", "survey"]).toContain(d.exit_interview.format)
  })
})

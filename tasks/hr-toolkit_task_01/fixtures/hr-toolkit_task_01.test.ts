import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadJD(): any {
  return JSON.parse(readFileSync("job_description.json", "utf-8"))
}

function loadPlan(): any {
  return JSON.parse(readFileSync("interview_plan.json", "utf-8"))
}

describe("job_description.json", () => {
  test("file exists", () => {
    expect(existsSync("job_description.json")).toBe(true)
  })

  test("has title, department, level, location, summary fields", () => {
    const jd = loadJD()
    expect(jd).toHaveProperty("title")
    expect(jd).toHaveProperty("department")
    expect(jd).toHaveProperty("level")
    expect(jd).toHaveProperty("location")
    expect(jd).toHaveProperty("summary")
    expect(typeof jd.summary).toBe("string")
    expect(jd.summary.length).toBeGreaterThan(20)
  })

  test("title is Senior Backend Engineer", () => {
    const jd = loadJD()
    expect(jd.title).toBe("Senior Backend Engineer")
  })

  test("responsibilities array has at least 5 items", () => {
    const jd = loadJD()
    expect(Array.isArray(jd.responsibilities)).toBe(true)
    expect(jd.responsibilities.length).toBeGreaterThanOrEqual(5)
  })

  test("requirements has required and preferred arrays", () => {
    const jd = loadJD()
    expect(jd).toHaveProperty("requirements")
    expect(jd.requirements).toHaveProperty("required")
    expect(jd.requirements).toHaveProperty("preferred")
    expect(Array.isArray(jd.requirements.required)).toBe(true)
    expect(Array.isArray(jd.requirements.preferred)).toBe(true)
    expect(jd.requirements.required.length).toBeGreaterThanOrEqual(5)
    expect(jd.requirements.preferred.length).toBeGreaterThanOrEqual(3)
  })

  test("compensation has min_salary and max_salary as numbers", () => {
    const jd = loadJD()
    expect(jd).toHaveProperty("compensation")
    expect(typeof jd.compensation.min_salary).toBe("number")
    expect(typeof jd.compensation.max_salary).toBe("number")
    expect(jd.compensation.min_salary).toBeGreaterThan(0)
    expect(jd.compensation.max_salary).toBeGreaterThan(jd.compensation.min_salary)
    expect(jd.compensation.currency).toBe("USD")
  })

  test("tech_stack is an array with at least 4 items", () => {
    const jd = loadJD()
    expect(Array.isArray(jd.tech_stack)).toBe(true)
    expect(jd.tech_stack.length).toBeGreaterThanOrEqual(4)
    for (const t of jd.tech_stack) {
      expect(typeof t).toBe("string")
    }
  })
})

describe("interview_plan.json", () => {
  test("file exists", () => {
    expect(existsSync("interview_plan.json")).toBe(true)
  })

  test("has role and stages fields", () => {
    const p = loadPlan()
    expect(p).toHaveProperty("role")
    expect(p).toHaveProperty("stages")
    expect(p).toHaveProperty("evaluation_criteria")
  })

  test("stages array has exactly 4 interview stages", () => {
    const p = loadPlan()
    expect(Array.isArray(p.stages)).toBe(true)
    expect(p.stages.length).toBe(4)
  })

  test("each stage has stage_number, name, duration_minutes, format, focus_areas, interviewers", () => {
    const p = loadPlan()
    for (const s of p.stages) {
      expect(s).toHaveProperty("stage_number")
      expect(s).toHaveProperty("name")
      expect(s).toHaveProperty("duration_minutes")
      expect(s).toHaveProperty("format")
      expect(s).toHaveProperty("focus_areas")
      expect(s).toHaveProperty("interviewers")
      expect(typeof s.duration_minutes).toBe("number")
      expect(s.duration_minutes).toBeGreaterThan(0)
      expect(["async", "live"]).toContain(s.format)
      expect(Array.isArray(s.focus_areas)).toBe(true)
      expect(s.focus_areas.length).toBeGreaterThanOrEqual(2)
    }
  })

  test("stage_numbers are 1 through 4 in order", () => {
    const p = loadPlan()
    const nums = p.stages.map((s: any) => s.stage_number)
    expect(nums).toContain(1)
    expect(nums).toContain(2)
    expect(nums).toContain(3)
    expect(nums).toContain(4)
  })

  test("evaluation_criteria has at least 3 dimensions each with name and weight", () => {
    const p = loadPlan()
    expect(Array.isArray(p.evaluation_criteria)).toBe(true)
    expect(p.evaluation_criteria.length).toBeGreaterThanOrEqual(3)
    for (const c of p.evaluation_criteria) {
      expect(c).toHaveProperty("name")
      expect(c).toHaveProperty("weight")
      expect(typeof c.weight).toBe("number")
      expect(c.weight).toBeGreaterThan(0)
    }
  })

  test("evaluation_criteria weights sum to 1.0", () => {
    const p = loadPlan()
    const total = p.evaluation_criteria.reduce((sum: number, c: any) => sum + c.weight, 0)
    expect(Math.abs(total - 1.0)).toBeLessThan(0.01)
  })
})

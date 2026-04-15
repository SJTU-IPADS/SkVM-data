import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"
import { join } from "path"

function loadReport(): any {
  return JSON.parse(readFileSync("inspection_report.json", "utf-8"))
}

function loadPlan(): string {
  return readFileSync("harness_plan.md", "utf-8")
}

describe("sample_project structure", () => {
  test("sample_project directory exists", () => {
    expect(existsSync("sample_project")).toBe(true)
  })

  test("README.md exists in sample_project", () => {
    expect(existsSync(join("sample_project", "README.md"))).toBe(true)
  })

  test("setup.py exists in sample_project", () => {
    expect(existsSync(join("sample_project", "setup.py"))).toBe(true)
  })

  test("setup.py contains name and version", () => {
    const content = readFileSync(join("sample_project", "setup.py"), "utf-8")
    expect(content).toContain("sample-tool")
    expect(content).toContain("0.1.0")
  })

  test("src/main.py exists", () => {
    expect(existsSync(join("sample_project", "src", "main.py"))).toBe(true)
  })

  test("tests directory exists with test file", () => {
    expect(existsSync(join("sample_project", "tests", "test_main.py"))).toBe(true)
  })
})

describe("inspection_report.json", () => {
  test("file exists", () => {
    expect(existsSync("inspection_report.json")).toBe(true)
  })

  test("all boolean fields are true", () => {
    const r = loadReport()
    expect(r.repo_exists).toBe(true)
    expect(r.has_readme).toBe(true)
    expect(r.has_setup_py).toBe(true)
    expect(r.has_tests).toBe(true)
  })

  test("source_files is an array with at least 3 entries", () => {
    const r = loadReport()
    expect(Array.isArray(r.source_files)).toBe(true)
    expect(r.source_files.length).toBeGreaterThanOrEqual(3)
    for (const f of r.source_files) {
      expect(typeof f).toBe("string")
      expect(f).toMatch(/\.py$/)
    }
  })

  test("harness_feasibility is a valid value", () => {
    const r = loadReport()
    expect(["high", "medium", "low"]).toContain(r.harness_feasibility)
  })

  test("recommended_entry_point is a non-empty string", () => {
    const r = loadReport()
    expect(typeof r.recommended_entry_point).toBe("string")
    expect(r.recommended_entry_point.length).toBeGreaterThan(0)
    expect(r.recommended_entry_point).toMatch(/python3|python/)
  })

  test("assessment_notes is between 20 and 100 words", () => {
    const r = loadReport()
    expect(typeof r.assessment_notes).toBe("string")
    const wordCount = r.assessment_notes.trim().split(/\s+/).length
    expect(wordCount).toBeGreaterThanOrEqual(20)
    expect(wordCount).toBeLessThanOrEqual(100)
  })
})

describe("harness_plan.md", () => {
  test("file exists", () => {
    expect(existsSync("harness_plan.md")).toBe(true)
  })

  test("plan is at least 100 words", () => {
    const text = loadPlan()
    const wordCount = text.trim().split(/\s+/).length
    expect(wordCount).toBeGreaterThanOrEqual(100)
  })

  test("plan mentions command groups or commands", () => {
    const text = loadPlan().toLowerCase()
    expect(text).toMatch(/command|group|cli|harness/)
  })
})

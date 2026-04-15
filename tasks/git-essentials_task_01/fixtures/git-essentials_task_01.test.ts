import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"
import { join } from "path"

const REPO = "demo-project"
const REPORT = join(REPO, "repo_report.json")

function loadReport(): any {
  return JSON.parse(readFileSync(REPORT, "utf-8"))
}

describe("demo-project", () => {
  test("demo-project directory exists", () => {
    expect(existsSync(REPO)).toBe(true)
  })

  test("is a git repository", () => {
    expect(existsSync(join(REPO, ".git"))).toBe(true)
  })
})

describe("repo_report.json", () => {
  test("repo_report.json exists", () => {
    expect(existsSync(REPORT)).toBe(true)
  })

  test("is valid JSON with required fields", () => {
    const r = loadReport()
    expect(r).toHaveProperty("branches")
    expect(r).toHaveProperty("current_branch")
    expect(r).toHaveProperty("commit_count")
    expect(r).toHaveProperty("has_feature_branch")
    expect(r).toHaveProperty("latest_commit_message")
    expect(r).toHaveProperty("files_on_main")
    expect(r).toHaveProperty("files_on_feature")
  })

  test("branches contains main and feature/add-config", () => {
    const r = loadReport()
    expect(Array.isArray(r.branches)).toBe(true)
    const names = r.branches.map((b: string) => b.trim())
    expect(names).toContain("main")
    expect(names).toContain("feature/add-config")
  })

  test("current_branch is main", () => {
    const r = loadReport()
    expect(r.current_branch.trim()).toBe("main")
  })

  test("commit_count is at least 2", () => {
    const r = loadReport()
    expect(typeof r.commit_count).toBe("number")
    expect(r.commit_count).toBeGreaterThanOrEqual(2)
  })

  test("has_feature_branch is true", () => {
    const r = loadReport()
    expect(r.has_feature_branch).toBe(true)
  })

  test("files_on_main contains README.md", () => {
    const r = loadReport()
    expect(Array.isArray(r.files_on_main)).toBe(true)
    expect(r.files_on_main).toContain("README.md")
  })

  test("files_on_feature contains config.json", () => {
    const r = loadReport()
    expect(Array.isArray(r.files_on_feature)).toBe(true)
    expect(r.files_on_feature).toContain("config.json")
  })
})

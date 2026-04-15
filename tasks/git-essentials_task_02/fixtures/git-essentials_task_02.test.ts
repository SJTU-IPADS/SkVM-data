import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"
import { join } from "path"

const REPO = "changelog-project"
const CHANGELOG = join(REPO, "changelog.json")

function loadChangelog(): any {
  return JSON.parse(readFileSync(CHANGELOG, "utf-8"))
}

describe("changelog-project", () => {
  test("changelog-project directory exists", () => {
    expect(existsSync(REPO)).toBe(true)
  })

  test("is a git repository", () => {
    expect(existsSync(join(REPO, ".git"))).toBe(true)
  })
})

describe("changelog.json", () => {
  test("changelog.json exists", () => {
    expect(existsSync(CHANGELOG)).toBe(true)
  })

  test("is valid JSON with required fields", () => {
    const c = loadChangelog()
    expect(c).toHaveProperty("total_commits")
    expect(c).toHaveProperty("features")
    expect(c).toHaveProperty("fixes")
    expect(c).toHaveProperty("other")
    expect(c).toHaveProperty("files_changed")
    expect(c).toHaveProperty("first_commit_date")
    expect(c).toHaveProperty("last_commit_date")
  })

  test("total_commits is at least 8", () => {
    const c = loadChangelog()
    expect(typeof c.total_commits).toBe("number")
    expect(c.total_commits).toBeGreaterThanOrEqual(8)
  })

  test("features array is non-empty and entries start with feat:", () => {
    const c = loadChangelog()
    expect(Array.isArray(c.features)).toBe(true)
    expect(c.features.length).toBeGreaterThanOrEqual(1)
    for (const msg of c.features) {
      expect(msg).toMatch(/^feat:/)
    }
  })

  test("fixes array is non-empty and entries start with fix:", () => {
    const c = loadChangelog()
    expect(Array.isArray(c.fixes)).toBe(true)
    expect(c.fixes.length).toBeGreaterThanOrEqual(1)
    for (const msg of c.fixes) {
      expect(msg).toMatch(/^fix:/)
    }
  })

  test("categories sum to total_commits", () => {
    const c = loadChangelog()
    const sum = c.features.length + c.fixes.length + c.other.length
    expect(sum).toBe(c.total_commits)
  })

  test("files_changed is non-empty array", () => {
    const c = loadChangelog()
    expect(Array.isArray(c.files_changed)).toBe(true)
    expect(c.files_changed.length).toBeGreaterThanOrEqual(1)
  })

  test("first_commit_date is a valid ISO date string", () => {
    const c = loadChangelog()
    expect(typeof c.first_commit_date).toBe("string")
    const d = new Date(c.first_commit_date)
    expect(d.getTime()).not.toBeNaN()
  })

  test("last_commit_date is a valid ISO date string", () => {
    const c = loadChangelog()
    expect(typeof c.last_commit_date).toBe("string")
    const d = new Date(c.last_commit_date)
    expect(d.getTime()).not.toBeNaN()
  })
})

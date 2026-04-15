import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadBug(): any {
  return JSON.parse(readFileSync("bug_report.json", "utf-8"))
}

function loadFeature(): any {
  return JSON.parse(readFileSync("feature_request.json", "utf-8"))
}

describe("bug_report.json", () => {
  test("file exists", () => {
    expect(existsSync("bug_report.json")).toBe(true)
  })

  test("has required top-level fields type, title, labels, body", () => {
    const b = loadBug()
    expect(b).toHaveProperty("type")
    expect(b).toHaveProperty("title")
    expect(b).toHaveProperty("labels")
    expect(b).toHaveProperty("body")
  })

  test("type is bug and labels contains bug", () => {
    const b = loadBug()
    expect(b.type).toBe("bug")
    expect(Array.isArray(b.labels)).toBe(true)
    expect(b.labels).toContain("bug")
  })

  test("title starts with Bug: and references MemoryError or 10MB or PNG", () => {
    const b = loadBug()
    expect(b.title).toMatch(/^Bug:/i)
    const titleLower = b.title.toLowerCase()
    expect(
      titleLower.includes("memoryerror") ||
      titleLower.includes("10mb") ||
      titleLower.includes("png") ||
      titleLower.includes("memory")
    ).toBe(true)
  })

  test("body has description, steps_to_reproduce, expected, actual", () => {
    const b = loadBug()
    expect(b.body).toHaveProperty("description")
    expect(b.body).toHaveProperty("steps_to_reproduce")
    expect(b.body).toHaveProperty("expected")
    expect(b.body).toHaveProperty("actual")
  })

  test("steps_to_reproduce is an array of at least 2 steps", () => {
    const b = loadBug()
    expect(Array.isArray(b.body.steps_to_reproduce)).toBe(true)
    expect(b.body.steps_to_reproduce.length).toBeGreaterThanOrEqual(2)
  })

  test("actual field contains the exact error text MemoryError", () => {
    const b = loadBug()
    expect(b.body.actual).toContain("MemoryError")
  })

  test("affected_flag is --quality=100 and file_size_threshold is 10MB", () => {
    const b = loadBug()
    expect(b.body.affected_flag).toBe("--quality=100")
    expect(b.body.file_size_threshold).toBe("10MB")
  })
})

describe("feature_request.json", () => {
  test("file exists", () => {
    expect(existsSync("feature_request.json")).toBe(true)
  })

  test("has required top-level fields type, title, labels, body", () => {
    const f = loadFeature()
    expect(f).toHaveProperty("type")
    expect(f).toHaveProperty("title")
    expect(f).toHaveProperty("labels")
    expect(f).toHaveProperty("body")
  })

  test("type is feature and labels contains enhancement", () => {
    const f = loadFeature()
    expect(f.type).toBe("feature")
    expect(Array.isArray(f.labels)).toBe(true)
    expect(f.labels).toContain("enhancement")
  })

  test("body has summary, acceptance_criteria, and flag_name", () => {
    const f = loadFeature()
    expect(f.body).toHaveProperty("summary")
    expect(f.body).toHaveProperty("acceptance_criteria")
    expect(f.body).toHaveProperty("flag_name")
  })

  test("flag_name is --dry-run", () => {
    const f = loadFeature()
    expect(f.body.flag_name).toBe("--dry-run")
  })

  test("acceptance_criteria is an array of at least 3 items", () => {
    const f = loadFeature()
    expect(Array.isArray(f.body.acceptance_criteria)).toBe(true)
    expect(f.body.acceptance_criteria.length).toBeGreaterThanOrEqual(3)
  })
})

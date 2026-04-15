import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadEntries(): string {
  return readFileSync("logdata/entries.log", "utf-8")
}

function loadOutput(): string {
  return readFileSync("run_output.txt", "utf-8")
}

describe("logger.sh", () => {
  test("file exists", () => {
    expect(existsSync("logger.sh")).toBe(true)
  })
})

describe("logdata directory", () => {
  test("logdata directory exists", () => {
    expect(existsSync("logdata")).toBe(true)
  })

  test("entries.log exists", () => {
    expect(existsSync("logdata/entries.log")).toBe(true)
  })

  test("entries.log has exactly 2 entries", () => {
    const lines = loadEntries().trim().split("\n").filter(l => l.trim() !== "")
    expect(lines.length).toBe(2)
  })

  test("entries are date-prefixed with YYYY-MM-DD format", () => {
    const lines = loadEntries().trim().split("\n").filter(l => l.trim() !== "")
    const datePattern = /^\d{4}-\d{2}-\d{2} /
    for (const line of lines) {
      expect(datePattern.test(line)).toBe(true)
    }
  })

  test("first entry contains 'test suite passed: 12 checks'", () => {
    const content = loadEntries()
    expect(content).toContain("test suite passed: 12 checks")
  })

  test("second entry contains 'deployment verified on staging'", () => {
    const content = loadEntries()
    expect(content).toContain("deployment verified on staging")
  })
})

describe("run_output.txt", () => {
  test("file exists", () => {
    expect(existsSync("run_output.txt")).toBe(true)
  })

  test("contains 'Initialized in logdata'", () => {
    const out = loadOutput()
    expect(out).toContain("Initialized in logdata")
  })

  test("contains 'Added: test suite passed: 12 checks'", () => {
    const out = loadOutput()
    expect(out).toContain("Added: test suite passed: 12 checks")
  })

  test("contains 'Added: deployment verified on staging'", () => {
    const out = loadOutput()
    expect(out).toContain("Added: deployment verified on staging")
  })

  test("search hit: output contains 'staging' entry line", () => {
    const out = loadOutput()
    expect(out.toLowerCase()).toContain("staging")
  })

  test("search miss: output contains 'Not found: missing'", () => {
    const out = loadOutput()
    expect(out).toContain("Not found: missing")
  })
})

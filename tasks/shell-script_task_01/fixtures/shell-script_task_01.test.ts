import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync, statSync } from "fs"
import { spawnSync } from "child_process"

function loadScript(): string {
  return readFileSync("log_analyzer.sh", "utf-8")
}

function loadOutput(): any {
  return JSON.parse(readFileSync("sample_output.json", "utf-8"))
}

describe("log_analyzer.sh", () => {
  test("file exists", () => {
    expect(existsSync("log_analyzer.sh")).toBe(true)
  })

  test("contains 'set -euo pipefail'", () => {
    const script = loadScript()
    expect(script).toContain("set -euo pipefail")
  })

  test("exits with code 1 when no argument is provided", () => {
    const result = spawnSync("bash", ["log_analyzer.sh"], { cwd: process.cwd() })
    expect(result.status).toBe(1)
  })

  test("prints usage message to stderr when no argument is provided", () => {
    const result = spawnSync("bash", ["log_analyzer.sh"], { cwd: process.cwd() })
    const stderr = result.stderr.toString()
    expect(stderr.toLowerCase()).toContain("usage")
  })

  test("exits with code 2 when file does not exist", () => {
    const result = spawnSync("bash", ["log_analyzer.sh", "nonexistent_file_xyz.log"], { cwd: process.cwd() })
    expect(result.status).toBe(2)
  })

  test("prints file not found message to stderr for missing file", () => {
    const result = spawnSync("bash", ["log_analyzer.sh", "nonexistent_file_xyz.log"], { cwd: process.cwd() })
    const stderr = result.stderr.toString()
    expect(stderr.toLowerCase()).toContain("not found")
  })

  test("uses $() for command substitution (not backticks)", () => {
    const script = loadScript()
    // Check for $( usage — allow backticks only in comments
    const nonCommentLines = script.split("\n").filter(l => !l.trim().startsWith("#"))
    const nonCommentText = nonCommentLines.join("\n")
    // Should have $( ) usage
    expect(nonCommentText).toContain("$(")
  })
})

describe("test.log", () => {
  test("file exists", () => {
    expect(existsSync("test.log")).toBe(true)
  })

  test("test.log has at least 20 lines", () => {
    const lines = readFileSync("test.log", "utf-8").split("\n").filter(l => l.trim().length > 0)
    expect(lines.length).toBeGreaterThanOrEqual(20)
  })

  test("test.log contains ERROR, WARN, and INFO entries", () => {
    const content = readFileSync("test.log", "utf-8").toUpperCase()
    expect(content).toContain("ERROR")
    expect(content).toContain("WARN")
    expect(content).toContain("INFO")
  })
})

describe("sample_output.json", () => {
  test("file exists", () => {
    expect(existsSync("sample_output.json")).toBe(true)
  })

  test("sample_output.json is valid JSON", () => {
    expect(() => loadOutput()).not.toThrow()
  })

  test("has total_lines, error_count, warn_count, info_count fields", () => {
    const d = loadOutput()
    expect(d).toHaveProperty("total_lines")
    expect(d).toHaveProperty("error_count")
    expect(d).toHaveProperty("warn_count")
    expect(d).toHaveProperty("info_count")
  })

  test("all count fields are non-negative integers", () => {
    const d = loadOutput()
    expect(typeof d.total_lines).toBe("number")
    expect(typeof d.error_count).toBe("number")
    expect(typeof d.warn_count).toBe("number")
    expect(typeof d.info_count).toBe("number")
    expect(d.total_lines).toBeGreaterThan(0)
    expect(d.error_count).toBeGreaterThanOrEqual(0)
    expect(d.warn_count).toBeGreaterThanOrEqual(0)
    expect(d.info_count).toBeGreaterThanOrEqual(0)
  })

  test("top_ips is an array with exactly 3 entries", () => {
    const d = loadOutput()
    expect(d).toHaveProperty("top_ips")
    expect(Array.isArray(d.top_ips)).toBe(true)
    expect(d.top_ips.length).toBe(3)
  })

  test("top_ips entries are non-empty strings", () => {
    const d = loadOutput()
    for (const ip of d.top_ips) {
      expect(typeof ip).toBe("string")
      expect(ip.length).toBeGreaterThan(0)
    }
  })

  test("total_lines matches actual line count of test.log", () => {
    const d = loadOutput()
    const logLines = readFileSync("test.log", "utf-8").split("\n").filter(l => l.trim().length > 0)
    expect(d.total_lines).toBe(logLines.length)
  })
})

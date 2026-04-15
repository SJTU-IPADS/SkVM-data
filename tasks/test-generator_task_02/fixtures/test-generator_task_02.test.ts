import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadConfig(): any {
  return JSON.parse(readFileSync("toolcli_data/config.json", "utf-8"))
}

function loadReport(): string {
  return readFileSync("cli_report.txt", "utf-8")
}

describe("toolcli.sh", () => {
  test("file exists", () => {
    expect(existsSync("toolcli.sh")).toBe(true)
  })
})

describe("toolcli_data/config.json", () => {
  test("config.json exists", () => {
    expect(existsSync("toolcli_data/config.json")).toBe(true)
  })

  test("config.json is valid JSON", () => {
    expect(() => loadConfig()).not.toThrow()
  })

  test("config.json is an object", () => {
    const cfg = loadConfig()
    expect(typeof cfg).toBe("object")
    expect(cfg).not.toBeNull()
  })
})

describe("cli_report.txt", () => {
  test("file exists", () => {
    expect(existsSync("cli_report.txt")).toBe(true)
  })

  test("contains 'Initialized in' line from init command", () => {
    const out = loadReport()
    expect(out).toContain("Initialized in")
  })

  test("contains 'Status: ready' from status command", () => {
    const out = loadReport()
    expect(out).toContain("Status: ready")
  })

  test("contains 'Config:' and 'config.json' from config command", () => {
    const out = loadReport()
    expect(out).toContain("Config:")
    expect(out).toContain("config.json")
  })

  test("contains 'toolcli v1.0.0' from version command", () => {
    const out = loadReport()
    expect(out).toContain("toolcli v1.0.0")
  })

  test("contains 'Version: 1.0.0 | Data:' from info command", () => {
    const out = loadReport()
    expect(out).toContain("Version: 1.0.0 | Data:")
  })

  test("report has at least 5 non-empty lines", () => {
    const lines = loadReport().split("\n").filter(l => l.trim() !== "")
    expect(lines.length).toBeGreaterThanOrEqual(5)
  })
})

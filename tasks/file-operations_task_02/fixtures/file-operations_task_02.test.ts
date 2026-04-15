import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function readFile(path: string): string {
  return readFileSync(path, "utf-8")
}

function loadChangelog(): any {
  return JSON.parse(readFileSync("change_log.json", "utf-8"))
}

describe("config files exist", () => {
  test("config/database.yml exists", () => {
    expect(existsSync("config/database.yml")).toBe(true)
  })

  test("config/app.conf exists", () => {
    expect(existsSync("config/app.conf")).toBe(true)
  })

  test("config/worker.conf exists", () => {
    expect(existsSync("config/worker.conf")).toBe(true)
  })
})

describe("localhost replaced with prod-db.example.com", () => {
  test("database.yml has no remaining 'localhost'", () => {
    const content = readFile("config/database.yml")
    expect(content).not.toContain("localhost")
    expect(content).toContain("prod-db.example.com")
  })

  test("app.conf has no remaining 'localhost'", () => {
    const content = readFile("config/app.conf")
    expect(content).not.toContain("localhost")
    expect(content).toContain("prod-db.example.com")
  })

  test("worker.conf has no remaining 'localhost'", () => {
    const content = readFile("config/worker.conf")
    expect(content).not.toContain("localhost")
    expect(content).toContain("prod-db.example.com")
  })
})

describe("DEBUG replaced with WARNING", () => {
  test("app.conf log_level is WARNING not DEBUG", () => {
    const content = readFile("config/app.conf")
    expect(content).toContain("WARNING")
    expect(content).not.toContain("DEBUG")
  })

  test("worker.conf log_level is WARNING not DEBUG", () => {
    const content = readFile("config/worker.conf")
    expect(content).toContain("WARNING")
    expect(content).not.toContain("DEBUG")
  })
})

describe("dev_db replaced with production_db", () => {
  test("database.yml has production_db not dev_db", () => {
    const content = readFile("config/database.yml")
    expect(content).toContain("production_db")
    expect(content).not.toContain("dev_db")
  })
})

describe("development replaced with production (env setting)", () => {
  test("app.conf env is production not development", () => {
    const content = readFile("config/app.conf")
    expect(content).toContain("env=production")
    expect(content).not.toContain("env=development")
  })
})

describe("change_log.json", () => {
  test("change_log.json exists", () => {
    expect(existsSync("change_log.json")).toBe(true)
  })

  test("parses as valid JSON", () => {
    expect(() => loadChangelog()).not.toThrow()
  })

  test("has replacements_applied array and files_modified array", () => {
    const log = loadChangelog()
    expect(Array.isArray(log.replacements_applied)).toBe(true)
    expect(Array.isArray(log.files_modified)).toBe(true)
  })

  test("replacements_applied has 4 entries", () => {
    const log = loadChangelog()
    expect(log.replacements_applied.length).toBe(4)
  })

  test("localhost replacement has occurrences of 3", () => {
    const log = loadChangelog()
    const entry = log.replacements_applied.find((r: any) => r.from === "localhost")
    expect(entry).toBeDefined()
    expect(entry.occurrences).toBe(3)
  })

  test("DEBUG replacement has occurrences of 2", () => {
    const log = loadChangelog()
    const entry = log.replacements_applied.find((r: any) => r.from === "DEBUG")
    expect(entry).toBeDefined()
    expect(entry.occurrences).toBe(2)
  })

  test("files_modified is sorted alphabetically and has 3 entries", () => {
    const log = loadChangelog()
    const files: string[] = log.files_modified
    expect(files.length).toBe(3)
    const sorted = [...files].sort()
    expect(files).toEqual(sorted)
  })
})

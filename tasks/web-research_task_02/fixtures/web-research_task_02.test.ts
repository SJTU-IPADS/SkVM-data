import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadComparison(): any {
  return JSON.parse(readFileSync("language_comparison.json", "utf-8"))
}

function loadTable(): string {
  return readFileSync("comparison_table.md", "utf-8")
}

const VALID_TYPING = new Set(["static", "dynamic"])
const VALID_MEMORY = new Set(["manual", "gc", "ownership"])

describe("language_comparison.json", () => {
  test("file exists", () => {
    expect(existsSync("language_comparison.json")).toBe(true)
  })

  test("has languages array, oldest_language, data_source fields", () => {
    const c = loadComparison()
    expect(c).toHaveProperty("languages")
    expect(c).toHaveProperty("oldest_language")
    expect(c).toHaveProperty("data_source")
    expect(Array.isArray(c.languages)).toBe(true)
  })

  test("contains exactly 3 languages", () => {
    const c = loadComparison()
    expect(c.languages.length).toBe(3)
  })

  test("language names are Python, Rust, Go", () => {
    const c = loadComparison()
    const names = c.languages.map((l: any) => l.name)
    expect(names).toContain("Python")
    expect(names).toContain("Rust")
    expect(names).toContain("Go")
  })

  test("each language has required fields: creator, year_created, primary_use_case, typing, memory_management, notable_feature", () => {
    const c = loadComparison()
    for (const lang of c.languages) {
      expect(lang).toHaveProperty("creator")
      expect(lang).toHaveProperty("year_created")
      expect(lang).toHaveProperty("primary_use_case")
      expect(lang).toHaveProperty("typing")
      expect(lang).toHaveProperty("memory_management")
      expect(lang).toHaveProperty("notable_feature")
    }
  })

  test("typing values are valid: static or dynamic", () => {
    const c = loadComparison()
    for (const lang of c.languages) {
      expect(VALID_TYPING.has(lang.typing)).toBe(true)
    }
  })

  test("memory_management values are valid: manual, gc, or ownership", () => {
    const c = loadComparison()
    for (const lang of c.languages) {
      expect(VALID_MEMORY.has(lang.memory_management)).toBe(true)
    }
  })

  test("Python year_created is 1991", () => {
    const c = loadComparison()
    const python = c.languages.find((l: any) => l.name === "Python")
    expect(python).toBeDefined()
    expect(python.year_created).toBe(1991)
  })

  test("Rust memory_management is ownership", () => {
    const c = loadComparison()
    const rust = c.languages.find((l: any) => l.name === "Rust")
    expect(rust).toBeDefined()
    expect(rust.memory_management).toBe("ownership")
  })

  test("oldest_language is Python (1991 < 2009 < 2010)", () => {
    const c = loadComparison()
    expect(c.oldest_language).toBe("Python")
  })
})

describe("comparison_table.md", () => {
  test("file exists", () => {
    expect(existsSync("comparison_table.md")).toBe(true)
  })

  test("markdown table has header row with required columns", () => {
    const t = loadTable()
    const lines = t.split("\n").filter((l: string) => l.includes("|"))
    expect(lines.length).toBeGreaterThanOrEqual(4) // header + separator + 3 data rows
    const header = lines[0].toLowerCase()
    expect(header).toContain("language")
    expect(header).toContain("creator")
    expect(header).toContain("year")
  })

  test("table has separator row after header", () => {
    const t = loadTable()
    const lines = t.split("\n").filter((l: string) => l.includes("|"))
    // Separator row contains dashes
    expect(lines[1]).toMatch(/[-|]+/)
  })

  test("table contains Python, Rust, Go rows", () => {
    const t = loadTable()
    expect(t).toContain("Python")
    expect(t).toContain("Rust")
    expect(t).toContain("Go")
  })
})

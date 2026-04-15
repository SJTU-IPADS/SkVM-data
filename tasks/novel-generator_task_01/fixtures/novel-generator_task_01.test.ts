import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadOutline(): any {
  return JSON.parse(readFileSync("output/outline.json", "utf-8"))
}

function loadChapter(): string {
  return readFileSync("output/chapter_01.md", "utf-8")
}

describe("outline.json", () => {
  test("file exists", () => {
    expect(existsSync("output/outline.json")).toBe(true)
  })

  test("outline has required top-level fields", () => {
    const o = loadOutline()
    expect(o).toHaveProperty("title")
    expect(o).toHaveProperty("genre")
    expect(o).toHaveProperty("protagonist")
    expect(o).toHaveProperty("power_system")
    expect(o).toHaveProperty("volume_1")
  })

  test("protagonist has name Wei Liang", () => {
    const o = loadOutline()
    expect(o.protagonist.name).toBe("Wei Liang")
  })

  test("power_system has 5 levels", () => {
    const o = loadOutline()
    expect(Array.isArray(o.power_system.levels)).toBe(true)
    expect(o.power_system.levels.length).toBe(5)
    for (const level of o.power_system.levels) {
      expect(typeof level).toBe("string")
      expect(level.length).toBeGreaterThan(0)
    }
  })

  test("volume_1 has name, chapter_count 5, and core_conflict", () => {
    const o = loadOutline()
    expect(o.volume_1).toHaveProperty("name")
    expect(o.volume_1.chapter_count).toBe(5)
    expect(o.volume_1).toHaveProperty("core_conflict")
    expect(typeof o.volume_1.core_conflict).toBe("string")
    expect(o.volume_1.core_conflict.length).toBeGreaterThan(10)
  })
})

describe("CHARACTERS.md", () => {
  test("file exists", () => {
    expect(existsSync(".learnings/CHARACTERS.md")).toBe(true)
  })

  test("Wei Liang is listed", () => {
    const content = readFileSync(".learnings/CHARACTERS.md", "utf-8")
    expect(content).toContain("Wei Liang")
  })

  test("contains markdown table header with Name column", () => {
    const content = readFileSync(".learnings/CHARACTERS.md", "utf-8")
    expect(content).toContain("| Name")
  })
})

describe("PLOT_POINTS.md", () => {
  test("file exists", () => {
    expect(existsSync(".learnings/PLOT_POINTS.md")).toBe(true)
  })

  test("at least 2 plot points", () => {
    const content = readFileSync(".learnings/PLOT_POINTS.md", "utf-8")
    // Count numbered list entries (1. or 2. etc)
    const matches = content.match(/^\s*\d+\./gm) || []
    expect(matches.length).toBeGreaterThanOrEqual(2)
  })
})

describe("chapter_01.md", () => {
  test("file exists", () => {
    expect(existsSync("output/chapter_01.md")).toBe(true)
  })

  test("starts with H1 heading", () => {
    const content = loadChapter()
    expect(content.trimStart().startsWith("# Chapter 1")).toBe(true)
  })

  test("contains Chapter Summary section", () => {
    const content = loadChapter()
    expect(content).toMatch(/\*\*Chapter Summary\*\*:/i)
  })

  test("contains Chapter Hook section", () => {
    const content = loadChapter()
    expect(content).toMatch(/\*\*Chapter Hook\*\*:/i)
  })

  test("at least 400 words", () => {
    const content = loadChapter()
    const wordCount = content.split(/\s+/).filter(w => w.length > 0).length
    expect(wordCount).toBeGreaterThanOrEqual(400)
  })
})

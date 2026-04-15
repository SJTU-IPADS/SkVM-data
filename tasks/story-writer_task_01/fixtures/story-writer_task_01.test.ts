import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadData(): any {
  return JSON.parse(readFileSync("story_outline.json", "utf-8"))
}

describe("story_outline.json", () => {
  test("file exists", () => {
    expect(existsSync("story_outline.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadData()).not.toThrow()
  })

  test("has required top-level keys", () => {
    const d = loadData()
    expect(d).toHaveProperty("title")
    expect(d).toHaveProperty("protagonist")
    expect(d).toHaveProperty("acts")
    expect(d).toHaveProperty("themes")
  })

  test("protagonist name and occupation are correct", () => {
    const d = loadData()
    expect(d.protagonist.name).toBe("Dr. Elena Voss")
    expect(d.protagonist.occupation).toBe("marine biologist")
    expect(typeof d.protagonist.goal).toBe("string")
    expect(d.protagonist.goal.length).toBeGreaterThan(5)
  })

  test("acts array has exactly 3 entries", () => {
    const d = loadData()
    expect(Array.isArray(d.acts)).toBe(true)
    expect(d.acts.length).toBe(3)
  })

  test("act names are Setup, Confrontation, Resolution", () => {
    const d = loadData()
    const names = d.acts.map((a: any) => a.name)
    expect(names).toContain("Setup")
    expect(names).toContain("Confrontation")
    expect(names).toContain("Resolution")
  })

  test("each act has act, name, summary, conflict fields", () => {
    const d = loadData()
    for (const a of d.acts) {
      expect(typeof a.act).toBe("number")
      expect(typeof a.name).toBe("string")
      expect(typeof a.summary).toBe("string")
      expect(a.summary.length).toBeGreaterThan(20)
      expect(typeof a.conflict).toBe("string")
      expect(a.conflict.length).toBeGreaterThan(5)
    }
  })

  test("acts are ordered 1, 2, 3", () => {
    const d = loadData()
    expect(d.acts[0].act).toBe(1)
    expect(d.acts[1].act).toBe(2)
    expect(d.acts[2].act).toBe(3)
  })

  test("themes array has at least 2 string entries", () => {
    const d = loadData()
    expect(Array.isArray(d.themes)).toBe(true)
    expect(d.themes.length).toBeGreaterThanOrEqual(2)
    for (const t of d.themes) {
      expect(typeof t).toBe("string")
    }
  })

  test("title is a non-empty string within length limits", () => {
    const d = loadData()
    expect(typeof d.title).toBe("string")
    expect(d.title.length).toBeGreaterThan(0)
    expect(d.title.length).toBeLessThanOrEqual(80)
  })
})

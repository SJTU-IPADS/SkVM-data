import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadData(): any {
  return JSON.parse(readFileSync("characters_and_dialogue.json", "utf-8"))
}

describe("characters_and_dialogue.json", () => {
  test("file exists", () => {
    expect(existsSync("characters_and_dialogue.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadData()).not.toThrow()
  })

  test("has required top-level keys", () => {
    const d = loadData()
    expect(d).toHaveProperty("characters")
    expect(d).toHaveProperty("dialogue")
    expect(d).toHaveProperty("setting_description")
  })

  test("characters array has exactly 2 entries", () => {
    const d = loadData()
    expect(Array.isArray(d.characters)).toBe(true)
    expect(d.characters.length).toBe(2)
  })

  test("each character has required fields with correct types", () => {
    const d = loadData()
    for (const c of d.characters) {
      expect(typeof c.name).toBe("string")
      expect(typeof c.age).toBe("number")
      expect(c.age).toBeGreaterThanOrEqual(18)
      expect(c.age).toBeLessThanOrEqual(80)
      expect(typeof c.role).toBe("string")
      expect(typeof c.personality).toBe("string")
      expect(c.personality.length).toBeGreaterThan(5)
      expect(typeof c.motivation).toBe("string")
      expect(c.motivation.length).toBeGreaterThan(5)
      expect(typeof c.flaw).toBe("string")
      expect(c.flaw.length).toBeGreaterThan(0)
    }
  })

  test("navigator and engineer roles are both present", () => {
    const d = loadData()
    const roles = d.characters.map((c: any) => c.role)
    expect(roles).toContain("navigator")
    expect(roles).toContain("engineer")
  })

  test("dialogue has at least 8 exchanges", () => {
    const d = loadData()
    expect(Array.isArray(d.dialogue)).toBe(true)
    expect(d.dialogue.length).toBeGreaterThanOrEqual(8)
  })

  test("all speakers in dialogue match a character name", () => {
    const d = loadData()
    const names = new Set(d.characters.map((c: any) => c.name))
    for (const exchange of d.dialogue) {
      expect(typeof exchange.speaker).toBe("string")
      expect(names.has(exchange.speaker)).toBe(true)
      expect(typeof exchange.line).toBe("string")
      expect(exchange.line.length).toBeGreaterThan(5)
    }
  })

  test("setting_description is a non-empty string", () => {
    const d = loadData()
    expect(typeof d.setting_description).toBe("string")
    expect(d.setting_description.length).toBeGreaterThan(20)
  })
})

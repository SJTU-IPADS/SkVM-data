import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadPersona(): any {
  return JSON.parse(readFileSync("persona.json", "utf-8"))
}

const VALID_ARCHETYPES = new Set(["power_user", "casual_user", "business_user", "mobile_first"])
const VALID_PROFICIENCY = new Set(["Basic", "Intermediate", "Advanced"])
const VALID_FREQUENCY = new Set(["daily", "weekly", "monthly"])
const VALID_DEVICES = new Set(["desktop", "mobile", "tablet"])
const VALID_CONFIDENCE = new Set(["Low", "Medium", "High"])

describe("persona.json", () => {
  test("file exists", () => {
    expect(existsSync("persona.json")).toBe(true)
  })

  test("has all required fields", () => {
    const p = loadPersona()
    const required = ["archetype", "name", "age_range", "tech_proficiency", "usage_frequency",
      "primary_device", "top_features", "goals", "frustrations", "design_implications",
      "sample_size", "confidence"]
    for (const field of required) {
      expect(p).toHaveProperty(field)
    }
  })

  test("archetype is power_user", () => {
    const p = loadPersona()
    expect(VALID_ARCHETYPES.has(p.archetype)).toBe(true)
    expect(p.archetype).toBe("power_user")
  })

  test("age_range is 28-35", () => {
    const p = loadPersona()
    expect(p.age_range).toBe("28-35")
  })

  test("tech_proficiency is Advanced", () => {
    const p = loadPersona()
    expect(VALID_PROFICIENCY.has(p.tech_proficiency)).toBe(true)
    expect(p.tech_proficiency).toBe("Advanced")
  })

  test("usage_frequency is daily", () => {
    const p = loadPersona()
    expect(VALID_FREQUENCY.has(p.usage_frequency)).toBe(true)
    expect(p.usage_frequency).toBe("daily")
  })

  test("primary_device is desktop", () => {
    const p = loadPersona()
    expect(VALID_DEVICES.has(p.primary_device)).toBe(true)
    expect(p.primary_device).toBe("desktop")
  })

  test("sample_size is 50", () => {
    const p = loadPersona()
    expect(p.sample_size).toBe(50)
  })

  test("confidence is High", () => {
    const p = loadPersona()
    expect(VALID_CONFIDENCE.has(p.confidence)).toBe(true)
    expect(p.confidence).toBe("High")
  })

  test("top_features is array with at least 3 entries", () => {
    const p = loadPersona()
    expect(Array.isArray(p.top_features)).toBe(true)
    expect(p.top_features.length).toBeGreaterThanOrEqual(3)
    for (const f of p.top_features) {
      expect(typeof f).toBe("string")
    }
  })

  test("frustrations has three frustration entries with frequency field", () => {
    const p = loadPersona()
    expect(Array.isArray(p.frustrations)).toBe(true)
    expect(p.frustrations.length).toBe(3)
    for (const f of p.frustrations) {
      expect(f).toHaveProperty("issue")
      expect(f).toHaveProperty("frequency")
      expect(typeof f.frequency).toBe("number")
    }
  })

  test("frustration frequencies match survey data: 42, 30, 25", () => {
    const p = loadPersona()
    const freqs = p.frustrations.map((f: any) => f.frequency).sort((a: number, b: number) => b - a)
    expect(freqs[0]).toBe(42)
    expect(freqs[1]).toBe(30)
    expect(freqs[2]).toBe(25)
  })

  test("design_implications is array with at least 3 entries", () => {
    const p = loadPersona()
    expect(Array.isArray(p.design_implications)).toBe(true)
    expect(p.design_implications.length).toBeGreaterThanOrEqual(3)
  })
})

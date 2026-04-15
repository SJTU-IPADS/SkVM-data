import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadNotes(): any[] {
  return JSON.parse(readFileSync("memory/notes/notes.json", "utf-8"))
}

function loadSearchResults(): any {
  return JSON.parse(readFileSync("search_results.json", "utf-8"))
}

function loadSynthesis(): any {
  return JSON.parse(readFileSync("synthesis.json", "utf-8"))
}

describe("memory/notes/notes.json", () => {
  test("notes file exists", () => {
    expect(existsSync("memory/notes/notes.json")).toBe(true)
  })

  test("valid JSON with exactly 5 notes", () => {
    const notes = loadNotes()
    expect(Array.isArray(notes)).toBe(true)
    expect(notes.length).toBe(5)
  })

  test("notes contain NOTE-001 through NOTE-005", () => {
    const notes = loadNotes()
    const ids = new Set(notes.map((n: any) => n.id))
    for (let i = 1; i <= 5; i++) {
      expect(ids.has(`NOTE-00${i}`)).toBe(true)
    }
  })
})

describe("search_results.json", () => {
  test("search results file exists", () => {
    expect(existsSync("search_results.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadSearchResults()).not.toThrow()
  })

  test("has query, matched_note_ids, and count fields", () => {
    const s = loadSearchResults()
    expect(s).toHaveProperty("query")
    expect(s).toHaveProperty("matched_note_ids")
    expect(s).toHaveProperty("count")
  })

  test("query is growth-metrics", () => {
    const s = loadSearchResults()
    expect(s.query).toBe("growth-metrics")
  })

  test("matched_note_ids contains exactly the 4 growth-metrics notes", () => {
    const s = loadSearchResults()
    expect(Array.isArray(s.matched_note_ids)).toBe(true)
    expect(s.matched_note_ids.length).toBe(4)
    const ids = new Set(s.matched_note_ids)
    expect(ids.has("NOTE-001")).toBe(true)
    expect(ids.has("NOTE-002")).toBe(true)
    expect(ids.has("NOTE-003")).toBe(true)
    expect(ids.has("NOTE-004")).toBe(true)
    expect(ids.has("NOTE-005")).toBe(false)
  })

  test("count equals 4", () => {
    const s = loadSearchResults()
    expect(s.count).toBe(4)
  })
})

describe("synthesis.json", () => {
  test("synthesis file exists", () => {
    expect(existsSync("synthesis.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadSynthesis()).not.toThrow()
  })

  test("has topic, framework_title, key_concepts, relationships, summary fields", () => {
    const s = loadSynthesis()
    expect(s).toHaveProperty("topic")
    expect(s).toHaveProperty("framework_title")
    expect(s).toHaveProperty("key_concepts")
    expect(s).toHaveProperty("relationships")
    expect(s).toHaveProperty("summary")
  })

  test("key_concepts has at least 4 entries with name, definition, and source_note", () => {
    const s = loadSynthesis()
    expect(Array.isArray(s.key_concepts)).toBe(true)
    expect(s.key_concepts.length).toBeGreaterThanOrEqual(4)
    for (const c of s.key_concepts) {
      expect(typeof c.name).toBe("string")
      expect(typeof c.definition).toBe("string")
      expect(typeof c.source_note).toBe("string")
      expect(c.source_note).toMatch(/^NOTE-\d{3}$/)
    }
  })

  test("key_concepts include CAC, LTV, churn_rate, and payback_period", () => {
    const s = loadSynthesis()
    const names = s.key_concepts.map((c: any) => c.name.toLowerCase())
    const hasCAC = names.some((n: string) => n.includes("cac"))
    const hasLTV = names.some((n: string) => n.includes("ltv"))
    const hasChurn = names.some((n: string) => n.includes("churn"))
    const hasPayback = names.some((n: string) => n.includes("payback"))
    expect(hasCAC).toBe(true)
    expect(hasLTV).toBe(true)
    expect(hasChurn).toBe(true)
    expect(hasPayback).toBe(true)
  })

  test("relationships array has at least 2 entries", () => {
    const s = loadSynthesis()
    expect(Array.isArray(s.relationships)).toBe(true)
    expect(s.relationships.length).toBeGreaterThanOrEqual(2)
  })

  test("summary is a non-empty string of at least 50 characters", () => {
    const s = loadSynthesis()
    expect(typeof s.summary).toBe("string")
    expect(s.summary.length).toBeGreaterThanOrEqual(50)
  })
})

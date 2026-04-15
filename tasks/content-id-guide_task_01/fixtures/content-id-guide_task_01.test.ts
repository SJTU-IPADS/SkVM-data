import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadChecklist(): any {
  return JSON.parse(readFileSync("claim_evidence_checklist.json", "utf-8"))
}

function loadSummary(): string {
  return readFileSync("evidence_summary.md", "utf-8")
}

describe("claim_evidence_checklist.json", () => {
  test("file exists", () => {
    expect(existsSync("claim_evidence_checklist.json")).toBe(true)
  })

  test("is valid JSON with required top-level keys", () => {
    const c = loadChecklist()
    expect(c).toHaveProperty("claim_summary")
    expect(c).toHaveProperty("match_segments")
    expect(c).toHaveProperty("evidence_inventory")
    expect(c).toHaveProperty("process_notes")
    expect(c).toHaveProperty("disclaimer_acknowledged")
  })

  test("claim_summary has correct platform and claim type", () => {
    const c = loadChecklist()
    const cs = c.claim_summary
    expect(typeof cs.platform).toBe("string")
    expect(cs.platform.toLowerCase()).toMatch(/youtube/)
    expect(typeof cs.claim_type).toBe("string")
    expect(cs.claim_type.toLowerCase()).toMatch(/audio|content id/)
    expect(typeof cs.enforcement_action).toBe("string")
    expect(typeof cs.match_segment_count).toBe("number")
  })

  test("match_segment_count matches actual segments array length", () => {
    const c = loadChecklist()
    expect(c.claim_summary.match_segment_count).toBe(c.match_segments.length)
  })

  test("match_segments has exactly 2 entries with start and end", () => {
    const c = loadChecklist()
    expect(Array.isArray(c.match_segments)).toBe(true)
    expect(c.match_segments.length).toBe(2)
    for (const seg of c.match_segments) {
      expect(typeof seg.start).toBe("string")
      expect(typeof seg.end).toBe("string")
    }
  })

  test("evidence_inventory has correct boolean fields", () => {
    const c = loadChecklist()
    const ev = c.evidence_inventory
    expect(typeof ev.has_license_documentation).toBe("boolean")
    expect(typeof ev.has_usage_description).toBe("boolean")
    expect(typeof ev.has_scope_documentation).toBe("boolean")
    expect(typeof ev.documentation_notes).toBe("string")
    // Creator stated they have license, usage description, and worldwide scope
    expect(ev.has_license_documentation).toBe(true)
    expect(ev.has_usage_description).toBe(true)
    expect(ev.has_scope_documentation).toBe(true)
  })

  test("process_notes is a string between 50 and 200 words", () => {
    const c = loadChecklist()
    expect(typeof c.process_notes).toBe("string")
    const wordCount = c.process_notes.trim().split(/\s+/).length
    expect(wordCount).toBeGreaterThanOrEqual(50)
    expect(wordCount).toBeLessThanOrEqual(200)
  })

  test("disclaimer_acknowledged is true", () => {
    const c = loadChecklist()
    expect(c.disclaimer_acknowledged).toBe(true)
  })
})

describe("evidence_summary.md", () => {
  test("file exists", () => {
    expect(existsSync("evidence_summary.md")).toBe(true)
  })

  test("summary is at least 100 words", () => {
    const text = loadSummary()
    const wordCount = text.trim().split(/\s+/).length
    expect(wordCount).toBeGreaterThanOrEqual(100)
  })

  test("summary mentions key documentation categories", () => {
    const text = loadSummary().toLowerCase()
    expect(text).toMatch(/license|invoice|permission/)
    expect(text).toMatch(/usage|review|purpose/)
    expect(text).toMatch(/scope|geographic|territory|worldwide|distribution/)
  })
})

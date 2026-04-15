import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadProposal(): string {
  return readFileSync("proposal.md", "utf-8")
}

function loadMeta(): any {
  return JSON.parse(readFileSync("proposal_meta.json", "utf-8"))
}

describe("proposal.md", () => {
  test("file exists", () => {
    expect(existsSync("proposal.md")).toBe(true)
  })

  test("starts with h1 heading Dark Mode Support", () => {
    const md = loadProposal()
    expect(md.trimStart().startsWith("# Dark Mode Support")).toBe(true)
  })

  test("contains Summary section", () => {
    const md = loadProposal()
    expect(md).toContain("## Summary")
  })

  test("contains Motivation section", () => {
    const md = loadProposal()
    expect(md).toContain("## Motivation")
  })

  test("contains Design section", () => {
    const md = loadProposal()
    expect(md).toContain("## Design")
  })

  test("contains Phases section with exactly 3 Phase headings", () => {
    const md = loadProposal()
    expect(md).toContain("## Phases")
    const phaseMatches = md.match(/^### Phase \d+/gm) || []
    expect(phaseMatches.length).toBe(3)
  })

  test("each phase section has at least 2 checklist items", () => {
    const md = loadProposal()
    // Find all checklist items
    const checklistItems = md.match(/^- \[ \]/gm) || []
    // At least 2 per phase = at least 6 total
    expect(checklistItems.length).toBeGreaterThanOrEqual(6)
  })

  test("contains Acceptance Criteria section with at least 4 numbered items", () => {
    const md = loadProposal()
    expect(md).toContain("## Acceptance Criteria")
    // numbered list items: "1. " "2. " etc
    const numberedItems = md.match(/^\d+\. .+/gm) || []
    expect(numberedItems.length).toBeGreaterThanOrEqual(4)
  })

  test("contains Open Questions section", () => {
    const md = loadProposal()
    expect(md).toContain("## Open Questions")
  })

  test("contains Status section with Draft or Ready", () => {
    const md = loadProposal()
    expect(md).toContain("## Status")
    const statusMatch = md.match(/## Status[\s\S]*?(Draft|Ready)/m)
    expect(statusMatch).not.toBeNull()
  })
})

describe("proposal_meta.json", () => {
  test("file exists", () => {
    expect(existsSync("proposal_meta.json")).toBe(true)
  })

  test("has required fields", () => {
    const m = loadMeta()
    expect(m).toHaveProperty("title")
    expect(m).toHaveProperty("feature")
    expect(m).toHaveProperty("status")
    expect(m).toHaveProperty("phase_count")
    expect(m).toHaveProperty("phases")
  })

  test("title is Dark Mode Support and phase_count is 3", () => {
    const m = loadMeta()
    expect(m.title).toBe("Dark Mode Support")
    expect(m.phase_count).toBe(3)
  })

  test("phases array has 3 entries with number and name", () => {
    const m = loadMeta()
    expect(Array.isArray(m.phases)).toBe(true)
    expect(m.phases.length).toBe(3)
    for (const phase of m.phases) {
      expect(phase).toHaveProperty("number")
      expect(phase).toHaveProperty("name")
      expect(typeof phase.name).toBe("string")
      expect(phase.name.trim().length).toBeGreaterThan(0)
    }
  })

  test("status is Draft or Ready", () => {
    const m = loadMeta()
    expect(["Draft", "Ready"]).toContain(m.status)
  })
})

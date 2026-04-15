import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadRBM(): any {
  return JSON.parse(readFileSync("rbm_chain.json", "utf-8"))
}

function loadLogframe(): any {
  return JSON.parse(readFileSync("logframe.json", "utf-8"))
}

describe("rbm_chain.json", () => {
  test("rbm chain file exists", () => {
    expect(existsSync("rbm_chain.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadRBM()).not.toThrow()
  })

  test("has required fields: project, inputs, activities, outputs, outcomes, impact", () => {
    const r = loadRBM()
    expect(r).toHaveProperty("project")
    expect(r).toHaveProperty("inputs")
    expect(r).toHaveProperty("activities")
    expect(r).toHaveProperty("outputs")
    expect(r).toHaveProperty("outcomes")
    expect(r).toHaveProperty("impact")
  })

  test("inputs array has at least 3 entries", () => {
    const r = loadRBM()
    expect(Array.isArray(r.inputs)).toBe(true)
    expect(r.inputs.length).toBeGreaterThanOrEqual(3)
  })

  test("activities array has at least 4 entries", () => {
    const r = loadRBM()
    expect(Array.isArray(r.activities)).toBe(true)
    expect(r.activities.length).toBeGreaterThanOrEqual(4)
  })

  test("outputs array has at least 3 entries", () => {
    const r = loadRBM()
    expect(Array.isArray(r.outputs)).toBe(true)
    expect(r.outputs.length).toBeGreaterThanOrEqual(3)
  })

  test("outcomes has short_term and long_term arrays with required minimums", () => {
    const r = loadRBM()
    expect(r.outcomes).toHaveProperty("short_term")
    expect(r.outcomes).toHaveProperty("long_term")
    expect(Array.isArray(r.outcomes.short_term)).toBe(true)
    expect(r.outcomes.short_term.length).toBeGreaterThanOrEqual(2)
    expect(Array.isArray(r.outcomes.long_term)).toBe(true)
    expect(r.outcomes.long_term.length).toBeGreaterThanOrEqual(1)
  })

  test("impact field is a non-empty string", () => {
    const r = loadRBM()
    expect(typeof r.impact).toBe("string")
    expect(r.impact.length).toBeGreaterThan(10)
  })
})

describe("logframe.json", () => {
  test("logframe file exists", () => {
    expect(existsSync("logframe.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadLogframe()).not.toThrow()
  })

  test("logframe array contains exactly 9 rows", () => {
    const l = loadLogframe()
    expect(Array.isArray(l.logframe)).toBe(true)
    expect(l.logframe.length).toBe(9)
  })

  test("each logframe row has required fields: level, description, indicator, baseline, target, means_of_verification, assumptions", () => {
    const l = loadLogframe()
    for (const row of l.logframe) {
      expect(typeof row.level).toBe("string")
      expect(typeof row.description).toBe("string")
      expect(typeof row.indicator).toBe("string")
      expect(typeof row.baseline).toBe("string")
      expect(typeof row.target).toBe("string")
      expect(typeof row.means_of_verification).toBe("string")
      expect(typeof row.assumptions).toBe("string")
    }
  })

  test("logframe level distribution: 1 Impact, 2 Outcome, 3 Output, 3 Activity rows", () => {
    const l = loadLogframe()
    const counts: Record<string, number> = {}
    for (const row of l.logframe) {
      const lvl = row.level
      counts[lvl] = (counts[lvl] || 0) + 1
    }
    expect(counts["Impact"]).toBe(1)
    expect(counts["Outcome"]).toBe(2)
    expect(counts["Output"]).toBe(3)
    expect(counts["Activity"]).toBe(3)
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadRecommendation(): any {
  return JSON.parse(readFileSync("recommendation.json", "utf-8"))
}

const VALID_INDEXES = new Set(["B-tree", "Hash", "Bitmap"])
const VALID_CONFIDENCE = new Set(["high", "medium", "low"])

describe("task_plan.md", () => {
  test("file exists", () => {
    expect(existsSync("task_plan.md")).toBe(true)
  })

  test("contains Goal section", () => {
    const content = readFileSync("task_plan.md", "utf-8")
    expect(content).toMatch(/Goal:/i)
  })

  test("task_plan has Phases, Decisions, and Errors sections", () => {
    const content = readFileSync("task_plan.md", "utf-8")
    expect(content).toMatch(/##\s+Phases/i)
    expect(content).toMatch(/##\s+Decisions/i)
    expect(content).toMatch(/##\s+Errors/i)
  })

  test("at least 4 phases listed", () => {
    const content = readFileSync("task_plan.md", "utf-8")
    // Count lines that look like phase entries (numbered, bulleted, or checkbox)
    const phaseMatches = content.match(/^[-*]\s+|\d+\.\s+|\[[ x]\]/gm) || []
    expect(phaseMatches.length).toBeGreaterThanOrEqual(4)
  })
})

describe("findings.md", () => {
  test("file exists", () => {
    expect(existsSync("findings.md")).toBe(true)
  })

  test("contains Research Findings heading", () => {
    const content = readFileSync("findings.md", "utf-8")
    expect(content).toMatch(/# Research Findings/i)
  })

  test("contains B-tree, Hash, and Bitmap subsections", () => {
    const content = readFileSync("findings.md", "utf-8")
    expect(content).toMatch(/##\s+B-tree/i)
    expect(content).toMatch(/##\s+Hash/i)
    expect(content).toMatch(/##\s+Bitmap/i)
  })

  test("each index type section has at least 3 bullet points", () => {
    const content = readFileSync("findings.md", "utf-8")
    const bullets = content.match(/^[-*]\s+\S/gm) || []
    // 3 sections * 3 bullets = at least 9 bullets total
    expect(bullets.length).toBeGreaterThanOrEqual(9)
  })
})

describe("progress.md", () => {
  test("file exists", () => {
    expect(existsSync("progress.md")).toBe(true)
  })

  test("contains Session Log heading", () => {
    const content = readFileSync("progress.md", "utf-8")
    expect(content).toMatch(/# Session Log/i)
  })

  test("at least 2 timestamped log entries", () => {
    const content = readFileSync("progress.md", "utf-8")
    const entries = content.match(/\[\d{4}-\d{2}-\d{2}/g) || []
    expect(entries.length).toBeGreaterThanOrEqual(2)
  })
})

describe("recommendation.json", () => {
  test("file exists", () => {
    expect(existsSync("recommendation.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadRecommendation()).not.toThrow()
  })

  test("recommendation has required fields", () => {
    const r = loadRecommendation()
    expect(r).toHaveProperty("use_case")
    expect(r).toHaveProperty("recommended_index")
    expect(r).toHaveProperty("confidence")
    expect(r).toHaveProperty("reasons")
    expect(r).toHaveProperty("tradeoffs_accepted")
  })

  test("recommended_index is a valid value", () => {
    const r = loadRecommendation()
    expect(VALID_INDEXES.has(r.recommended_index)).toBe(true)
  })

  test("confidence is high, medium, or low", () => {
    const r = loadRecommendation()
    expect(VALID_CONFIDENCE.has(r.confidence)).toBe(true)
  })

  test("reasons has at least 3 non-empty strings", () => {
    const r = loadRecommendation()
    expect(Array.isArray(r.reasons)).toBe(true)
    expect(r.reasons.length).toBeGreaterThanOrEqual(3)
    for (const reason of r.reasons) {
      expect(typeof reason).toBe("string")
      expect(reason.length).toBeGreaterThan(5)
    }
  })

  test("tradeoffs_accepted has at least 2 non-empty strings", () => {
    const r = loadRecommendation()
    expect(Array.isArray(r.tradeoffs_accepted)).toBe(true)
    expect(r.tradeoffs_accepted.length).toBeGreaterThanOrEqual(2)
    for (const t of r.tradeoffs_accepted) {
      expect(typeof t).toBe("string")
      expect(t.length).toBeGreaterThan(5)
    }
  })
})

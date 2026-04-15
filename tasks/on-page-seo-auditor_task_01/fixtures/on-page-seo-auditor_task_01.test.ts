import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadAudit(): any {
  return JSON.parse(readFileSync("seo_audit.json", "utf-8"))
}

const VALID_SEVERITIES = new Set(["critical", "important", "minor"])

describe("seo_audit.json", () => {
  test("file exists", () => {
    expect(existsSync("seo_audit.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadAudit()).not.toThrow()
  })

  test("target_keyword is noise-cancelling headphones under 100", () => {
    const a = loadAudit()
    expect(a.target_keyword).toBe("noise-cancelling headphones under 100")
  })

  test("scores has all required fields", () => {
    const a = loadAudit()
    expect(a).toHaveProperty("scores")
    expect(a.scores).toHaveProperty("title_tag")
    expect(a.scores).toHaveProperty("meta_description")
    expect(a.scores).toHaveProperty("h1")
    expect(a.scores).toHaveProperty("images")
    expect(a.scores).toHaveProperty("overall")
  })

  test("all component scores are integers 0-10", () => {
    const a = loadAudit()
    const componentKeys = ["title_tag", "meta_description", "h1", "images"]
    for (const key of componentKeys) {
      const val = a.scores[key]
      expect(Number.isInteger(val)).toBe(true)
      expect(val).toBeGreaterThanOrEqual(0)
      expect(val).toBeLessThanOrEqual(10)
    }
  })

  test("overall is average of the 4 component scores (within 0.2 tolerance)", () => {
    const a = loadAudit()
    const { title_tag, meta_description, h1, images, overall } = a.scores
    const expected = (title_tag + meta_description + h1 + images) / 4
    expect(Math.abs(overall - expected)).toBeLessThanOrEqual(0.2)
  })

  test("at least 4 issues in issues array", () => {
    const a = loadAudit()
    expect(Array.isArray(a.issues)).toBe(true)
    expect(a.issues.length).toBeGreaterThanOrEqual(4)
  })

  test("each issue has element, severity, description, and recommendation", () => {
    const a = loadAudit()
    for (const issue of a.issues) {
      expect(issue).toHaveProperty("element")
      expect(issue).toHaveProperty("severity")
      expect(issue).toHaveProperty("description")
      expect(issue).toHaveProperty("recommendation")
    }
  })

  test("severity values are valid (critical, important, or minor)", () => {
    const a = loadAudit()
    for (const issue of a.issues) {
      expect(VALID_SEVERITIES.has(issue.severity)).toBe(true)
    }
  })

  test("optimized_title is 50-60 chars", () => {
    const a = loadAudit()
    expect(a).toHaveProperty("optimized_title")
    expect(typeof a.optimized_title).toBe("string")
    expect(a.optimized_title.length).toBeGreaterThanOrEqual(50)
    expect(a.optimized_title.length).toBeLessThanOrEqual(60)
  })

  test("optimized_meta_description length is 140-165 chars", () => {
    const a = loadAudit()
    expect(a).toHaveProperty("optimized_meta_description")
    expect(typeof a.optimized_meta_description).toBe("string")
    expect(a.optimized_meta_description.length).toBeGreaterThanOrEqual(140)
    expect(a.optimized_meta_description.length).toBeLessThanOrEqual(165)
  })
})

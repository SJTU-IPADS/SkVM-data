import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadData(): any {
  return JSON.parse(readFileSync("crawlability_audit.json", "utf-8"))
}

describe("crawlability_audit.json", () => {
  test("file exists", () => {
    expect(existsSync("crawlability_audit.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadData()).not.toThrow()
  })

  test("has required top-level keys", () => {
    const d = loadData()
    expect(d).toHaveProperty("domain")
    expect(d).toHaveProperty("robots_txt")
    expect(d).toHaveProperty("crawlability_score")
    expect(d).toHaveProperty("recommendations")
  })

  test("domain is example.com", () => {
    const d = loadData()
    expect(d.domain).toBe("example.com")
  })

  test("robots_txt has required subfields", () => {
    const d = loadData()
    expect(d.robots_txt).toHaveProperty("sitemap_declared")
    expect(d.robots_txt).toHaveProperty("sitemap_url")
    expect(d.robots_txt).toHaveProperty("disallowed_paths")
    expect(d.robots_txt).toHaveProperty("assets_blocked")
    expect(d.robots_txt).toHaveProperty("issues")
  })

  test("sitemap_declared is true", () => {
    const d = loadData()
    expect(d.robots_txt.sitemap_declared).toBe(true)
  })

  test("sitemap_url matches declared URL", () => {
    const d = loadData()
    expect(d.robots_txt.sitemap_url).toBe("https://example.com/sitemap.xml")
  })

  test("disallowed_paths has at least 5 entries", () => {
    const d = loadData()
    expect(Array.isArray(d.robots_txt.disallowed_paths)).toBe(true)
    expect(d.robots_txt.disallowed_paths.length).toBeGreaterThanOrEqual(5)
    // Must include /css/ and /js/
    const paths = d.robots_txt.disallowed_paths.join(" ")
    expect(paths).toMatch(/\/css\//)
    expect(paths).toMatch(/\/js\//)
  })

  test("assets_blocked is true", () => {
    const d = loadData()
    expect(d.robots_txt.assets_blocked).toBe(true)
  })

  test("issues array has at least 2 entries", () => {
    const d = loadData()
    expect(Array.isArray(d.robots_txt.issues)).toBe(true)
    expect(d.robots_txt.issues.length).toBeGreaterThanOrEqual(2)
  })

  test("crawlability_score is an integer between 0 and 10", () => {
    const d = loadData()
    expect(typeof d.crawlability_score).toBe("number")
    expect(d.crawlability_score).toBeGreaterThanOrEqual(0)
    expect(d.crawlability_score).toBeLessThanOrEqual(10)
    expect(Number.isInteger(d.crawlability_score)).toBe(true)
  })

  test("recommendations has at least 2 entries", () => {
    const d = loadData()
    expect(Array.isArray(d.recommendations)).toBe(true)
    expect(d.recommendations.length).toBeGreaterThanOrEqual(2)
    for (const r of d.recommendations) {
      expect(typeof r).toBe("string")
      expect(r.length).toBeGreaterThan(5)
    }
  })
})

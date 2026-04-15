import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadSummary(): string {
  return readFileSync("summary.txt", "utf-8")
}

function loadDigest(): string {
  return readFileSync("digest.txt", "utf-8")
}

function countWords(text: string): number {
  return text.trim().split(/\s+/).filter((w) => w.length > 0).length
}

function countParagraphs(text: string): number {
  return text.trim().split(/\n\s*\n/).filter((p) => p.trim().length > 0).length
}

describe("summary.txt", () => {
  test("file exists", () => {
    expect(existsSync("summary.txt")).toBe(true)
  })

  test("summary is non-empty and at least 40 words", () => {
    const s = loadSummary()
    expect(s.trim().length).toBeGreaterThan(0)
    expect(countWords(s)).toBeGreaterThanOrEqual(40)
  })

  test("summary is within 60-80 words (30% of ~250 word source, with tolerance)", () => {
    const s = loadSummary()
    const wc = countWords(s)
    expect(wc).toBeGreaterThanOrEqual(40)
    expect(wc).toBeLessThanOrEqual(120)
  })

  test("summary preserves key numbers: 14 features mentioned", () => {
    const s = loadSummary()
    expect(s).toMatch(/14\s+feature/i)
  })

  test("summary preserves key numbers: 87 bugs and 57% improvement", () => {
    const s = loadSummary()
    expect(s).toMatch(/87/i)
    expect(s).toMatch(/57%/i)
  })

  test("summary mentions 34% incident reduction and 23 incidents", () => {
    const s = loadSummary()
    expect(s).toMatch(/34%/i)
    expect(s).toMatch(/23/i)
  })

  test("summary has 3 paragraphs (overview, details, implications)", () => {
    const s = loadSummary()
    const paragraphs = countParagraphs(s)
    expect(paragraphs).toBeGreaterThanOrEqual(2)
    expect(paragraphs).toBeLessThanOrEqual(4)
  })

  test("summary first paragraph leads with main conclusion (performance improvement)", () => {
    const s = loadSummary()
    const firstPara = s.trim().split(/\n\s*\n/)[0].toLowerCase()
    expect(firstPara).toMatch(/engineer|ship|feature|performance|quarter/)
  })
})

describe("digest.txt", () => {
  test("file exists", () => {
    expect(existsSync("digest.txt")).toBe(true)
  })

  test("digest is non-empty with at least 30 words", () => {
    const d = loadDigest()
    expect(d.trim().length).toBeGreaterThan(0)
    expect(countWords(d)).toBeGreaterThanOrEqual(30)
  })

  test("digest word count is within 60-100 words (with tolerance)", () => {
    const d = loadDigest()
    const wc = countWords(d)
    expect(wc).toBeGreaterThanOrEqual(40)
    expect(wc).toBeLessThanOrEqual(150)
  })

  test("digest contains all three items: database migration, mobile beta, benefits enrollment", () => {
    const d = loadDigest().toLowerCase()
    expect(d).toMatch(/database|migration|postgresql/)
    expect(d).toMatch(/mobile|beta|app/)
    expect(d).toMatch(/benefit|enrollment|deadline/)
  })

  test("digest highlights April 18 deadline as urgent", () => {
    const d = loadDigest()
    expect(d).toMatch(/april 18|apr(il)?\s*18/i)
    expect(d.toLowerCase()).toMatch(/urgent|deadline|action required|must complete|by 5/)
  })

  test("digest has at least 3 bullet point lines", () => {
    const d = loadDigest()
    const bulletLines = d.split("\n").filter((l) => l.trim().match(/^[-*•]/))
    expect(bulletLines.length).toBeGreaterThanOrEqual(3)
  })

  test("digest has no ## markdown subheadings", () => {
    const d = loadDigest()
    expect(d).not.toMatch(/^##\s/m)
  })
})

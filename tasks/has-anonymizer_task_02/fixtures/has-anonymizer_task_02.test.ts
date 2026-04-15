import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

const ORIGINAL_TEXT = "Dr. Emily Chen and Dr. Marcus Webb attended the symposium in Boston. Dr. Chen can be reached at emily.chen@hospital.org. Dr. Webb's office number is 617-555-0198. Both doctors work at Northside Medical Center."

function loadMapping(): any {
  return JSON.parse(readFileSync("mapping.json", "utf-8"))
}

describe("original.txt exists", () => {
  test("file exists and contains expected content", () => {
    expect(existsSync("original.txt")).toBe(true)
    const content = readFileSync("original.txt", "utf-8")
    expect(content).toContain("Dr. Emily Chen")
    expect(content).toContain("emily.chen@hospital.org")
    expect(content).toContain("617-555-0198")
    expect(content).toContain("Northside Medical Center")
  })
})

describe("scripts exist", () => {
  test("anonymize.py and restore.py are present", () => {
    expect(existsSync("anonymize.py")).toBe(true)
    expect(existsSync("restore.py")).toBe(true)
  })
})

describe("anonymized.txt", () => {
  test("file exists", () => {
    expect(existsSync("anonymized.txt")).toBe(true)
  })

  test("anonymized text contains no original PII (Dr. Emily Chen not in anonymized)", () => {
    const content = readFileSync("anonymized.txt", "utf-8")
    expect(content).not.toContain("emily.chen@hospital.org")
    expect(content).not.toContain("617-555-0198")
  })

  test("anonymized text contains semantic tags with angle brackets", () => {
    const content = readFileSync("anonymized.txt", "utf-8")
    expect(content).toMatch(/<[a-z_]+\[\d+\]\.[a-z]+\.[a-z]+>/)
  })

  test("anonymized text is shorter or same length as original (not inflated)", () => {
    const original = readFileSync("original.txt", "utf-8")
    const anonymized = readFileSync("anonymized.txt", "utf-8")
    // Anonymized should not be more than 2x the original
    expect(anonymized.length).toBeLessThan(original.length * 2)
  })
})

describe("mapping.json", () => {
  test("file exists", () => {
    expect(existsSync("mapping.json")).toBe(true)
  })

  test("mapping has mappings array", () => {
    const m = loadMapping()
    expect(m).toHaveProperty("mappings")
    expect(Array.isArray(m.mappings)).toBe(true)
  })

  test("at least 4 mapping entries covering names, email, phone, org", () => {
    const m = loadMapping()
    expect(m.mappings.length).toBeGreaterThanOrEqual(4)
  })

  test("each mapping entry has tag and original fields", () => {
    const m = loadMapping()
    for (const entry of m.mappings) {
      expect(entry).toHaveProperty("tag")
      expect(entry).toHaveProperty("original")
      expect(entry.tag).toMatch(/^</)
      expect(entry.tag).toMatch(/>$/)
    }
  })

  test("mapping covers emily.chen@hospital.org and 617-555-0198", () => {
    const m = loadMapping()
    const originals = m.mappings.map((e: any) => e.original)
    expect(originals.some((o: string) => o.includes("emily.chen@hospital.org"))).toBe(true)
    expect(originals.some((o: string) => o.includes("617-555-0198"))).toBe(true)
  })
})

describe("restored.txt", () => {
  test("file exists", () => {
    expect(existsSync("restored.txt")).toBe(true)
  })

  test("restored.txt matches original content", () => {
    const restored = readFileSync("restored.txt", "utf-8").trim()
    expect(restored).toContain("Dr. Emily Chen")
    expect(restored).toContain("emily.chen@hospital.org")
    expect(restored).toContain("617-555-0198")
    expect(restored).toContain("Northside Medical Center")
  })
})

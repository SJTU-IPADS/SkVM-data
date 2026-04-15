import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadInventory(): any {
  return JSON.parse(readFileSync("claim_inventory.json", "utf-8"))
}

describe("claim_inventory.json", () => {
  test("file exists", () => {
    expect(existsSync("claim_inventory.json")).toBe(true)
  })

  test("is valid JSON with required top-level keys", () => {
    const inv = loadInventory()
    expect(inv).toHaveProperty("claims")
    expect(inv).toHaveProperty("total_claims")
    expect(inv).toHaveProperty("total_segments")
    expect(inv).toHaveProperty("pii_redacted")
  })

  test("claims array has exactly 2 entries", () => {
    const inv = loadInventory()
    expect(Array.isArray(inv.claims)).toBe(true)
    expect(inv.claims.length).toBe(2)
  })

  test("total_claims equals 2", () => {
    const inv = loadInventory()
    expect(inv.total_claims).toBe(2)
  })

  test("each claim has required fields with correct types", () => {
    const inv = loadInventory()
    for (const claim of inv.claims) {
      expect(typeof claim.platform).toBe("string")
      expect(typeof claim.claim_id).toBe("string")
      expect(typeof claim.claimant_identifier).toBe("string")
      expect(Array.isArray(claim.match_segments)).toBe(true)
      expect(typeof claim.enforcement_action).toBe("string")
      expect(typeof claim.segment_count).toBe("number")
    }
  })

  test("segment_count matches match_segments array length for each claim", () => {
    const inv = loadInventory()
    for (const claim of inv.claims) {
      expect(claim.segment_count).toBe(claim.match_segments.length)
    }
  })

  test("total_segments equals sum of all segment counts", () => {
    const inv = loadInventory()
    const sum = inv.claims.reduce((acc: number, c: any) => acc + c.segment_count, 0)
    expect(inv.total_segments).toBe(sum)
  })

  test("total_segments is 3 (1 from notice 1, 2 from notice 2)", () => {
    const inv = loadInventory()
    expect(inv.total_segments).toBe(3)
  })

  test("no email addresses present in JSON output (PII redacted)", () => {
    const raw = readFileSync("claim_inventory.json", "utf-8")
    expect(raw).not.toMatch(/rights@soundhouse\.example\.com/i)
    expect(raw).not.toMatch(/creator@example\.net/i)
    expect(raw).not.toMatch(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/)
  })

  test("no phone numbers present in JSON output (PII redacted)", () => {
    const raw = readFileSync("claim_inventory.json", "utf-8")
    expect(raw).not.toMatch(/\+1-555-234-5678/)
    expect(raw).not.toMatch(/\+1[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{4}/)
  })

  test("pii_redacted is true", () => {
    const inv = loadInventory()
    expect(inv.pii_redacted).toBe(true)
  })
})

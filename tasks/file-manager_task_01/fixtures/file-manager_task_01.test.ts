import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("dedup_report.json", "utf-8"))
}

describe("dedup_report.json", () => {
  test("file exists", () => {
    expect(existsSync("dedup_report.json")).toBe(true)
  })

  test("parses as valid JSON", () => {
    expect(() => loadReport()).not.toThrow()
  })

  test("has required top-level fields", () => {
    const r = loadReport()
    expect(r).toHaveProperty("total_files")
    expect(r).toHaveProperty("unique_hashes")
    expect(r).toHaveProperty("duplicate_groups")
    expect(r).toHaveProperty("duplicates_found")
  })

  test("total_files is 5", () => {
    const r = loadReport()
    expect(r.total_files).toBe(5)
  })

  test("unique_hashes is 3", () => {
    const r = loadReport()
    expect(r.unique_hashes).toBe(3)
  })

  test("duplicate_groups is an array", () => {
    const r = loadReport()
    expect(Array.isArray(r.duplicate_groups)).toBe(true)
  })

  test("contains exactly one duplicate group", () => {
    const r = loadReport()
    expect(r.duplicate_groups.length).toBe(1)
  })

  test("group has 3 files and count equals 3", () => {
    const r = loadReport()
    const group = r.duplicate_groups[0]
    expect(group.count).toBe(3)
    expect(Array.isArray(group.files)).toBe(true)
    expect(group.files.length).toBe(3)
  })

  test("group contains alpha.txt, beta.txt, delta.txt", () => {
    const r = loadReport()
    const files: string[] = r.duplicate_groups[0].files
    expect(files).toContain("alpha.txt")
    expect(files).toContain("beta.txt")
    expect(files).toContain("delta.txt")
  })

  test("files sorted alphabetically in duplicate group", () => {
    const r = loadReport()
    const files: string[] = r.duplicate_groups[0].files
    const sorted = [...files].sort()
    expect(files).toEqual(sorted)
  })

  test("duplicates_found is 2", () => {
    const r = loadReport()
    expect(r.duplicates_found).toBe(2)
  })

  test("group hash is a non-empty hex string", () => {
    const r = loadReport()
    const hash: string = r.duplicate_groups[0].hash
    expect(typeof hash).toBe("string")
    expect(hash.length).toBeGreaterThan(0)
    expect(/^[0-9a-fA-F]+$/.test(hash)).toBe(true)
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync, readdirSync } from "fs"
import { join } from "path"

function loadResults(): any {
  return JSON.parse(readFileSync("scan_results.json", "utf-8"))
}

describe("input files exist", () => {
  test("input_docs directory has 3 files", () => {
    expect(existsSync("input_docs")).toBe(true)
    const files = readdirSync("input_docs")
    expect(files.length).toBe(3)
  })

  test("report_a.txt, report_b.txt, report_c.txt exist", () => {
    expect(existsSync(join("input_docs", "report_a.txt"))).toBe(true)
    expect(existsSync(join("input_docs", "report_b.txt"))).toBe(true)
    expect(existsSync(join("input_docs", "report_c.txt"))).toBe(true)
  })

  test("report_a.txt contains alice.johnson@company.com", () => {
    const content = readFileSync(join("input_docs", "report_a.txt"), "utf-8")
    expect(content).toContain("alice.johnson@company.com")
  })
})

describe("scan_pii.py exists", () => {
  test("scan_pii.py is present", () => {
    expect(existsSync("scan_pii.py")).toBe(true)
  })

  test("scan_pii.py does not import requests or urllib or openai", () => {
    const script = readFileSync("scan_pii.py", "utf-8")
    expect(script).not.toMatch(/import\s+requests/)
    expect(script).not.toMatch(/import\s+openai/)
    expect(script).toContain("import re")
  })
})

describe("scan_results.json", () => {
  test("file exists", () => {
    expect(existsSync("scan_results.json")).toBe(true)
  })

  test("has scanned_files, results, summary", () => {
    const r = loadResults()
    expect(r).toHaveProperty("scanned_files")
    expect(r).toHaveProperty("results")
    expect(r).toHaveProperty("summary")
  })

  test("scanned_files is 3", () => {
    const r = loadResults()
    expect(r.scanned_files).toBe(3)
  })

  test("results array has 3 entries", () => {
    const r = loadResults()
    expect(Array.isArray(r.results)).toBe(true)
    expect(r.results.length).toBe(3)
  })

  test("each result entry has file, emails, phones, pii_found fields", () => {
    const r = loadResults()
    for (const entry of r.results) {
      expect(entry).toHaveProperty("file")
      expect(entry).toHaveProperty("emails")
      expect(entry).toHaveProperty("phones")
      expect(entry).toHaveProperty("pii_found")
      expect(Array.isArray(entry.emails)).toBe(true)
      expect(Array.isArray(entry.phones)).toBe(true)
    }
  })

  test("report_a has email alice.johnson@company.com and pii_found true", () => {
    const r = loadResults()
    const entryA = r.results.find((e: any) => e.file === "report_a.txt" || e.file.endsWith("report_a.txt"))
    expect(entryA).toBeDefined()
    expect(entryA.pii_found).toBe(true)
    const allEmails = entryA.emails.join(" ")
    expect(allEmails).toContain("alice.johnson@company.com")
  })

  test("report_c has no pii (pii_found false)", () => {
    const r = loadResults()
    const entryC = r.results.find((e: any) => e.file === "report_c.txt" || e.file.endsWith("report_c.txt"))
    expect(entryC).toBeDefined()
    expect(entryC.pii_found).toBe(false)
    expect(entryC.emails.length).toBe(0)
    expect(entryC.phones.length).toBe(0)
  })

  test("summary total_emails is at least 2 and total_phones is at least 2", () => {
    const r = loadResults()
    expect(r.summary).toHaveProperty("total_emails")
    expect(r.summary).toHaveProperty("total_phones")
    expect(r.summary.total_emails).toBeGreaterThanOrEqual(2)
    expect(r.summary.total_phones).toBeGreaterThanOrEqual(2)
  })

  test("files_with_pii is 2", () => {
    const r = loadResults()
    expect(r.summary).toHaveProperty("files_with_pii")
    expect(r.summary.files_with_pii).toBe(2)
  })
})

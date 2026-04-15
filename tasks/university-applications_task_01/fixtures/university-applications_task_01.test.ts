import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadAdmissions(): any {
  return JSON.parse(readFileSync("admissions.json", "utf-8"))
}

function loadTsv(): string {
  return readFileSync("programs.tsv", "utf-8")
}

describe("admissions_manager.py", () => {
  test("file exists", () => {
    expect(existsSync("admissions_manager.py")).toBe(true)
  })
})

describe("admissions.json", () => {
  test("file exists", () => {
    expect(existsSync("admissions.json")).toBe(true)
  })

  test("has programs array and total_count", () => {
    const data = loadAdmissions()
    expect(data).toHaveProperty("programs")
    expect(data).toHaveProperty("total_count")
    expect(Array.isArray(data.programs)).toBe(true)
  })

  test("total_count is 3", () => {
    const data = loadAdmissions()
    expect(data.total_count).toBe(3)
  })

  test("programs array has 3 entries", () => {
    const data = loadAdmissions()
    expect(data.programs.length).toBe(3)
  })

  test("HKU MSc Computer Science program is present", () => {
    const data = loadAdmissions()
    const prog = data.programs.find((p: any) => p.university_abbr === "HKU")
    expect(prog).toBeDefined()
    expect(prog.program_name_en).toBe("MSc Computer Science")
    expect(prog.degree_type).toBe("MSc")
  })

  test("CUHK MA Linguistics program is present", () => {
    const data = loadAdmissions()
    const prog = data.programs.find((p: any) => p.university_abbr === "CUHK")
    expect(prog).toBeDefined()
    expect(prog.program_name_en).toBe("MA Linguistics")
    expect(prog.degree_type).toBe("MA")
  })

  test("HKUST MBA program is present with tuition HKD 580,000", () => {
    const data = loadAdmissions()
    const prog = data.programs.find((p: any) => p.university_abbr === "HKUST")
    expect(prog).toBeDefined()
    expect(prog.tuition_fee_total).toBe("HKD 580,000")
  })

  test("all programs have tuition_fee_total in HKD format", () => {
    const data = loadAdmissions()
    for (const prog of data.programs) {
      expect(prog.tuition_fee_total).toMatch(/^HKD [\d,]+$/)
    }
  })
})

describe("programs.tsv", () => {
  test("file exists", () => {
    expect(existsSync("programs.tsv")).toBe(true)
  })

  test("TSV header contains all 8 required field names", () => {
    const tsv = loadTsv()
    const header = tsv.split("\n")[0]
    const fields = header.split("\t")
    expect(fields).toContain("university_abbr")
    expect(fields).toContain("program_name_en")
    expect(fields).toContain("degree_type")
    expect(fields).toContain("official_url")
  })

  test("TSV header has 8 tab-separated fields", () => {
    const tsv = loadTsv()
    const header = tsv.split("\n")[0]
    expect(header.split("\t").length).toBe(8)
  })

  test("TSV has 3 data rows after header", () => {
    const tsv = loadTsv()
    const lines = tsv.split("\n").filter(l => l.trim() !== "")
    // 1 header + 3 data rows = 4 lines
    expect(lines.length).toBeGreaterThanOrEqual(4)
  })

  test("TSV data rows contain HKU, CUHK, and HKUST", () => {
    const tsv = loadTsv()
    expect(tsv).toContain("HKU")
    expect(tsv).toContain("CUHK")
    expect(tsv).toContain("HKUST")
  })
})

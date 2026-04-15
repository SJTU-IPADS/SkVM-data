import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadDiagnosis(): any {
  return JSON.parse(readFileSync("formula_diagnosis.json", "utf-8"))
}

function loadCsv(): string {
  return readFileSync("budget_template.csv", "utf-8")
}

describe("formula_diagnosis.json", () => {
  test("formula_diagnosis.json file exists", () => {
    expect(existsSync("formula_diagnosis.json")).toBe(true)
  })

  test("has a top-level 'diagnoses' array", () => {
    const d = loadDiagnosis()
    expect(d).toHaveProperty("diagnoses")
    expect(Array.isArray(d.diagnoses)).toBe(true)
  })

  test("contains exactly 4 diagnoses", () => {
    const d = loadDiagnosis()
    expect(d.diagnoses.length).toBe(4)
  })

  test("error IDs are E1, E2, E3, E4", () => {
    const d = loadDiagnosis()
    const ids = d.diagnoses.map((e: any) => e.error_id).sort()
    expect(ids).toContain("E1")
    expect(ids).toContain("E2")
    expect(ids).toContain("E3")
    expect(ids).toContain("E4")
  })

  test("each entry has required fields: error_id, original_formula, error_type, error_description, corrected_formula", () => {
    const d = loadDiagnosis()
    for (const entry of d.diagnoses) {
      expect(entry).toHaveProperty("error_id")
      expect(entry).toHaveProperty("original_formula")
      expect(entry).toHaveProperty("error_type")
      expect(entry).toHaveProperty("error_description")
      expect(entry).toHaveProperty("corrected_formula")
    }
  })

  test("each corrected_formula starts with '='", () => {
    const d = loadDiagnosis()
    for (const entry of d.diagnoses) {
      expect(typeof entry.corrected_formula).toBe("string")
      expect(entry.corrected_formula.startsWith("=")).toBe(true)
    }
  })

  test("error descriptions are non-empty strings of at least 15 characters", () => {
    const d = loadDiagnosis()
    for (const entry of d.diagnoses) {
      expect(typeof entry.error_description).toBe("string")
      expect(entry.error_description.length).toBeGreaterThanOrEqual(15)
    }
  })
})

describe("budget_template.csv", () => {
  test("budget_template.csv file exists", () => {
    expect(existsSync("budget_template.csv")).toBe(true)
  })

  test("first row is the correct header: Date,Category,Description,Amount,Currency,Notes", () => {
    const csv = loadCsv()
    const firstLine = csv.split("\n")[0].trim()
    expect(firstLine).toBe("Date,Category,Description,Amount,Currency,Notes")
  })

  test("CSV has exactly 3 data rows (4 total lines including header)", () => {
    const csv = loadCsv()
    const lines = csv.split("\n").filter((l: string) => l.trim().length > 0)
    expect(lines.length).toBe(4)
  })

  test("each data row has 6 comma-separated fields", () => {
    const csv = loadCsv()
    const lines = csv.split("\n").filter((l: string) => l.trim().length > 0)
    for (const line of lines.slice(1)) {
      const fields = line.split(",")
      expect(fields.length).toBe(6)
    }
  })
})

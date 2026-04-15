import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadSummary(): any {
  return JSON.parse(readFileSync("admissions_summary.json", "utf-8"))
}

// Dataset: 8 programs across 4 universities
// Tuitions (sorted): 95000, 110000, 130000, 140000, 160000, 180000, 520000, 580000
// Sum = 1715000, mean = 214375
// Median = (140000 + 160000) / 2 = 150000
// Degree types: MSc=4, MA=2, MBA=2
// Study modes: Full-time=5, Part-time=2, Full-time & Part-time=1
// Per university: HKU=2, CUHK=2, HKUST=2, PolyU=1, CityU=1

describe("admissions_stats.py", () => {
  test("file exists", () => {
    expect(existsSync("admissions_stats.py")).toBe(true)
  })
})

describe("raw_programs.json", () => {
  test("file exists", () => {
    expect(existsSync("raw_programs.json")).toBe(true)
  })
})

describe("admissions_summary.json", () => {
  test("file exists", () => {
    expect(existsSync("admissions_summary.json")).toBe(true)
  })

  test("has all 6 required top-level keys", () => {
    const s = loadSummary()
    expect(s).toHaveProperty("total_programs")
    expect(s).toHaveProperty("universities_covered")
    expect(s).toHaveProperty("degree_type_distribution")
    expect(s).toHaveProperty("study_mode_distribution")
    expect(s).toHaveProperty("tuition_stats")
    expect(s).toHaveProperty("programs_per_university")
  })

  test("total_programs is 8", () => {
    const s = loadSummary()
    expect(s.total_programs).toBe(8)
  })

  test("universities_covered is 4 distinct universities", () => {
    const s = loadSummary()
    expect(s.universities_covered).toBe(4)
  })

  test("degree_type_distribution has MSc count 4", () => {
    const s = loadSummary()
    expect(s.degree_type_distribution["MSc"]).toBe(4)
  })

  test("degree_type_distribution has MA count 2 and MBA count 2", () => {
    const s = loadSummary()
    expect(s.degree_type_distribution["MA"]).toBe(2)
    expect(s.degree_type_distribution["MBA"]).toBe(2)
  })

  test("tuition_stats min is 95000 and max is 580000", () => {
    const s = loadSummary()
    expect(s.tuition_stats.min_hkd).toBe(95000)
    expect(s.tuition_stats.max_hkd).toBe(580000)
  })

  test("tuition_stats mean_hkd is 214375", () => {
    const s = loadSummary()
    expect(s.tuition_stats.mean_hkd).toBe(214375)
  })

  test("tuition_stats median_hkd is 150000", () => {
    const s = loadSummary()
    expect(s.tuition_stats.median_hkd).toBe(150000)
  })

  test("programs_per_university: HKU=2, CUHK=2, HKUST=2", () => {
    const s = loadSummary()
    expect(s.programs_per_university["HKU"]).toBe(2)
    expect(s.programs_per_university["CUHK"]).toBe(2)
    expect(s.programs_per_university["HKUST"]).toBe(2)
  })

  test("programs_per_university: PolyU=1, CityU=1", () => {
    const s = loadSummary()
    expect(s.programs_per_university["PolyU"]).toBe(1)
    expect(s.programs_per_university["CityU"]).toBe(1)
  })
})

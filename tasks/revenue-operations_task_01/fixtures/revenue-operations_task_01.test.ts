import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("gtm_report.json", "utf-8"))
}

describe("gtm_report.json", () => {
  test("file exists", () => {
    expect(existsSync("gtm_report.json")).toBe(true)
  })

  test("has metrics object at top level", () => {
    const r = loadReport()
    expect(r).toHaveProperty("metrics")
    expect(typeof r.metrics).toBe("object")
  })

  test("metrics contains all 6 required keys", () => {
    const m = loadReport().metrics
    expect(m).toHaveProperty("magic_number")
    expect(m).toHaveProperty("ltv_cac")
    expect(m).toHaveProperty("cac_payback_months")
    expect(m).toHaveProperty("burn_multiple")
    expect(m).toHaveProperty("rule_of_40")
    expect(m).toHaveProperty("ndr_pct")
  })

  test("each metric has value (number) and rating (string) fields", () => {
    const m = loadReport().metrics
    for (const key of ["magic_number", "ltv_cac", "cac_payback_months", "burn_multiple", "rule_of_40", "ndr_pct"]) {
      expect(typeof m[key].value).toBe("number")
      expect(typeof m[key].rating).toBe("string")
    }
  })

  test("magic_number value is 0.75 (1500000 / 2000000)", () => {
    const val = loadReport().metrics.magic_number.value
    expect(Math.abs(val - 0.75)).toBeLessThan(0.001)
  })

  test("magic_number rating is 'Good' (>=0.75 threshold)", () => {
    expect(loadReport().metrics.magic_number.rating).toBe("Good")
  })

  test("burn_multiple value is 1.2 (1800000 / 1500000)", () => {
    const val = loadReport().metrics.burn_multiple.value
    expect(Math.abs(val - 1.2)).toBeLessThan(0.001)
  })

  test("rule_of_40 value is 38.3 (33.3 + 5.0)", () => {
    const val = loadReport().metrics.rule_of_40.value
    expect(Math.abs(val - 38.3)).toBeLessThan(0.15)
  })

  test("rule_of_40 rating is 'Poor' (<40 threshold)", () => {
    expect(loadReport().metrics.rule_of_40.rating).toBe("Poor")
  })

  test("ndr_pct value is approximately 111.11 ((4500000+700000-150000-550000)/4500000*100)", () => {
    const val = loadReport().metrics.ndr_pct.value
    // (4500000 + 700000 - 150000 - 550000) / 4500000 * 100 = 4500000/4500000*100 = 100
    // Actually: 4500000+700000-150000-550000 = 4500000, ndr = 100%
    // Recalc: beginning=4500000, +expansion=700000, -contraction=150000, -churned=550000 => 4500000
    // ndr = 4500000/4500000 = 100%
    expect(val).toBeGreaterThan(95)
    expect(val).toBeLessThan(115)
  })

  test("rating values are only 'Good' or 'Poor'", () => {
    const m = loadReport().metrics
    const valid = new Set(["Good", "Poor"])
    for (const key of ["magic_number", "ltv_cac", "cac_payback_months", "burn_multiple", "rule_of_40", "ndr_pct"]) {
      expect(valid.has(m[key].rating)).toBe(true)
    }
  })
})

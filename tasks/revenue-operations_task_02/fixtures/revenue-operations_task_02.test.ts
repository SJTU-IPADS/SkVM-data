import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadAnalysis(): any {
  return JSON.parse(readFileSync("forecast_analysis.json", "utf-8"))
}

// Pre-computed expected values
// Q1: |520000-480000|/520000*100 = 40000/520000*100 = 7.6923...
// Q2: |510000-550000|/510000*100 = 40000/510000*100 = 7.8431...
// Q3: |580000-600000|/580000*100 = 20000/580000*100 = 3.4483...
// Q4: |650000-620000|/650000*100 = 30000/650000*100 = 4.6154...
// MAPE = (7.6923+7.8431+3.4483+4.6154)/4 = 23.5991/4 = 5.8998
// Biases: Q1=-40000, Q2=40000, Q3=20000(forecast)-actual: 600000-580000=20000, Q4=620000-650000=-30000
// mean_bias = (-40000+40000+20000-30000)/4 = -10000/4 = -2500

describe("forecast_analysis.json", () => {
  test("file exists", () => {
    expect(existsSync("forecast_analysis.json")).toBe(true)
  })

  test("has periods array and summary object", () => {
    const a = loadAnalysis()
    expect(Array.isArray(a.periods)).toBe(true)
    expect(typeof a.summary).toBe("object")
  })

  test("periods array has exactly 4 entries", () => {
    expect(loadAnalysis().periods.length).toBe(4)
  })

  test("each period has period, forecast, actual, absolute_pct_error, bias fields", () => {
    for (const p of loadAnalysis().periods) {
      expect(p).toHaveProperty("period")
      expect(p).toHaveProperty("forecast")
      expect(p).toHaveProperty("actual")
      expect(p).toHaveProperty("absolute_pct_error")
      expect(p).toHaveProperty("bias")
      expect(typeof p.absolute_pct_error).toBe("number")
      expect(typeof p.bias).toBe("number")
    }
  })

  test("Q1 absolute_pct_error is approximately 7.69 (40000/520000*100)", () => {
    const q1 = loadAnalysis().periods.find((p: any) => p.period === "Q1")
    expect(q1).toBeDefined()
    expect(Math.abs(q1.absolute_pct_error - 7.6923)).toBeLessThan(0.02)
  })

  test("summary has mape, mean_bias, bias_direction, accuracy_rating, period_count", () => {
    const s = loadAnalysis().summary
    expect(s).toHaveProperty("mape")
    expect(s).toHaveProperty("mean_bias")
    expect(s).toHaveProperty("bias_direction")
    expect(s).toHaveProperty("accuracy_rating")
    expect(s).toHaveProperty("period_count")
  })

  test("MAPE is approximately 5.90 (average of 4 absolute pct errors)", () => {
    const mape = loadAnalysis().summary.mape
    expect(Math.abs(mape - 5.8998)).toBeLessThan(0.1)
  })

  test("accuracy_rating is 'Excellent' (MAPE < 10)", () => {
    expect(loadAnalysis().summary.accuracy_rating).toBe("Excellent")
  })

  test("mean_bias is approximately -2500 (under-forecast)", () => {
    const s = loadAnalysis().summary
    expect(Math.abs(s.mean_bias - (-2500))).toBeLessThan(10)
  })

  test("bias_direction is 'under_forecast' (mean_bias < 0)", () => {
    expect(loadAnalysis().summary.bias_direction).toBe("under_forecast")
  })
})

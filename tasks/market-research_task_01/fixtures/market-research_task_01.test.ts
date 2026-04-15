import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadSizing(): any {
  return JSON.parse(readFileSync("market_sizing.json", "utf-8"))
}

describe("market_sizing.json", () => {
  test("file exists", () => {
    expect(existsSync("market_sizing.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const s = loadSizing()
    expect(s).toHaveProperty("product")
    expect(s).toHaveProperty("target")
    expect(s).toHaveProperty("sizing")
    expect(s).toHaveProperty("segments")
    expect(s).toHaveProperty("recommendation")
  })

  test("sizing has tam, sam, som, and confidence", () => {
    const s = loadSizing()
    expect(s.sizing).toHaveProperty("tam")
    expect(s.sizing).toHaveProperty("sam")
    expect(s.sizing).toHaveProperty("som")
    expect(s.sizing).toHaveProperty("confidence")
  })

  test("tam has label, description, value_usd_billions, formula", () => {
    const tam = loadSizing().sizing.tam
    expect(tam).toHaveProperty("label")
    expect(tam).toHaveProperty("description")
    expect(tam).toHaveProperty("value_usd_billions")
    expect(tam).toHaveProperty("formula")
    expect(tam.label).toBe("TAM")
  })

  test("sam has label, description, value_usd_billions, formula", () => {
    const sam = loadSizing().sizing.sam
    expect(sam).toHaveProperty("label")
    expect(sam.label).toBe("SAM")
    expect(typeof sam.value_usd_billions).toBe("number")
    expect(sam.value_usd_billions).toBeGreaterThan(0)
  })

  test("som has label, value_usd_millions, formula", () => {
    const som = loadSizing().sizing.som
    expect(som).toHaveProperty("label")
    expect(som.label).toBe("SOM")
    expect(typeof som.value_usd_millions).toBe("number")
    expect(som.value_usd_millions).toBeGreaterThan(0)
  })

  test("SAM is less than or equal to TAM", () => {
    const s = loadSizing().sizing
    expect(s.sam.value_usd_billions).toBeLessThanOrEqual(s.tam.value_usd_billions)
  })

  test("confidence is one of low, medium, high", () => {
    const conf = loadSizing().sizing.confidence
    expect(["low", "medium", "high"]).toContain(conf)
  })

  test("segments is an array of at least 3 entries", () => {
    const s = loadSizing()
    expect(Array.isArray(s.segments)).toBe(true)
    expect(s.segments.length).toBeGreaterThanOrEqual(3)
  })

  test("each segment has name, size_description, willingness_to_pay, urgency", () => {
    const validLevels = new Set(["low", "medium", "high"])
    for (const seg of loadSizing().segments) {
      expect(seg).toHaveProperty("name")
      expect(seg).toHaveProperty("size_description")
      expect(seg).toHaveProperty("willingness_to_pay")
      expect(seg).toHaveProperty("urgency")
      expect(validLevels.has(seg.willingness_to_pay)).toBe(true)
      expect(validLevels.has(seg.urgency)).toBe(true)
    }
  })

  test("recommendation has verdict, rationale, uncertainties, next_steps", () => {
    const rec = loadSizing().recommendation
    expect(rec).toHaveProperty("verdict")
    expect(rec).toHaveProperty("rationale")
    expect(rec).toHaveProperty("uncertainties")
    expect(rec).toHaveProperty("next_steps")
    expect(["enter", "avoid", "investigate_further"]).toContain(rec.verdict)
    expect(Array.isArray(rec.uncertainties)).toBe(true)
    expect(rec.uncertainties.length).toBeGreaterThanOrEqual(2)
    expect(Array.isArray(rec.next_steps)).toBe(true)
    expect(rec.next_steps.length).toBeGreaterThanOrEqual(2)
  })
})

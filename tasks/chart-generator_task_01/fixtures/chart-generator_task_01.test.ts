import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync, statSync } from "fs"

function loadSVG(): string {
  return readFileSync("sales_chart.svg", "utf-8")
}

function loadMetadata(): any {
  return JSON.parse(readFileSync("chart_metadata.json", "utf-8"))
}

describe("sales_chart.svg", () => {
  test("file exists", () => {
    expect(existsSync("sales_chart.svg")).toBe(true)
  })

  test("file has non-trivial size (at least 200 bytes)", () => {
    const stat = statSync("sales_chart.svg")
    expect(stat.size).toBeGreaterThan(200)
  })

  test("is a valid SVG document", () => {
    const svg = loadSVG()
    expect(svg).toMatch(/<svg[\s>]|<\?xml/)
    expect(svg).toContain("</svg>")
  })

  test("contains rect elements for bars", () => {
    const svg = loadSVG()
    const rectMatches = svg.match(/<rect/gi) || []
    expect(rectMatches.length).toBeGreaterThanOrEqual(4)
  })

  test("contains quarter labels Q1 through Q4", () => {
    const svg = loadSVG()
    expect(svg).toContain("Q1")
    expect(svg).toContain("Q2")
    expect(svg).toContain("Q3")
    expect(svg).toContain("Q4")
  })

  test("contains a title or heading text", () => {
    const svg = loadSVG().toLowerCase()
    expect(svg).toMatch(/quarterly|sales/)
  })
})

describe("chart_metadata.json", () => {
  test("file exists", () => {
    expect(existsSync("chart_metadata.json")).toBe(true)
  })

  test("has required top-level keys", () => {
    const m = loadMetadata()
    expect(m).toHaveProperty("title")
    expect(m).toHaveProperty("chart_type")
    expect(m).toHaveProperty("data_points")
    expect(m).toHaveProperty("max_value")
    expect(m).toHaveProperty("min_value")
    expect(m).toHaveProperty("total")
  })

  test("title and chart_type are correct", () => {
    const m = loadMetadata()
    expect(m.title).toBe("Quarterly Sales")
    expect(m.chart_type).toBe("bar")
  })

  test("data_points array has 4 entries with correct values", () => {
    const m = loadMetadata()
    expect(Array.isArray(m.data_points)).toBe(true)
    expect(m.data_points.length).toBe(4)
    const values = m.data_points.map((d: any) => d.value).sort((a: number, b: number) => a - b)
    expect(values).toEqual([95, 120, 185, 210])
  })

  test("max_value, min_value, and total are correct", () => {
    const m = loadMetadata()
    expect(m.max_value).toBe(210)
    expect(m.min_value).toBe(95)
    expect(m.total).toBe(610)
  })
})

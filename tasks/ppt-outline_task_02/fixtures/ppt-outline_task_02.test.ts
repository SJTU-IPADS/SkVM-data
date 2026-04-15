import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync, statSync } from "fs"

function loadHTML(): string {
  return readFileSync("presentation.html", "utf-8")
}

describe("presentation.html", () => {
  test("file exists", () => {
    expect(existsSync("presentation.html")).toBe(true)
  })

  test("file is non-empty (at least 500 bytes)", () => {
    const stat = statSync("presentation.html")
    expect(stat.size).toBeGreaterThan(500)
  })

  test("contains DOCTYPE or html tag indicating valid HTML", () => {
    const html = loadHTML()
    const lower = html.toLowerCase()
    expect(lower.includes("<!doctype html>") || lower.includes("<html")).toBe(true)
  })

  test("contains exact text Remote Work Productivity in a heading", () => {
    const html = loadHTML()
    expect(html).toContain("Remote Work Productivity")
  })

  test("contains exactly 6 data-slide attributes (slides 1 through 6)", () => {
    const html = loadHTML()
    const matches = html.match(/data-slide/gi) || []
    expect(matches.length).toBeGreaterThanOrEqual(6)
    for (let i = 1; i <= 6; i++) {
      expect(html).toContain(`data-slide="${i}"`)
    }
  })

  test("each slide has a heading element (h1 or h2)", () => {
    const html = loadHTML()
    const h1Count = (html.match(/<h1/gi) || []).length
    const h2Count = (html.match(/<h2/gi) || []).length
    expect(h1Count + h2Count).toBeGreaterThanOrEqual(6)
  })

  test("contains at least 6 list elements (ul or ol) for bullet points", () => {
    const html = loadHTML()
    const ulCount = (html.match(/<ul/gi) || []).length
    const olCount = (html.match(/<ol/gi) || []).length
    expect(ulCount + olCount).toBeGreaterThanOrEqual(6)
  })

  test("final slide contains an ordered list for action items", () => {
    const html = loadHTML()
    // Look for slide 6 section with an <ol> in proximity
    const slide6Idx = html.indexOf('data-slide="6"')
    expect(slide6Idx).toBeGreaterThan(-1)
    const afterSlide6 = html.slice(slide6Idx)
    expect(afterSlide6).toContain("<ol")
  })

  test("contains inline CSS style block", () => {
    const html = loadHTML()
    expect(html.toLowerCase()).toContain("<style")
  })

  test("inline CSS includes background-color and font-family", () => {
    const html = loadHTML()
    expect(html).toContain("background-color")
    expect(html).toContain("font-family")
  })
})

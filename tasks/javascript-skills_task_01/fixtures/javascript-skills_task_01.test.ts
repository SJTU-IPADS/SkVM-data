import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadUtils(): string {
  return readFileSync("utils.js", "utf-8")
}

function loadDemoOutput(): string {
  return readFileSync("demo_output.txt", "utf-8")
}

describe("utils.js", () => {
  test("file exists", () => {
    expect(existsSync("utils.js")).toBe(true)
  })

  test("uses ES module export syntax", () => {
    const src = loadUtils()
    expect(src).toMatch(/export\s+(const|function|default)/)
    expect(src).not.toMatch(/module\.exports/)
    expect(src).not.toMatch(/require\(/)
  })

  test("does not use var declarations", () => {
    const src = loadUtils()
    expect(src).not.toMatch(/\bvar\b/)
  })

  test("uses single quotes for strings", () => {
    const src = loadUtils()
    // No double-quoted string literals (allow template literals and JSDoc)
    const doubleQuoted = src.match(/"[^"]*"/g) || []
    // Filter out JSDoc @param and comment strings — only count actual string literals
    const realDoubleQuotes = doubleQuoted.filter(s => !s.startsWith('"@') && s.length > 2)
    expect(realDoubleQuotes.length).toBe(0)
  })

  test("exports calculateAverage, formatCurrency, and groupBy", () => {
    const src = loadUtils()
    expect(src).toMatch(/calculateAverage/)
    expect(src).toMatch(/formatCurrency/)
    expect(src).toMatch(/groupBy/)
  })

  test("uses arrow functions for callbacks", () => {
    const src = loadUtils()
    expect(src).toMatch(/=>/)
  })

  test("uses reduce for calculateAverage or groupBy", () => {
    const src = loadUtils()
    expect(src).toMatch(/\.reduce\(/)
  })
})

describe("demo_output.txt", () => {
  test("file exists", () => {
    expect(existsSync("demo_output.txt")).toBe(true)
  })

  test("contains average line with value 25", () => {
    const out = loadDemoOutput()
    expect(out).toMatch(/average:\s*25/)
  })

  test("contains currency line with dollar sign and 1234", () => {
    const out = loadDemoOutput()
    expect(out).toMatch(/currency:.*\$.*1[,.]?234/)
  })

  test("contains groupBy line with keys a and b", () => {
    const out = loadDemoOutput()
    expect(out).toMatch(/groupBy:/)
    expect(out).toMatch(/"a"/)
    expect(out).toMatch(/"b"/)
  })
})

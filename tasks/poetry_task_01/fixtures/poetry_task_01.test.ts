import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadPoem(): any {
  return JSON.parse(readFileSync("poem.json", "utf-8"))
}

// Count Chinese characters only (CJK Unified Ideographs range)
function countChinese(s: string): number {
  return (s.match(/[\u4e00-\u9fff]/g) || []).length
}

describe("poem.json", () => {
  test("file exists", () => {
    expect(existsSync("poem.json")).toBe(true)
  })

  test("is valid JSON with required fields", () => {
    const p = loadPoem()
    expect(p).toHaveProperty("form")
    expect(p).toHaveProperty("theme")
    expect(p).toHaveProperty("title")
    expect(p).toHaveProperty("lines")
    expect(p).toHaveProperty("rhyme_char")
    expect(p).toHaveProperty("annotation")
  })

  test("form is 五言绝句", () => {
    const p = loadPoem()
    expect(p.form).toBe("五言绝句")
  })

  test("theme is 秋天", () => {
    const p = loadPoem()
    expect(p.theme).toBe("秋天")
  })

  test("lines is an array of exactly 4 elements", () => {
    const p = loadPoem()
    expect(Array.isArray(p.lines)).toBe(true)
    expect(p.lines.length).toBe(4)
  })

  test("each line contains exactly 5 Chinese characters", () => {
    const p = loadPoem()
    for (const line of p.lines) {
      expect(typeof line).toBe("string")
      expect(countChinese(line)).toBe(5)
    }
  })

  test("title is a non-empty string with at least 1 Chinese character", () => {
    const p = loadPoem()
    expect(typeof p.title).toBe("string")
    expect(countChinese(p.title)).toBeGreaterThanOrEqual(1)
  })

  test("rhyme_char is a non-empty string", () => {
    const p = loadPoem()
    expect(typeof p.rhyme_char).toBe("string")
    expect(p.rhyme_char.length).toBeGreaterThan(0)
  })

  test("annotation is a non-empty English string between 10 and 120 words", () => {
    const p = loadPoem()
    expect(typeof p.annotation).toBe("string")
    const wordCount = p.annotation.trim().split(/\s+/).length
    expect(wordCount).toBeGreaterThanOrEqual(10)
    expect(wordCount).toBeLessThanOrEqual(120)
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadCollection(): any {
  return JSON.parse(readFileSync("ci_collection.json", "utf-8"))
}

function countChinese(s: string): number {
  return (s.match(/[\u4e00-\u9fff]/g) || []).length
}

describe("ci_collection.json", () => {
  test("file exists", () => {
    expect(existsSync("ci_collection.json")).toBe(true)
  })

  test("has pattern and poems fields", () => {
    const c = loadCollection()
    expect(c).toHaveProperty("pattern")
    expect(c).toHaveProperty("poems")
    expect(Array.isArray(c.poems)).toBe(true)
  })

  test("pattern is 临江仙", () => {
    const c = loadCollection()
    expect(c.pattern).toBe("临江仙")
  })

  test("poems array has exactly 3 entries", () => {
    const c = loadCollection()
    expect(c.poems.length).toBe(3)
  })

  test("seasons are 春, 夏, 冬 in order", () => {
    const c = loadCollection()
    expect(c.poems[0].season).toBe("春")
    expect(c.poems[1].season).toBe("夏")
    expect(c.poems[2].season).toBe("冬")
  })

  test("each poem has title, stanza1, stanza2, annotation", () => {
    const c = loadCollection()
    for (const poem of c.poems) {
      expect(poem).toHaveProperty("title")
      expect(poem).toHaveProperty("stanza1")
      expect(poem).toHaveProperty("stanza2")
      expect(poem).toHaveProperty("annotation")
    }
  })

  test("each poem has exactly 6 lines per stanza", () => {
    const c = loadCollection()
    for (const poem of c.poems) {
      expect(Array.isArray(poem.stanza1)).toBe(true)
      expect(poem.stanza1.length).toBe(6)
      expect(Array.isArray(poem.stanza2)).toBe(true)
      expect(poem.stanza2.length).toBe(6)
    }
  })

  test("all stanza lines are non-empty strings with at least 1 Chinese character", () => {
    const c = loadCollection()
    for (const poem of c.poems) {
      for (const line of [...poem.stanza1, ...poem.stanza2]) {
        expect(typeof line).toBe("string")
        expect(countChinese(line)).toBeGreaterThanOrEqual(1)
      }
    }
  })

  test("each annotation is a non-empty English string", () => {
    const c = loadCollection()
    for (const poem of c.poems) {
      expect(typeof poem.annotation).toBe("string")
      expect(poem.annotation.trim().length).toBeGreaterThan(10)
    }
  })
})

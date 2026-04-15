import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadStats(): any {
  return JSON.parse(readFileSync("stats.json", "utf-8"))
}

function loadScript(): string {
  return readFileSync("text_stats.py", "utf-8")
}

// Expected values for sample.txt:
// Line 1: "The quick brown fox jumps over the lazy dog"   (9 words)
// Line 2: "The dog barked at the fox"                     (6 words)
// Line 3: "A quick brown fox is a clever fox"             (8 words)
// Line 4: "The lazy dog slept all day"                    (6 words)
// Total words: 29, lines: 4
// char_count: exact character count including newlines
// unique_words: case-insensitive distinct alpha words
// top 5 words: the(5), fox(4), dog(3), quick(2), brown(2) — or similar ordering for ties

describe("stats.json", () => {
  test("file exists", () => {
    expect(existsSync("stats.json")).toBe(true)
  })

  test("has all required fields", () => {
    const s = loadStats()
    expect(s).toHaveProperty("char_count")
    expect(s).toHaveProperty("word_count")
    expect(s).toHaveProperty("line_count")
    expect(s).toHaveProperty("unique_words")
    expect(s).toHaveProperty("avg_word_length")
    expect(s).toHaveProperty("top_words")
  })

  test("word_count is 29", () => {
    const s = loadStats()
    expect(s.word_count).toBe(29)
  })

  test("line_count is 4", () => {
    const s = loadStats()
    expect(s.line_count).toBe(4)
  })

  test("char_count is a positive integer greater than 100", () => {
    const s = loadStats()
    expect(typeof s.char_count).toBe("number")
    expect(s.char_count).toBeGreaterThan(100)
    expect(Number.isInteger(s.char_count)).toBe(true)
  })

  test("unique_words is between 15 and 25", () => {
    const s = loadStats()
    expect(typeof s.unique_words).toBe("number")
    expect(s.unique_words).toBeGreaterThanOrEqual(15)
    expect(s.unique_words).toBeLessThanOrEqual(25)
  })

  test("avg_word_length is a positive float rounded to 2 decimal places", () => {
    const s = loadStats()
    expect(typeof s.avg_word_length).toBe("number")
    expect(s.avg_word_length).toBeGreaterThan(2)
    expect(s.avg_word_length).toBeLessThan(10)
    // Check it is rounded to 2 decimal places
    expect(s.avg_word_length).toBe(Math.round(s.avg_word_length * 100) / 100)
  })

  test("top_words is an array of exactly 5 objects", () => {
    const s = loadStats()
    expect(Array.isArray(s.top_words)).toBe(true)
    expect(s.top_words.length).toBe(5)
  })

  test("each top_words entry has word and count fields", () => {
    const s = loadStats()
    for (const entry of s.top_words) {
      expect(entry).toHaveProperty("word")
      expect(entry).toHaveProperty("count")
      expect(typeof entry.word).toBe("string")
      expect(typeof entry.count).toBe("number")
    }
  })

  test("top_words is sorted descending by count", () => {
    const s = loadStats()
    for (let i = 0; i < s.top_words.length - 1; i++) {
      expect(s.top_words[i].count).toBeGreaterThanOrEqual(s.top_words[i + 1].count)
    }
  })

  test("the most frequent word is 'the' with count 5", () => {
    const s = loadStats()
    const topWord = s.top_words[0]
    expect(topWord.word.toLowerCase()).toBe("the")
    expect(topWord.count).toBe(5)
  })
})

describe("text_stats.py", () => {
  test("script file exists", () => {
    expect(existsSync("text_stats.py")).toBe(true)
  })

  test("script uses argparse", () => {
    const src = loadScript()
    expect(src).toContain("argparse")
  })

  test("script defines --input, --output, --top-words arguments", () => {
    const src = loadScript()
    expect(src).toContain("--input")
    expect(src).toContain("--output")
    expect(src).toContain("--top-words")
  })

  test("script contains main() function", () => {
    const src = loadScript()
    expect(src).toContain("def main(")
  })
})

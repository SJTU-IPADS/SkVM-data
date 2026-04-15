import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadVocab(): string {
  return readFileSync("memory/vocabulary.md", "utf-8")
}

function loadSummary(): any {
  return JSON.parse(readFileSync("words_summary.json", "utf-8"))
}

describe("memory/vocabulary.md", () => {
  test("file exists", () => {
    expect(existsSync("memory/vocabulary.md")).toBe(true)
  })

  test("Quiz State section present", () => {
    const content = loadVocab()
    expect(content).toContain("## Quiz State")
    expect(content).toContain("Pending quiz")
  })

  test("Active Words section present", () => {
    const content = loadVocab()
    expect(content).toContain("## Active Words")
  })

  test("contains 3 word entries using ### headers", () => {
    const content = loadVocab()
    const entries = content.match(/^### \w/gm) || []
    expect(entries.length).toBe(3)
  })

  test("ephemeral entry is present with correct fields", () => {
    const content = loadVocab()
    expect(content).toContain("### ephemeral")
    expect(content).toContain("**Type:** adjective")
    expect(content.toLowerCase()).toContain("ephemeral")
    expect(content).toContain("The Midnight Library")
  })

  test("cacophony entry is present with correct fields", () => {
    const content = loadVocab()
    expect(content).toContain("### cacophony")
    expect(content).toContain("**Type:** noun")
    expect(content).toContain("Page:")
  })

  test("sycophant entry is present with correct fields", () => {
    const content = loadVocab()
    expect(content).toContain("### sycophant")
    expect(content).toContain("**Type:** noun")
  })

  test("each entry has Pronunciation, Meaning, Synonyms, Context fields", () => {
    const content = loadVocab()
    expect(content).toContain("**Pronunciation:**")
    expect(content).toContain("**Meaning:**")
    expect(content).toContain("**Synonyms:**")
    expect(content).toContain("**Context:**")
  })

  test("file contains Long-Term Review Words and Mastered Words sections", () => {
    const content = loadVocab()
    expect(content).toContain("## Long-Term Review Words")
    expect(content).toContain("## Mastered Words")
  })

  test("section order: Quiz State before Active Words before Long-Term Review before Mastered", () => {
    const content = loadVocab()
    const quizIdx = content.indexOf("## Quiz State")
    const activeIdx = content.indexOf("## Active Words")
    const ltIdx = content.indexOf("## Long-Term Review Words")
    const masteredIdx = content.indexOf("## Mastered Words")
    expect(quizIdx).toBeLessThan(activeIdx)
    expect(activeIdx).toBeLessThan(ltIdx)
    expect(ltIdx).toBeLessThan(masteredIdx)
  })
})

describe("words_summary.json", () => {
  test("file exists", () => {
    expect(existsSync("words_summary.json")).toBe(true)
  })

  test("summary has words array and count 3", () => {
    const s = loadSummary()
    expect(s).toHaveProperty("words")
    expect(s).toHaveProperty("count")
    expect(Array.isArray(s.words)).toBe(true)
    expect(s.count).toBe(3)
    expect(s.words.length).toBe(3)
  })

  test("words array contains ephemeral, cacophony, sycophant", () => {
    const s = loadSummary()
    expect(s.words).toContain("ephemeral")
    expect(s.words).toContain("cacophony")
    expect(s.words).toContain("sycophant")
  })
})

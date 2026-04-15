import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

describe("transcript_alice.txt", () => {
  test("transcript_alice.txt exists", () => {
    expect(existsSync("transcript_alice.txt")).toBe(true)
  })

  test("alice transcript has content", () => {
    const text = readFileSync("transcript_alice.txt", "utf-8").trim()
    expect(text.length).toBeGreaterThan(20)
    const words = text.split(/\s+/)
    expect(words.length).toBeGreaterThanOrEqual(5)
  })
})

describe("transcript_bob.txt", () => {
  test("transcript_bob.txt exists", () => {
    expect(existsSync("transcript_bob.txt")).toBe(true)
  })

  test("bob transcript has content", () => {
    const text = readFileSync("transcript_bob.txt", "utf-8").trim()
    expect(text.length).toBeGreaterThan(20)
    const words = text.split(/\s+/)
    expect(words.length).toBeGreaterThanOrEqual(5)
  })
})

describe("meeting_notes.json", () => {
  test("meeting_notes.json exists", () => {
    expect(existsSync("meeting_notes.json")).toBe(true)
  })

  test("speakers array with 2 entries", () => {
    const data = JSON.parse(readFileSync("meeting_notes.json", "utf-8"))
    expect(Array.isArray(data.speakers)).toBe(true)
    expect(data.speakers.length).toBe(2)
    for (const speaker of data.speakers) {
      expect(typeof speaker.name).toBe("string")
      expect(speaker.name.length).toBeGreaterThan(0)
      expect(typeof speaker.word_count).toBe("number")
      expect(speaker.word_count).toBeGreaterThan(0)
    }
  })

  test("combined_transcript has speaker labels", () => {
    const data = JSON.parse(readFileSync("meeting_notes.json", "utf-8"))
    expect(typeof data.combined_transcript).toBe("string")
    expect(data.combined_transcript.length).toBeGreaterThan(50)
    // Should contain speaker attribution
    const lower = data.combined_transcript.toLowerCase()
    const hasLabels = lower.includes("alice") || lower.includes("bob") ||
                      lower.includes("speaker 1") || lower.includes("speaker 2")
    expect(hasLabels).toBe(true)
  })

  test("total_word_count is a positive number", () => {
    const data = JSON.parse(readFileSync("meeting_notes.json", "utf-8"))
    expect(typeof data.total_word_count).toBe("number")
    expect(data.total_word_count).toBeGreaterThan(10)
  })

  test("action_items has at least 2 entries", () => {
    const data = JSON.parse(readFileSync("meeting_notes.json", "utf-8"))
    expect(Array.isArray(data.action_items)).toBe(true)
    expect(data.action_items.length).toBeGreaterThanOrEqual(2)
    for (const item of data.action_items) {
      expect(typeof item).toBe("string")
      expect(item.length).toBeGreaterThan(5)
    }
  })

  test("topics_discussed has at least 2 entries", () => {
    const data = JSON.parse(readFileSync("meeting_notes.json", "utf-8"))
    expect(Array.isArray(data.topics_discussed)).toBe(true)
    expect(data.topics_discussed.length).toBeGreaterThanOrEqual(2)
    for (const topic of data.topics_discussed) {
      expect(typeof topic).toBe("string")
      expect(topic.length).toBeGreaterThan(5)
    }
  })
})

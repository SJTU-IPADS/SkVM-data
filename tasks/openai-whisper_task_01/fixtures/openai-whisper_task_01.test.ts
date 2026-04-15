import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

describe("transcript.txt", () => {
  test("transcript.txt exists", () => {
    expect(existsSync("transcript.txt")).toBe(true)
  })

  test("transcript has meaningful content", () => {
    const text = readFileSync("transcript.txt", "utf-8").trim()
    expect(text.length).toBeGreaterThan(20)
    const words = text.split(/\s+/)
    expect(words.length).toBeGreaterThanOrEqual(5)
    // Should contain at least some words related to the original text
    const lower = text.toLowerCase()
    const hasRelevantContent =
      lower.includes("artificial") ||
      lower.includes("intelligence") ||
      lower.includes("software") ||
      lower.includes("machine") ||
      lower.includes("learning") ||
      lower.includes("code") ||
      lower.includes("automate")
    expect(hasRelevantContent).toBe(true)
  })
})

describe("transcription_report.json", () => {
  test("transcription_report.json exists", () => {
    expect(existsSync("transcription_report.json")).toBe(true)
  })

  test("has source_text, audio_file, transcript fields", () => {
    const data = JSON.parse(readFileSync("transcription_report.json", "utf-8"))
    expect(typeof data.source_text).toBe("string")
    expect(data.source_text.length).toBeGreaterThan(10)
    expect(typeof data.audio_file).toBe("string")
    expect(data.audio_file.length).toBeGreaterThan(0)
    expect(typeof data.transcript).toBe("string")
    expect(data.transcript.length).toBeGreaterThan(10)
  })

  test("word_count is a positive number", () => {
    const data = JSON.parse(readFileSync("transcription_report.json", "utf-8"))
    expect(typeof data.word_count).toBe("number")
    expect(data.word_count).toBeGreaterThan(0)
  })

  test("accuracy_notes is at least 30 characters", () => {
    const data = JSON.parse(readFileSync("transcription_report.json", "utf-8"))
    expect(typeof data.accuracy_notes).toBe("string")
    expect(data.accuracy_notes.length).toBeGreaterThanOrEqual(30)
  })
})

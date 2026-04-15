import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadSchedule(): any {
  return JSON.parse(readFileSync("daily_schedule.json", "utf-8"))
}

function timeToMinutes(t: string): number {
  const [h, m] = t.split(":").map(Number)
  return h * 60 + m
}

const VALID_LEVELS = new Set(["high", "medium", "low"])

describe("daily_schedule.json", () => {
  test("file exists", () => {
    expect(existsSync("daily_schedule.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadSchedule()).not.toThrow()
  })

  test("required top-level fields exist", () => {
    const s = loadSchedule()
    expect(s).toHaveProperty("person")
    expect(s).toHaveProperty("date")
    expect(s).toHaveProperty("time_blocks")
    expect(s).toHaveProperty("energy_alignment_score")
    expect(s).toHaveProperty("productivity_notes")
  })

  test("date is 2026-04-11", () => {
    const s = loadSchedule()
    expect(s.date).toBe("2026-04-11")
  })

  test("time_blocks is a non-empty array", () => {
    const s = loadSchedule()
    expect(Array.isArray(s.time_blocks)).toBe(true)
    expect(s.time_blocks.length).toBeGreaterThan(0)
  })

  test("each block has start, end, task, energy_level, and cognitive_load", () => {
    const s = loadSchedule()
    for (const block of s.time_blocks) {
      expect(block).toHaveProperty("start")
      expect(block).toHaveProperty("end")
      expect(block).toHaveProperty("task")
      expect(block).toHaveProperty("energy_level")
      expect(block).toHaveProperty("cognitive_load")
    }
  })

  test("energy_level values are valid (high, medium, or low)", () => {
    const s = loadSchedule()
    for (const block of s.time_blocks) {
      expect(VALID_LEVELS.has(block.energy_level)).toBe(true)
    }
  })

  test("cognitive_load values are valid (high, medium, or low)", () => {
    const s = loadSchedule()
    for (const block of s.time_blocks) {
      expect(VALID_LEVELS.has(block.cognitive_load)).toBe(true)
    }
  })

  test("bug fix task ends by 16:00 (4 PM)", () => {
    const s = loadSchedule()
    const bugBlocks = s.time_blocks.filter((b: any) =>
      b.task.toLowerCase().includes("bug") || b.task.toLowerCase().includes("fix")
    )
    expect(bugBlocks.length).toBeGreaterThan(0)
    for (const b of bugBlocks) {
      const endMinutes = timeToMinutes(b.end)
      expect(endMinutes).toBeLessThanOrEqual(16 * 60) // 16:00
    }
  })

  test("schedule starts at 09:00 or earlier and ends at 18:00 or later", () => {
    const s = loadSchedule()
    const starts = s.time_blocks.map((b: any) => timeToMinutes(b.start))
    const ends = s.time_blocks.map((b: any) => timeToMinutes(b.end))
    expect(Math.min(...starts)).toBeLessThanOrEqual(9 * 60) // 09:00
    expect(Math.max(...ends)).toBeGreaterThanOrEqual(18 * 60) // 18:00
  })

  test("energy_alignment_score is an integer between 0 and 10", () => {
    const s = loadSchedule()
    const score = s.energy_alignment_score
    expect(Number.isInteger(score)).toBe(true)
    expect(score).toBeGreaterThanOrEqual(0)
    expect(score).toBeLessThanOrEqual(10)
  })

  test("at least 2 productivity notes as non-empty strings", () => {
    const s = loadSchedule()
    expect(Array.isArray(s.productivity_notes)).toBe(true)
    expect(s.productivity_notes.length).toBeGreaterThanOrEqual(2)
    for (const note of s.productivity_notes) {
      expect(typeof note).toBe("string")
      expect(note.length).toBeGreaterThan(5)
    }
  })
})

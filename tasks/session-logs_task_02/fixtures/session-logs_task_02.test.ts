import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

const SESSION_FILES = ["session_a.jsonl", "session_b.jsonl", "session_c.jsonl"]

function loadJsonl(filename: string): string[] {
  return readFileSync(filename, "utf-8").trim().split("\n")
}

function loadReport(): any {
  return JSON.parse(readFileSync("cross_session_report.json", "utf-8"))
}

for (const file of SESSION_FILES) {
  describe(file, () => {
    test("file exists", () => {
      expect(existsSync(file)).toBe(true)
    })

    test("has at least 15 lines", () => {
      const lines = loadJsonl(file)
      expect(lines.length).toBeGreaterThanOrEqual(15)
    })

    test("each line is valid JSON", () => {
      const lines = loadJsonl(file)
      for (const line of lines) {
        expect(() => JSON.parse(line)).not.toThrow()
      }
    })

    test("messages have required fields", () => {
      const lines = loadJsonl(file)
      for (const line of lines) {
        const obj = JSON.parse(line)
        expect(obj).toHaveProperty("type")
        expect(obj).toHaveProperty("timestamp")
        expect(obj).toHaveProperty("message")
        expect(obj.message).toHaveProperty("role")
        expect(["user", "assistant", "toolResult"]).toContain(obj.message.role)
      }
    })
  })
}

describe("cross_session_report.json", () => {
  test("file exists", () => {
    expect(existsSync("cross_session_report.json")).toBe(true)
  })

  test("has sessions array with 3 entries", () => {
    const r = loadReport()
    expect(r).toHaveProperty("sessions")
    expect(Array.isArray(r.sessions)).toBe(true)
    expect(r.sessions.length).toBe(3)
    for (const s of r.sessions) {
      expect(s).toHaveProperty("filename")
      expect(s).toHaveProperty("message_count")
      expect(s).toHaveProperty("duration_minutes")
      expect(s).toHaveProperty("total_cost")
      expect(s).toHaveProperty("topic_keywords")
      expect(Array.isArray(s.topic_keywords)).toBe(true)
      expect(s.topic_keywords.length).toBeGreaterThan(0)
    }
  })

  test("total_messages and total_cost are valid", () => {
    const r = loadReport()
    expect(r.total_messages).toBeGreaterThanOrEqual(45)
    expect(r.total_cost).toBeGreaterThan(0)
  })

  test("most_expensive_session and longest_session are valid filenames", () => {
    const r = loadReport()
    expect(r.most_expensive_session).toBeTruthy()
    expect(r.longest_session).toBeTruthy()
    expect(SESSION_FILES).toContain(r.most_expensive_session)
    expect(SESSION_FILES).toContain(r.longest_session)
  })

  test("has tool_usage field", () => {
    const r = loadReport()
    expect(r).toHaveProperty("tool_usage")
    expect(typeof r.tool_usage).toBe("object")
  })
})

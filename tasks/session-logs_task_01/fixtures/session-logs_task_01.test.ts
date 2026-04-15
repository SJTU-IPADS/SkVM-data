import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadJsonl(): string[] {
  return readFileSync("session_data.jsonl", "utf-8").trim().split("\n")
}

function loadReport(): any {
  return JSON.parse(readFileSync("session_report.json", "utf-8"))
}

describe("session_data.jsonl", () => {
  test("file exists", () => {
    expect(existsSync("session_data.jsonl")).toBe(true)
  })

  test("has at least 30 lines", () => {
    const lines = loadJsonl()
    expect(lines.length).toBeGreaterThanOrEqual(30)
  })

  test("each line is valid JSON", () => {
    const lines = loadJsonl()
    for (const line of lines) {
      expect(() => JSON.parse(line)).not.toThrow()
    }
  })

  test("messages have required fields", () => {
    const lines = loadJsonl()
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

describe("session_report.json", () => {
  test("file exists", () => {
    expect(existsSync("session_report.json")).toBe(true)
  })

  test("has all required fields", () => {
    const r = loadReport()
    expect(r).toHaveProperty("total_messages")
    expect(r).toHaveProperty("user_messages")
    expect(r).toHaveProperty("assistant_messages")
    expect(r).toHaveProperty("duration_minutes")
    expect(r).toHaveProperty("total_cost")
    expect(r).toHaveProperty("avg_cost_per_response")
    expect(r).toHaveProperty("first_timestamp")
    expect(r).toHaveProperty("last_timestamp")
  })

  test("message counts are consistent", () => {
    const r = loadReport()
    expect(r.total_messages).toBeGreaterThanOrEqual(30)
    expect(r.user_messages).toBeGreaterThan(0)
    expect(r.assistant_messages).toBeGreaterThan(0)
    expect(r.user_messages + r.assistant_messages).toBeLessThanOrEqual(r.total_messages)
  })

  test("duration_minutes is positive", () => {
    const r = loadReport()
    expect(r.duration_minutes).toBeGreaterThan(0)
  })

  test("cost values are positive and consistent", () => {
    const r = loadReport()
    expect(r.total_cost).toBeGreaterThan(0)
    expect(r.avg_cost_per_response).toBeGreaterThan(0)
  })

  test("timestamps are valid ISO dates", () => {
    const r = loadReport()
    expect(new Date(r.first_timestamp).toISOString()).toBeTruthy()
    expect(new Date(r.last_timestamp).toISOString()).toBeTruthy()
    expect(new Date(r.first_timestamp).getTime()).toBeLessThanOrEqual(
      new Date(r.last_timestamp).getTime()
    )
  })
})

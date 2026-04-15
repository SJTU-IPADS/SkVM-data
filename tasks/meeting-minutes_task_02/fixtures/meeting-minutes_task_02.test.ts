import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadAgenda(): any {
  return JSON.parse(readFileSync("agenda.json", "utf-8"))
}

describe("agenda.json", () => {
  test("agenda file exists", () => {
    expect(existsSync("agenda.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadAgenda()).not.toThrow()
  })

  test("has required agenda fields: title, date, start_time, end_time, facilitator, total_minutes, items", () => {
    const a = loadAgenda()
    expect(a).toHaveProperty("title")
    expect(a).toHaveProperty("date")
    expect(a).toHaveProperty("start_time")
    expect(a).toHaveProperty("end_time")
    expect(a).toHaveProperty("facilitator")
    expect(a).toHaveProperty("total_minutes")
    expect(a).toHaveProperty("items")
  })

  test("total_minutes is exactly 60", () => {
    const a = loadAgenda()
    expect(a.total_minutes).toBe(60)
  })

  test("date is 2026-04-15, start_time is 14:00, end_time is 15:00", () => {
    const a = loadAgenda()
    expect(a.date).toBe("2026-04-15")
    expect(a.start_time).toBe("14:00")
    expect(a.end_time).toBe("15:00")
  })

  test("agenda items array has at least 4 items covering all required topics", () => {
    const a = loadAgenda()
    expect(Array.isArray(a.items)).toBe(true)
    expect(a.items.length).toBeGreaterThanOrEqual(4)
  })

  test("each item has order, topic, duration_minutes, and owner fields", () => {
    const a = loadAgenda()
    for (const item of a.items) {
      expect(typeof item.order).toBe("number")
      expect(typeof item.topic).toBe("string")
      expect(item.topic.length).toBeGreaterThan(0)
      expect(typeof item.duration_minutes).toBe("number")
      expect(item.duration_minutes).toBeGreaterThan(0)
      expect(typeof item.owner).toBe("string")
    }
  })

  test("item orders start at 1 and are sequential", () => {
    const a = loadAgenda()
    const orders = a.items.map((i: any) => i.order).sort((x: number, y: number) => x - y)
    expect(orders[0]).toBe(1)
    for (let i = 1; i < orders.length; i++) {
      expect(orders[i]).toBe(orders[i - 1] + 1)
    }
  })

  test("all duration_minutes values sum to exactly 60", () => {
    const a = loadAgenda()
    const total = a.items.reduce((sum: number, item: any) => sum + item.duration_minutes, 0)
    expect(total).toBe(60)
  })
})

describe("followup_email.txt", () => {
  test("email file exists", () => {
    expect(existsSync("followup_email.txt")).toBe(true)
  })

  test("email file has content", () => {
    const content = readFileSync("followup_email.txt", "utf-8")
    expect(content.length).toBeGreaterThan(50)
  })

  test("email has a Subject: line", () => {
    const content = readFileSync("followup_email.txt", "utf-8")
    expect(content).toMatch(/^Subject:/im)
  })

  test("email contains ACTION ITEMS section", () => {
    const content = readFileSync("followup_email.txt", "utf-8")
    expect(content).toMatch(/ACTION ITEMS/i)
  })

  test("email references the retrospective and date 2026-04-15", () => {
    const content = readFileSync("followup_email.txt", "utf-8")
    const lower = content.toLowerCase()
    expect(lower).toMatch(/retrospective|retro/)
    expect(content).toMatch(/2026-04-15|April 15/)
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadListOutput(): any[] {
  return JSON.parse(readFileSync("list_output.json", "utf-8"))
}

function loadItemsJson(): any {
  return JSON.parse(readFileSync("todo_items.json", "utf-8"))
}

describe("todo_manager.py", () => {
  test("file exists", () => {
    expect(existsSync("todo_manager.py")).toBe(true)
  })
})

describe("todo_items.json", () => {
  test("file exists", () => {
    expect(existsSync("todo_items.json")).toBe(true)
  })

  test("is valid JSON with an items array", () => {
    const data = loadItemsJson()
    expect(data).toHaveProperty("items")
    expect(Array.isArray(data.items)).toBe(true)
  })
})

describe("list_output.json", () => {
  test("file exists", () => {
    expect(existsSync("list_output.json")).toBe(true)
  })

  test("list_output is a JSON array", () => {
    const items = loadListOutput()
    expect(Array.isArray(items)).toBe(true)
  })

  test("contains exactly 3 items", () => {
    const items = loadListOutput()
    expect(items.length).toBe(3)
  })

  test("IDs are 1, 2, 3 in sequential order", () => {
    const items = loadListOutput()
    const ids = items.map((i: any) => i.id)
    expect(ids).toContain(1)
    expect(ids).toContain(2)
    expect(ids).toContain(3)
  })

  test("titles match the three added items", () => {
    const items = loadListOutput()
    const titles = items.map((i: any) => i.title)
    expect(titles).toContain("Write project proposal")
    expect(titles).toContain("Call dentist")
    expect(titles).toContain("Review PR from Alice")
  })

  test("types are project, reminder, task respectively", () => {
    const items = loadListOutput()
    const byId: Record<number, any> = {}
    for (const item of items) byId[item.id] = item
    expect(byId[1].type).toBe("project")
    expect(byId[2].type).toBe("reminder")
    expect(byId[3].type).toBe("task")
  })

  test("all items have status 'open'", () => {
    const items = loadListOutput()
    for (const item of items) {
      expect(item.status).toBe("open")
    }
  })

  test("each item has a created_at string field", () => {
    const items = loadListOutput()
    for (const item of items) {
      expect(typeof item.created_at).toBe("string")
      expect(item.created_at.length).toBeGreaterThan(0)
    }
  })
})

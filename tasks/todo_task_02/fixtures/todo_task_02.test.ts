import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadTasks(): any {
  return JSON.parse(readFileSync("tasks.json", "utf-8"))
}

function loadWhatNext(): any {
  return JSON.parse(readFileSync("what_next_output.json", "utf-8"))
}

describe("todo_ops.py", () => {
  test("file exists", () => {
    expect(existsSync("todo_ops.py")).toBe(true)
  })
})

describe("tasks.json", () => {
  test("file exists", () => {
    expect(existsSync("tasks.json")).toBe(true)
  })

  test("tasks.json has 4 items total", () => {
    const data = loadTasks()
    expect(Array.isArray(data.items)).toBe(true)
    expect(data.items.length).toBe(4)
  })

  test("item 1 has status 'done' after complete command", () => {
    const data = loadTasks()
    const item1 = data.items.find((i: any) => i.id === 1)
    expect(item1).toBeDefined()
    expect(item1.status).toBe("done")
  })

  test("items 2, 3, and 4 are still open", () => {
    const data = loadTasks()
    for (const id of [2, 3, 4]) {
      const item = data.items.find((i: any) => i.id === id)
      expect(item).toBeDefined()
      expect(item.status).toBe("open")
    }
  })

  test("item 1 title is 'Fix login bug'", () => {
    const data = loadTasks()
    const item1 = data.items.find((i: any) => i.id === 1)
    expect(item1.title).toBe("Fix login bug")
  })
})

describe("what_next_output.json", () => {
  test("file exists", () => {
    expect(existsSync("what_next_output.json")).toBe(true)
  })

  test("what_next_output is valid JSON object", () => {
    const n = loadWhatNext()
    expect(typeof n).toBe("object")
    expect(n).not.toBeNull()
  })

  test("what_next title is 'Prepare demo slides'", () => {
    const n = loadWhatNext()
    expect(n.title).toBe("Prepare demo slides")
  })

  test("what_next priority is 2", () => {
    const n = loadWhatNext()
    expect(n.priority).toBe(2)
  })

  test("what_next status is 'open'", () => {
    const n = loadWhatNext()
    expect(n.status).toBe("open")
  })
})

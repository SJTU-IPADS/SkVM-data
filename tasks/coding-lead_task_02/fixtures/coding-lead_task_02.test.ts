import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadOutput(): any {
  return JSON.parse(readFileSync("output.json", "utf-8"))
}

describe("refactored source files", () => {
  test("models.py exists", () => {
    expect(existsSync("models.py")).toBe(true)
  })

  test("pipeline.py exists", () => {
    expect(existsSync("pipeline.py")).toBe(true)
  })

  test("main.py exists", () => {
    expect(existsSync("main.py")).toBe(true)
  })

  test("models.py defines DataItem dataclass", () => {
    const src = readFileSync("models.py", "utf-8")
    expect(src).toContain("DataItem")
    expect(src).toContain("dataclass")
  })

  test("models.py defines ProcessedItem dataclass", () => {
    const src = readFileSync("models.py", "utf-8")
    expect(src).toContain("ProcessedItem")
  })

  test("pipeline.py defines DataPipeline class with required methods", () => {
    const src = readFileSync("pipeline.py", "utf-8")
    expect(src).toContain("class DataPipeline")
    expect(src).toContain("def load")
    expect(src).toContain("def process")
    expect(src).toContain("def save")
    expect(src).toContain("def run")
  })
})

describe("output.json", () => {
  test("file exists", () => {
    expect(existsSync("output.json")).toBe(true)
  })

  test("is array with 4 items", () => {
    const out = loadOutput()
    expect(Array.isArray(out)).toBe(true)
    expect(out.length).toBe(4)
  })

  test("each item has id, processed_value, status fields", () => {
    const out = loadOutput()
    for (const item of out) {
      expect(item).toHaveProperty("id")
      expect(item).toHaveProperty("processed_value")
      expect(item).toHaveProperty("status")
    }
  })

  test("item id=1 has processed_value=80 and status=done", () => {
    const out = loadOutput()
    const item = out.find((i: any) => i.id === 1)
    expect(item).toBeDefined()
    expect(item.processed_value).toBe(80)
    expect(item.status).toBe("done")
  })

  test("item id=2 has processed_value=100 (capped at 120)", () => {
    const out = loadOutput()
    const item = out.find((i: any) => i.id === 2)
    expect(item).toBeDefined()
    expect(item.processed_value).toBe(100)
    expect(item.status).toBe("done")
  })

  test("item id=3 is skipped with processed_value=0", () => {
    const out = loadOutput()
    const item = out.find((i: any) => i.id === 3)
    expect(item).toBeDefined()
    expect(item.processed_value).toBe(0)
    expect(item.status).toBe("skipped")
  })

  test("item id=4 has processed_value=100 (capped at 160)", () => {
    const out = loadOutput()
    const item = out.find((i: any) => i.id === 4)
    expect(item).toBeDefined()
    expect(item.processed_value).toBe(100)
    expect(item.status).toBe("done")
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadOutput(): any {
  return JSON.parse(readFileSync("pipeline_output.json", "utf-8"))
}

function loadPipeline(): string {
  return readFileSync("pipeline.js", "utf-8")
}

describe("pipeline.js", () => {
  test("file exists", () => {
    expect(existsSync("pipeline.js")).toBe(true)
  })

  test("uses class syntax for DataPipeline", () => {
    const src = loadPipeline()
    expect(src).toMatch(/class\s+DataPipeline/)
  })

  test("uses class syntax for PipelineError extending Error", () => {
    const src = loadPipeline()
    expect(src).toMatch(/class\s+PipelineError\s+extends\s+Error/)
  })

  test("uses async/await pattern", () => {
    const src = loadPipeline()
    expect(src).toMatch(/\basync\b/)
    expect(src).toMatch(/\bawait\b/)
  })

  test("uses try/catch for error handling", () => {
    const src = loadPipeline()
    expect(src).toMatch(/\btry\s*\{/)
    expect(src).toMatch(/\bcatch\b/)
  })

  test("uses Promise.all", () => {
    const src = loadPipeline()
    expect(src).toMatch(/Promise\.all/)
  })

  test("does not use var or prototype manipulation", () => {
    const src = loadPipeline()
    expect(src).not.toMatch(/\bvar\b/)
    expect(src).not.toMatch(/\.prototype\./)
  })
})

describe("pipeline_output.json", () => {
  test("file exists", () => {
    expect(existsSync("pipeline_output.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const o = loadOutput()
    expect(o).toHaveProperty("name")
    expect(o).toHaveProperty("processed")
    expect(o).toHaveProperty("stats")
  })

  test("name is test-pipeline", () => {
    const o = loadOutput()
    expect(o.name).toBe("test-pipeline")
  })

  test("processed array is [1, 2, 3] with nulls removed", () => {
    const o = loadOutput()
    expect(Array.isArray(o.processed)).toBe(true)
    expect(o.processed).toEqual([1, 2, 3])
  })

  test("stats has correct count and sum", () => {
    const o = loadOutput()
    expect(o.stats).toBeDefined()
    expect(Number(o.stats.count)).toBe(3)
    expect(Number(o.stats.sum)).toBe(6)
  })
})

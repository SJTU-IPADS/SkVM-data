import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadPatterns(): any {
  return JSON.parse(readFileSync("prompt_patterns.json", "utf-8"))
}

function loadFewShot(): any {
  return JSON.parse(readFileSync("fewshot_prompt.json", "utf-8"))
}

const REQUIRED_PATTERNS = new Set(["zero-shot", "few-shot", "chain-of-thought", "role-prompting", "structured-output"])
const VALID_OVERHEAD = new Set(["low", "medium", "high"])
const VALID_SENTIMENTS = new Set(["positive", "negative", "neutral"])

describe("prompt_patterns.json", () => {
  test("file exists", () => {
    expect(existsSync("prompt_patterns.json")).toBe(true)
  })

  test("is an array with exactly 5 pattern objects", () => {
    const d = loadPatterns()
    expect(Array.isArray(d)).toBe(true)
    expect(d.length).toBe(5)
  })

  test("all required pattern names are present", () => {
    const d = loadPatterns()
    const names = new Set(d.map((p: any) => p.pattern))
    for (const name of REQUIRED_PATTERNS) {
      expect(names.has(name)).toBe(true)
    }
  })

  test("each pattern has required fields", () => {
    const d = loadPatterns()
    for (const p of d) {
      expect(typeof p.pattern).toBe("string")
      expect(typeof p.best_for).toBe("string")
      expect(typeof p.token_overhead).toBe("string")
      expect(typeof p.requires_examples).toBe("boolean")
      expect(typeof p.output_format_controlled).toBe("boolean")
      expect(typeof p.example_trigger_phrase).toBe("string")
    }
  })

  test("token_overhead values are valid: low, medium, or high", () => {
    const d = loadPatterns()
    for (const p of d) {
      expect(VALID_OVERHEAD.has(p.token_overhead)).toBe(true)
    }
  })

  test("requires_examples is boolean for all patterns", () => {
    const d = loadPatterns()
    for (const p of d) {
      expect(typeof p.requires_examples).toBe("boolean")
    }
  })

  test("few-shot pattern has requires_examples = true", () => {
    const d = loadPatterns()
    const fewshot = d.find((p: any) => p.pattern === "few-shot")
    expect(fewshot).toBeDefined()
    expect(fewshot.requires_examples).toBe(true)
  })

  test("zero-shot pattern has requires_examples = false", () => {
    const d = loadPatterns()
    const zeroshot = d.find((p: any) => p.pattern === "zero-shot")
    expect(zeroshot).toBeDefined()
    expect(zeroshot.requires_examples).toBe(false)
  })

  test("example_trigger_phrase is a non-empty string for all patterns", () => {
    const d = loadPatterns()
    for (const p of d) {
      expect(p.example_trigger_phrase.length).toBeGreaterThan(3)
    }
  })
})

describe("fewshot_prompt.json", () => {
  test("file exists", () => {
    expect(existsSync("fewshot_prompt.json")).toBe(true)
  })

  test("has task_description, output_schema, examples, and instruction fields", () => {
    const d = loadFewShot()
    expect(d).toHaveProperty("task_description")
    expect(d).toHaveProperty("output_schema")
    expect(d).toHaveProperty("examples")
    expect(d).toHaveProperty("instruction")
  })

  test("examples is an array with at least 3 entries", () => {
    const d = loadFewShot()
    expect(Array.isArray(d.examples)).toBe(true)
    expect(d.examples.length).toBeGreaterThanOrEqual(3)
  })

  test("each example has input and output fields", () => {
    const d = loadFewShot()
    for (const ex of d.examples) {
      expect(ex).toHaveProperty("input")
      expect(ex).toHaveProperty("output")
      expect(ex.output).toHaveProperty("product_name")
      expect(ex.output).toHaveProperty("sentiment")
    }
  })

  test("all example sentiment values are valid: positive, negative, or neutral", () => {
    const d = loadFewShot()
    for (const ex of d.examples) {
      expect(VALID_SENTIMENTS.has(ex.output.sentiment)).toBe(true)
    }
  })

  test("covers all three sentiments: positive, negative, and neutral", () => {
    const d = loadFewShot()
    const sentiments = new Set(d.examples.map((ex: any) => ex.output.sentiment))
    expect(sentiments.has("positive")).toBe(true)
    expect(sentiments.has("negative")).toBe(true)
    expect(sentiments.has("neutral")).toBe(true)
  })

  test("instruction is a non-empty string", () => {
    const d = loadFewShot()
    expect(typeof d.instruction).toBe("string")
    expect(d.instruction.length).toBeGreaterThan(20)
  })
})

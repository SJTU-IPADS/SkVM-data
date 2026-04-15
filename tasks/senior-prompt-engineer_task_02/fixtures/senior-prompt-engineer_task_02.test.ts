import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadAgentConfig(): any {
  return JSON.parse(readFileSync("agent_config.json", "utf-8"))
}

function loadCostEstimate(): any {
  return JSON.parse(readFileSync("token_cost_estimate.json", "utf-8"))
}

describe("agent_config.json", () => {
  test("file exists", () => {
    expect(existsSync("agent_config.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const d = loadAgentConfig()
    expect(d).toHaveProperty("agent_name")
    expect(d).toHaveProperty("pattern")
    expect(d).toHaveProperty("max_iterations")
    expect(d).toHaveProperty("tools")
    expect(d).toHaveProperty("estimated_tokens_per_run")
    expect(d).toHaveProperty("system_prompt")
  })

  test("agent_name is 'research_assistant' and pattern is 'ReAct'", () => {
    const d = loadAgentConfig()
    expect(d.agent_name).toBe("research_assistant")
    expect(d.pattern).toBe("ReAct")
  })

  test("contains exactly 4 tools", () => {
    const d = loadAgentConfig()
    expect(Array.isArray(d.tools)).toBe(true)
    expect(d.tools.length).toBe(4)
  })

  test("each tool has required fields: name, requires_config, config_keys, description", () => {
    const d = loadAgentConfig()
    for (const tool of d.tools) {
      expect(typeof tool.name).toBe("string")
      expect(typeof tool.requires_config).toBe("boolean")
      expect(Array.isArray(tool.config_keys)).toBe(true)
      expect(typeof tool.description).toBe("string")
    }
  })

  test("web_search has api_key in config_keys and file_reader has allowed_paths", () => {
    const d = loadAgentConfig()
    const webSearch = d.tools.find((t: any) => t.name === "web_search")
    const fileReader = d.tools.find((t: any) => t.name === "file_reader")
    expect(webSearch).toBeDefined()
    expect(webSearch.config_keys).toContain("api_key")
    expect(fileReader).toBeDefined()
    expect(fileReader.config_keys).toContain("allowed_paths")
  })

  test("calculator and summarizer have requires_config = false", () => {
    const d = loadAgentConfig()
    const calc = d.tools.find((t: any) => t.name === "calculator")
    const summ = d.tools.find((t: any) => t.name === "summarizer")
    expect(calc).toBeDefined()
    expect(calc.requires_config).toBe(false)
    expect(summ).toBeDefined()
    expect(summ.requires_config).toBe(false)
  })

  test("system_prompt is at least 50 characters long", () => {
    const d = loadAgentConfig()
    expect(typeof d.system_prompt).toBe("string")
    expect(d.system_prompt.length).toBeGreaterThanOrEqual(50)
  })

  test("estimated_tokens_per_run has min and max fields as positive integers", () => {
    const d = loadAgentConfig()
    expect(d.estimated_tokens_per_run).toHaveProperty("min")
    expect(d.estimated_tokens_per_run).toHaveProperty("max")
    expect(d.estimated_tokens_per_run.min).toBeGreaterThan(0)
    expect(d.estimated_tokens_per_run.max).toBeGreaterThan(d.estimated_tokens_per_run.min)
  })
})

describe("token_cost_estimate.json", () => {
  test("file exists", () => {
    expect(existsSync("token_cost_estimate.json")).toBe(true)
  })

  test("has required cost fields", () => {
    const d = loadCostEstimate()
    expect(d).toHaveProperty("model")
    expect(d).toHaveProperty("input_price_per_1k")
    expect(d).toHaveProperty("output_price_per_1k")
    expect(d).toHaveProperty("estimated_input_tokens")
    expect(d).toHaveProperty("estimated_output_tokens")
    expect(d).toHaveProperty("estimated_cost_usd")
    expect(d).toHaveProperty("cost_formula")
  })

  test("model is 'gpt-4' and prices match the task specification", () => {
    const d = loadCostEstimate()
    expect(d.model).toBe("gpt-4")
    expect(d.input_price_per_1k).toBe(0.03)
    expect(d.output_price_per_1k).toBe(0.06)
  })

  test("token counts are within specified ranges", () => {
    const d = loadCostEstimate()
    expect(d.estimated_input_tokens).toBeGreaterThanOrEqual(1000)
    expect(d.estimated_input_tokens).toBeLessThanOrEqual(10000)
    expect(d.estimated_output_tokens).toBeGreaterThanOrEqual(200)
    expect(d.estimated_output_tokens).toBeLessThanOrEqual(3000)
  })

  test("estimated_cost_usd matches formula (rounded to 4 decimal places)", () => {
    const d = loadCostEstimate()
    const expected = Math.round(
      ((d.estimated_input_tokens / 1000) * 0.03 + (d.estimated_output_tokens / 1000) * 0.06) * 10000
    ) / 10000
    expect(Math.abs(d.estimated_cost_usd - expected)).toBeLessThan(0.0001)
  })

  test("cost_formula is a non-empty string", () => {
    const d = loadCostEstimate()
    expect(typeof d.cost_formula).toBe("string")
    expect(d.cost_formula.length).toBeGreaterThan(10)
  })
})

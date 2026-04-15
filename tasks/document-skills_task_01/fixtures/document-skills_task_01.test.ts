import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

const SKILL_PATH = "skills/validate-csv/SKILL.md"

function loadSkill(): string {
  return readFileSync(SKILL_PATH, "utf-8")
}

function extractFrontmatter(content: string): Record<string, string> {
  const match = content.match(/^---\n([\s\S]*?)\n---/)
  if (!match) return {}
  const fm: Record<string, string> = {}
  for (const line of match[1].split("\n")) {
    const kv = line.match(/^(\w[\w-]*):\s*(.*)$/)
    if (kv) fm[kv[1]] = kv[2].trim()
  }
  return fm
}

describe("skills/validate-csv/SKILL.md", () => {
  test("file exists", () => {
    expect(existsSync(SKILL_PATH)).toBe(true)
  })

  test("YAML frontmatter is delimited by --- lines", () => {
    const content = loadSkill()
    expect(content.startsWith("---")).toBe(true)
    const closingIndex = content.indexOf("---", 3)
    expect(closingIndex).toBeGreaterThan(3)
  })

  test("frontmatter name is exactly 'validate-csv'", () => {
    const fm = extractFrontmatter(loadSkill())
    expect(fm["name"]).toBe("validate-csv")
  })

  test("description has at least 50 characters", () => {
    const fm = extractFrontmatter(loadSkill())
    expect(typeof fm["description"]).toBe("string")
    expect(fm["description"].length).toBeGreaterThanOrEqual(50)
  })

  test("disable-model-invocation is true", () => {
    const content = loadSkill()
    expect(content).toMatch(/disable-model-invocation:\s*true/)
  })

  test("contains ## Inputs section", () => {
    const content = loadSkill()
    expect(content).toMatch(/^## Inputs/m)
  })

  test("contains ## Output section", () => {
    const content = loadSkill()
    expect(content).toMatch(/^## Output/m)
  })

  test("contains ## Process section", () => {
    const content = loadSkill()
    expect(content).toMatch(/^## Process/m)
  })

  test("Process section has at least 3 numbered steps", () => {
    const content = loadSkill()
    const processMatch = content.match(/^## Process([\s\S]*?)(?=^## |\Z)/m)
    expect(processMatch).not.toBeNull()
    const processBody = processMatch![1]
    const steps = processBody.match(/^\d+\./gm) || []
    expect(steps.length).toBeGreaterThanOrEqual(3)
  })

  test("file is under 300 lines", () => {
    const content = loadSkill()
    const lines = content.split("\n").length
    expect(lines).toBeLessThan(300)
  })
})

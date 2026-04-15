import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

const SKILL_PATH = "skills/slack-notify/SKILL.md"
const REF_PATH = "skills/slack-notify/references/api-patterns.md"

function loadSkill(): string {
  return readFileSync(SKILL_PATH, "utf-8")
}

function loadRef(): string {
  return readFileSync(REF_PATH, "utf-8")
}

function extractFrontmatter(content: string): Record<string, string> {
  const match = content.match(/^---\n([\s\S]*?)\n---/)
  if (!match) return {}
  const fm: Record<string, string> = {}
  for (const line of match[1].split("\n")) {
    const kv = line.match(/^([\w-]+):\s*(.*)$/)
    if (kv) fm[kv[1]] = kv[2].trim()
  }
  return fm
}

describe("skills/slack-notify/SKILL.md", () => {
  test("SKILL.md exists", () => {
    expect(existsSync(SKILL_PATH)).toBe(true)
  })

  test("frontmatter name is exactly 'slack-notify'", () => {
    const fm = extractFrontmatter(loadSkill())
    expect(fm["name"]).toBe("slack-notify")
  })

  test("description is at least 80 characters", () => {
    const fm = extractFrontmatter(loadSkill())
    expect(fm["description"].length).toBeGreaterThanOrEqual(80)
  })

  test("argument-hint contains '[channel]' and '[message]'", () => {
    const fm = extractFrontmatter(loadSkill())
    const hint = fm["argument-hint"] || ""
    expect(hint).toContain("[channel]")
    expect(hint).toContain("[message]")
  })

  test("disable-model-invocation is true", () => {
    expect(loadSkill()).toMatch(/disable-model-invocation:\s*true/)
  })

  test("Process section mentions api-patterns.md reference file", () => {
    const content = loadSkill()
    const processMatch = content.match(/^## Process([\s\S]*?)(?=^## |\Z)/m)
    expect(processMatch).not.toBeNull()
    expect(processMatch![1]).toMatch(/api-patterns\.md/)
  })

  test("Reference section contains a relative link to api-patterns.md", () => {
    const content = loadSkill()
    const refMatch = content.match(/^## Reference([\s\S]*?)(?=^## |\Z)/m)
    expect(refMatch).not.toBeNull()
    expect(refMatch![1]).toMatch(/api-patterns\.md/)
  })
})

describe("skills/slack-notify/references/api-patterns.md", () => {
  test("api-patterns.md exists", () => {
    expect(existsSync(REF_PATH)).toBe(true)
  })

  test("file is non-empty (at least 100 characters)", () => {
    expect(loadRef().length).toBeGreaterThan(100)
  })

  test("contains at least 2 fenced code blocks", () => {
    const content = loadRef()
    const blocks = content.match(/```/g) || []
    // Each block has an opening and closing ```, so 2 blocks = 4 occurrences
    expect(blocks.length).toBeGreaterThanOrEqual(4)
  })
})

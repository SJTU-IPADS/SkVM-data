import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

describe("ERRORS.md", () => {
  test("file exists", () => {
    expect(existsSync(".learnings/ERRORS.md")).toBe(true)
  })

  test("entry heading with NOVEL-ERR", () => {
    const content = readFileSync(".learnings/ERRORS.md", "utf-8")
    expect(content).toMatch(/##\s+\[NOVEL-ERR-/i)
  })

  test("contains Chapter 12 field", () => {
    const content = readFileSync(".learnings/ERRORS.md", "utf-8")
    expect(content).toContain("Chapter 12")
  })

  test("contains Severity field with a valid value", () => {
    const content = readFileSync(".learnings/ERRORS.md", "utf-8")
    expect(content).toMatch(/\*\*Severity\*\*:\s*(low|medium|high|critical)/i)
  })

  test("Problem Description section exists", () => {
    const content = readFileSync(".learnings/ERRORS.md", "utf-8")
    expect(content).toMatch(/###\s+Problem Description/i)
  })

  test("Correction Plan section exists", () => {
    const content = readFileSync(".learnings/ERRORS.md", "utf-8")
    expect(content).toMatch(/###\s+Correction Plan/i)
  })
})

describe("character_relationships.md", () => {
  test("file exists", () => {
    expect(existsSync("output/character_relationships.md")).toBe(true)
  })

  test("contains mermaid block", () => {
    const content = readFileSync("output/character_relationships.md", "utf-8")
    expect(content).toContain("```mermaid")
  })

  test("mentions all 4 characters", () => {
    const content = readFileSync("output/character_relationships.md", "utf-8")
    expect(content).toContain("Shen Yue")
    expect(content).toContain("Elder Cao")
    expect(content).toContain("Xu Peng")
    expect(content).toContain("Lin Rui")
  })

  test("at least 4 edges (arrows in mermaid)", () => {
    const content = readFileSync("output/character_relationships.md", "utf-8")
    // Count --> or --- edges in mermaid
    const arrows = (content.match(/-->/g) || []).length + (content.match(/---/g) || []).length
    expect(arrows).toBeGreaterThanOrEqual(4)
  })
})

describe("CHARACTERS.md", () => {
  test("file exists", () => {
    expect(existsSync(".learnings/CHARACTERS.md")).toBe(true)
  })

  test("contains all 4 characters", () => {
    const content = readFileSync(".learnings/CHARACTERS.md", "utf-8")
    expect(content).toContain("Shen Yue")
    expect(content).toContain("Elder Cao")
    expect(content).toContain("Xu Peng")
    expect(content).toContain("Lin Rui")
  })

  test("Elder Cao is marked as deceased", () => {
    const content = readFileSync(".learnings/CHARACTERS.md", "utf-8")
    expect(content).toMatch(/deceased/i)
  })
})

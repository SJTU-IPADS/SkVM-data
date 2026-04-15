import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadCharacters(): any {
  return JSON.parse(readFileSync("characters.json", "utf-8"))
}

function loadEpisode(): string {
  return readFileSync("episode_01.md", "utf-8")
}

function loadHookAnalysis(): any {
  return JSON.parse(readFileSync("hook_analysis.json", "utf-8"))
}

function countWords(text: string): number {
  return text.trim().split(/\s+/).filter(w => w.length > 0).length
}

const VALID_ROLES = new Set(["protagonist", "antagonist", "supporting"])
const VALID_HOOK_TYPES = new Set(["mystery", "conflict", "revelation", "cliffhanger"])

describe("characters.json", () => {
  test("file exists", () => {
    expect(existsSync("characters.json")).toBe(true)
  })

  test("is an array with exactly 3 characters", () => {
    const d = loadCharacters()
    expect(Array.isArray(d)).toBe(true)
    expect(d.length).toBe(3)
  })

  test("each character has required fields", () => {
    const d = loadCharacters()
    for (const c of d) {
      expect(typeof c.name).toBe("string")
      expect(typeof c.role).toBe("string")
      expect(typeof c.age).toBe("number")
      expect(Array.isArray(c.personality_traits)).toBe(true)
      expect(typeof c.motivation).toBe("string")
      expect(typeof c.conflict).toBe("string")
    }
  })

  test("character roles are valid and include protagonist", () => {
    const d = loadCharacters()
    const roles = d.map((c: any) => c.role)
    for (const role of roles) {
      expect(VALID_ROLES.has(role)).toBe(true)
    }
    expect(roles).toContain("protagonist")
  })

  test("each character has exactly 3 personality traits", () => {
    const d = loadCharacters()
    for (const c of d) {
      expect(c.personality_traits.length).toBe(3)
      for (const trait of c.personality_traits) {
        expect(typeof trait).toBe("string")
        expect(trait.length).toBeGreaterThan(0)
      }
    }
  })

  test("character ages are positive integers", () => {
    const d = loadCharacters()
    for (const c of d) {
      expect(c.age).toBeGreaterThan(0)
      expect(Number.isInteger(c.age)).toBe(true)
    }
  })

  test("motivation and conflict are non-empty strings", () => {
    const d = loadCharacters()
    for (const c of d) {
      expect(c.motivation.length).toBeGreaterThan(10)
      expect(c.conflict.length).toBeGreaterThan(10)
    }
  })
})

describe("episode_01.md", () => {
  test("file exists", () => {
    expect(existsSync("episode_01.md")).toBe(true)
  })

  test("has H1 title containing 'Episode 1'", () => {
    const text = loadEpisode()
    const h1Match = text.match(/^#\s+.+$/m)
    expect(h1Match).not.toBeNull()
    expect(h1Match![0].toLowerCase()).toContain("episode 1")
  })

  test("contains a SCENE: block", () => {
    const text = loadEpisode()
    expect(text).toContain("SCENE:")
  })

  test("contains at least 6 lines of dialogue in 'NAME: text' format", () => {
    const text = loadEpisode()
    // Match lines like "CHARACTER_NAME: some dialogue" — uppercase name at start of line
    const dialogueLines = text.match(/^[A-Z][A-Z\s_]{1,30}:\s+.+$/gm) || []
    expect(dialogueLines.length).toBeGreaterThanOrEqual(6)
  })

  test("contains [CLIFFHANGER] marker", () => {
    const text = loadEpisode()
    expect(text).toContain("[CLIFFHANGER]")
  })

  test("word count is between 150 and 400", () => {
    const text = loadEpisode()
    const words = countWords(text)
    expect(words).toBeGreaterThanOrEqual(150)
    expect(words).toBeLessThanOrEqual(400)
  })
})

describe("hook_analysis.json", () => {
  test("file exists", () => {
    expect(existsSync("hook_analysis.json")).toBe(true)
  })

  test("has required fields", () => {
    const d = loadHookAnalysis()
    expect(d).toHaveProperty("hook_type")
    expect(d).toHaveProperty("hook_description")
    expect(d).toHaveProperty("emotional_triggers")
    expect(d).toHaveProperty("target_audience")
    expect(d).toHaveProperty("episode_end_type")
  })

  test("hook_type is one of: mystery, conflict, revelation, cliffhanger", () => {
    const d = loadHookAnalysis()
    expect(VALID_HOOK_TYPES.has(d.hook_type)).toBe(true)
  })

  test("emotional_triggers is an array with at least 2 entries", () => {
    const d = loadHookAnalysis()
    expect(Array.isArray(d.emotional_triggers)).toBe(true)
    expect(d.emotional_triggers.length).toBeGreaterThanOrEqual(2)
    for (const trigger of d.emotional_triggers) {
      expect(typeof trigger).toBe("string")
    }
  })

  test("episode_end_type is 'cliffhanger'", () => {
    const d = loadHookAnalysis()
    expect(d.episode_end_type).toBe("cliffhanger")
  })

  test("hook_description is a non-empty string", () => {
    const d = loadHookAnalysis()
    expect(typeof d.hook_description).toBe("string")
    expect(d.hook_description.length).toBeGreaterThan(15)
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadSeriesPlan(): any {
  return JSON.parse(readFileSync("series_plan.json", "utf-8"))
}

function loadOutline(): any {
  return JSON.parse(readFileSync("episode_outline.json", "utf-8"))
}

function loadScene(): string {
  return readFileSync("key_scene.md", "utf-8")
}

describe("series_plan.json", () => {
  test("file exists", () => {
    expect(existsSync("series_plan.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const d = loadSeriesPlan()
    expect(d).toHaveProperty("title")
    expect(d).toHaveProperty("premise")
    expect(d).toHaveProperty("genre")
    expect(d).toHaveProperty("total_episodes")
    expect(d).toHaveProperty("structure")
    expect(d).toHaveProperty("acts")
  })

  test("total_episodes is 6 and structure is 'three-act'", () => {
    const d = loadSeriesPlan()
    expect(d.total_episodes).toBe(6)
    expect(d.structure).toBe("three-act")
  })

  test("acts array has exactly 3 acts with setup, confrontation, resolution labels", () => {
    const d = loadSeriesPlan()
    expect(Array.isArray(d.acts)).toBe(true)
    expect(d.acts.length).toBe(3)
    const labels = d.acts.map((a: any) => a.label)
    expect(labels).toContain("Setup")
    expect(labels).toContain("Confrontation")
    expect(labels).toContain("Resolution")
  })

  test("each act has act number, episodes array, label, and goal", () => {
    const d = loadSeriesPlan()
    for (const act of d.acts) {
      expect(typeof act.act).toBe("number")
      expect(Array.isArray(act.episodes)).toBe(true)
      expect(act.episodes.length).toBe(2)
      expect(typeof act.label).toBe("string")
      expect(typeof act.goal).toBe("string")
      expect(act.goal.length).toBeGreaterThan(10)
    }
  })

  test("acts cover episodes 1-6 without overlap", () => {
    const d = loadSeriesPlan()
    const allEps = d.acts.flatMap((a: any) => a.episodes).sort((x: number, y: number) => x - y)
    expect(allEps).toEqual([1, 2, 3, 4, 5, 6])
  })
})

describe("episode_outline.json", () => {
  test("file exists", () => {
    expect(existsSync("episode_outline.json")).toBe(true)
  })

  test("is an array with exactly 6 episode objects", () => {
    const d = loadOutline()
    expect(Array.isArray(d)).toBe(true)
    expect(d.length).toBe(6)
  })

  test("each episode has required fields", () => {
    const d = loadOutline()
    for (const ep of d) {
      expect(typeof ep.episode).toBe("number")
      expect(typeof ep.title).toBe("string")
      expect(typeof ep.hook).toBe("string")
      expect(typeof ep.conflict).toBe("string")
      expect(typeof ep.resolution).toBe("string")
      expect(typeof ep.cliffhanger).toBe("boolean")
    }
  })

  test("episode numbers are 1 through 6", () => {
    const d = loadOutline()
    const epNums = d.map((ep: any) => ep.episode).sort((a: number, b: number) => a - b)
    expect(epNums).toEqual([1, 2, 3, 4, 5, 6])
  })

  test("episodes 1-5 have cliffhanger=true and episode 6 has cliffhanger=false", () => {
    const d = loadOutline()
    const sorted = [...d].sort((a: any, b: any) => a.episode - b.episode)
    for (let i = 0; i < 5; i++) {
      expect(sorted[i].cliffhanger).toBe(true)
    }
    expect(sorted[5].cliffhanger).toBe(false)
  })

  test("hook, conflict, and resolution are non-empty strings", () => {
    const d = loadOutline()
    for (const ep of d) {
      expect(ep.hook.length).toBeGreaterThan(10)
      expect(ep.conflict.length).toBeGreaterThan(10)
      expect(ep.resolution.length).toBeGreaterThan(10)
    }
  })
})

describe("key_scene.md", () => {
  test("file exists", () => {
    expect(existsSync("key_scene.md")).toBe(true)
  })

  test("contains SCENE: location description", () => {
    const text = loadScene()
    expect(text).toContain("SCENE:")
  })

  test("contains at least 5 lines of dialogue in 'NAME: text' format", () => {
    const text = loadScene()
    const dialogueLines = text.match(/^[A-Z][A-Z\s_]{1,30}:\s+.+$/gm) || []
    expect(dialogueLines.length).toBeGreaterThanOrEqual(5)
  })

  test("contains at least one stage direction in parentheses", () => {
    const text = loadScene()
    const stageDirections = text.match(/\([^)]+\)/g) || []
    expect(stageDirections.length).toBeGreaterThanOrEqual(1)
  })

  test("contains [TO BE CONTINUED] tag", () => {
    const text = loadScene()
    expect(text).toContain("[TO BE CONTINUED]")
  })
})

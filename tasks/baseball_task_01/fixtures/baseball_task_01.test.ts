import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadStats(): any {
  return JSON.parse(readFileSync("player_stats.json", "utf-8"))
}

describe("player_stats.json", () => {
  test("file exists", () => {
    expect(existsSync("player_stats.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadStats()).not.toThrow()
  })

  test("has all required fields", () => {
    const s = loadStats()
    const requiredFields = [
      "player_id", "full_name", "position", "team",
      "jersey_number", "bats", "throws", "season",
      "stats_type", "games", "home_runs", "avg", "ops"
    ]
    for (const field of requiredFields) {
      expect(s).toHaveProperty(field)
    }
  })

  test("player_id is Aaron Judge's MLB ID 592450", () => {
    const s = loadStats()
    expect(s.player_id).toBe(592450)
  })

  test("full_name contains 'Judge'", () => {
    const s = loadStats()
    expect(s.full_name.toLowerCase()).toContain("judge")
  })

  test("team contains 'Yankees'", () => {
    const s = loadStats()
    expect(s.team.toLowerCase()).toContain("yankee")
  })

  test("position is a non-empty string", () => {
    const s = loadStats()
    expect(typeof s.position).toBe("string")
    expect(s.position.length).toBeGreaterThan(0)
  })

  test("season is a valid recent year (2020-2026)", () => {
    const s = loadStats()
    expect(typeof s.season).toBe("number")
    expect(s.season).toBeGreaterThanOrEqual(2020)
    expect(s.season).toBeLessThanOrEqual(2026)
  })

  test("stats_type is 'batting' or 'pitching'", () => {
    const s = loadStats()
    expect(["batting", "pitching"]).toContain(s.stats_type)
  })

  test("games is a positive integer", () => {
    const s = loadStats()
    expect(typeof s.games).toBe("number")
    expect(s.games).toBeGreaterThan(0)
  })

  test("home_runs is a non-negative integer", () => {
    const s = loadStats()
    expect(typeof s.home_runs).toBe("number")
    expect(s.home_runs).toBeGreaterThanOrEqual(0)
  })
})

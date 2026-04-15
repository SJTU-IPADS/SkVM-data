import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadSchedule(): any {
  return JSON.parse(readFileSync("schedule_summary.json", "utf-8"))
}

describe("schedule_summary.json", () => {
  test("file exists", () => {
    expect(existsSync("schedule_summary.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadSchedule()).not.toThrow()
  })

  test("has all required top-level fields", () => {
    const s = loadSchedule()
    expect(s).toHaveProperty("team")
    expect(s).toHaveProperty("team_id")
    expect(s).toHaveProperty("date_range")
    expect(s).toHaveProperty("games")
    expect(s).toHaveProperty("total_games")
    expect(s).toHaveProperty("home_games")
    expect(s).toHaveProperty("away_games")
  })

  test("team is New York Yankees and team_id is 147", () => {
    const s = loadSchedule()
    expect(s.team).toBe("New York Yankees")
    expect(s.team_id).toBe(147)
  })

  test("date_range has correct start and end", () => {
    const s = loadSchedule()
    expect(s.date_range).toHaveProperty("start")
    expect(s.date_range).toHaveProperty("end")
    expect(s.date_range.start).toBe("2025-09-15")
    expect(s.date_range.end).toBe("2025-09-21")
  })

  test("games is an array with at least one game", () => {
    const s = loadSchedule()
    expect(Array.isArray(s.games)).toBe(true)
    expect(s.games.length).toBeGreaterThanOrEqual(1)
  })

  test("each game has required fields: game_pk, date, home_team, away_team, venue, status", () => {
    const s = loadSchedule()
    for (const g of s.games) {
      expect(g).toHaveProperty("game_pk")
      expect(g).toHaveProperty("date")
      expect(g).toHaveProperty("home_team")
      expect(g).toHaveProperty("away_team")
      expect(g).toHaveProperty("venue")
      expect(g).toHaveProperty("status")
    }
  })

  test("game dates are within the 2025-09-15 to 2025-09-21 range", () => {
    const s = loadSchedule()
    for (const g of s.games) {
      expect(g.date >= "2025-09-15").toBe(true)
      expect(g.date <= "2025-09-21").toBe(true)
    }
  })

  test("total_games equals home_games plus away_games", () => {
    const s = loadSchedule()
    expect(s.total_games).toBe(s.home_games + s.away_games)
  })

  test("total_games matches the length of the games array", () => {
    const s = loadSchedule()
    expect(s.total_games).toBe(s.games.length)
  })

  test("all game_pk values are positive integers", () => {
    const s = loadSchedule()
    for (const g of s.games) {
      expect(typeof g.game_pk).toBe("number")
      expect(g.game_pk).toBeGreaterThan(0)
      expect(Number.isInteger(g.game_pk)).toBe(true)
    }
  })
})

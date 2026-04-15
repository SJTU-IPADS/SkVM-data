import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadReport(): any {
  return JSON.parse(readFileSync("slacking_report.json", "utf-8"))
}

describe("slacking_report.json", () => {
  test("file exists", () => {
    expect(existsSync("slacking_report.json")).toBe(true)
  })

  test("has all required keys", () => {
    const r = loadReport()
    expect(r).toHaveProperty("developer")
    expect(r).toHaveProperty("total_commits")
    expect(r).toHaveProperty("trivial_commit_count")
    expect(r).toHaveProperty("trivial_commit_ratio")
    expect(r).toHaveProperty("late_night_commits")
    expect(r).toHaveProperty("burst_days")
    expect(r).toHaveProperty("active_days")
    expect(r).toHaveProperty("slacking_index")
    expect(r).toHaveProperty("slacking_level")
  })

  test("developer name and total_commits are correct", () => {
    const r = loadReport()
    expect(r.developer).toBe("Carlos Mendez")
    expect(r.total_commits).toBe(20)
  })

  test("trivial_commit_count is 11", () => {
    const r = loadReport()
    // fix: commits 3,6,8,9,10,12,18 = 7 fix commits
    // chore: commits 7,19 = 2 chore commits
    // docs: commits 4,14 = 2 docs commits
    // Total trivial = 11
    expect(r.trivial_commit_count).toBe(11)
  })

  test("trivial_commit_ratio is 0.55 (11/20)", () => {
    const r = loadReport()
    expect(r.trivial_commit_ratio).toBe(0.55)
  })

  test("late_night_commits is 2 (commits at 23:45 and 00:05)", () => {
    const r = loadReport()
    expect(r.late_night_commits).toBe(2)
  })

  test("burst_days is 1 (March 10 has 4 commits)", () => {
    const r = loadReport()
    expect(r.burst_days).toBe(1)
  })

  test("active_days is 15", () => {
    const r = loadReport()
    // Distinct dates: Mar 2,3,4,5,6,10,11,12,15,20,21,22,23,29,30 = 15 distinct days
    expect(r.active_days).toBe(15)
  })

  test("slacking_index is a number between 0 and 100", () => {
    const r = loadReport()
    expect(typeof r.slacking_index).toBe("number")
    expect(r.slacking_index).toBeGreaterThanOrEqual(0)
    expect(r.slacking_index).toBeLessThanOrEqual(100)
  })

  test("slacking_level is a valid category string", () => {
    const r = loadReport()
    const validLevels = ["Workaholic", "Normal", "Suspicious", "Slacking Pro", "Slacking Master"]
    expect(validLevels).toContain(r.slacking_level)
  })
})

describe("compute_slacking.py", () => {
  test("script file exists", () => {
    expect(existsSync("compute_slacking.py")).toBe(true)
  })

  test("script uses only standard library (no pip imports for core logic)", () => {
    const content = readFileSync("compute_slacking.py", "utf-8")
    // Should not import gitpython, pydriller, pandas as core deps
    expect(content).not.toMatch(/from pydriller|import pydriller|import pandas/)
  })
})

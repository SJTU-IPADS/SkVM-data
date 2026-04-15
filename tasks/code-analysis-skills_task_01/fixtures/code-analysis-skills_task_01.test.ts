import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"
import { execSync } from "child_process"
import { join } from "path"

function loadReport(): any {
  return JSON.parse(readFileSync("developer_report.json", "utf-8"))
}

describe("analysis_repo", () => {
  test("directory exists", () => {
    expect(existsSync("analysis_repo")).toBe(true)
  })

  test("is a valid git repository", () => {
    expect(existsSync(join("analysis_repo", ".git"))).toBe(true)
  })

  test("has at least 8 commits", () => {
    const output = execSync("git log --oneline", { cwd: "analysis_repo", encoding: "utf-8" })
    const commitCount = output.trim().split("\n").filter(l => l.length > 0).length
    expect(commitCount).toBeGreaterThanOrEqual(8)
  })

  test("has commits from Alice Chen", () => {
    const output = execSync("git log --format=%ae", { cwd: "analysis_repo", encoding: "utf-8" })
    expect(output).toContain("alice@example.com")
  })

  test("has commits from Bob Smith", () => {
    const output = execSync("git log --format=%ae", { cwd: "analysis_repo", encoding: "utf-8" })
    expect(output).toContain("bob@example.com")
  })
})

describe("developer_report.json", () => {
  test("file exists", () => {
    expect(existsSync("developer_report.json")).toBe(true)
  })

  test("has all required top-level keys", () => {
    const r = loadReport()
    expect(r).toHaveProperty("repo_path")
    expect(r).toHaveProperty("total_commits")
    expect(r).toHaveProperty("developers")
    expect(r).toHaveProperty("top_contributor")
    expect(r).toHaveProperty("analysis_date")
  })

  test("total_commits is 8", () => {
    const r = loadReport()
    expect(r.total_commits).toBe(8)
  })

  test("developers array has 2 entries with required fields", () => {
    const r = loadReport()
    expect(Array.isArray(r.developers)).toBe(true)
    expect(r.developers.length).toBe(2)
    for (const dev of r.developers) {
      expect(typeof dev.name).toBe("string")
      expect(typeof dev.email).toBe("string")
      expect(typeof dev.commit_count).toBe("number")
      expect(typeof dev.files_changed).toBe("number")
      expect(["A", "B", "C", "D", "F"]).toContain(dev.grade)
    }
  })

  test("Alice has 5 commits and grade A", () => {
    const r = loadReport()
    const alice = r.developers.find((d: any) => d.name.toLowerCase().includes("alice") || d.email.includes("alice"))
    expect(alice).toBeDefined()
    expect(alice.commit_count).toBe(5)
    expect(alice.grade).toBe("A")
  })

  test("Bob has 3 commits and grade B", () => {
    const r = loadReport()
    const bob = r.developers.find((d: any) => d.name.toLowerCase().includes("bob") || d.email.includes("bob"))
    expect(bob).toBeDefined()
    expect(bob.commit_count).toBe(3)
    expect(bob.grade).toBe("B")
  })

  test("top_contributor is Alice", () => {
    const r = loadReport()
    expect(r.top_contributor.toLowerCase()).toContain("alice")
  })

  test("analysis_date is 2026-04-11", () => {
    const r = loadReport()
    expect(r.analysis_date).toBe("2026-04-11")
  })
})

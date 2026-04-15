import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadApiSpec(): any {
  return JSON.parse(readFileSync("api_spec.json", "utf-8"))
}

describe("task_plan.md", () => {
  test("file exists", () => {
    expect(existsSync("task_plan.md")).toBe(true)
  })

  test("Phase 3 is marked complete ([x])", () => {
    const content = readFileSync("task_plan.md", "utf-8")
    // Match [x] followed by content containing Phase 3
    expect(content).toMatch(/\[x\].*Phase 3/i)
  })

  test("phases 1 and 2 remain marked complete", () => {
    const content = readFileSync("task_plan.md", "utf-8")
    expect(content).toMatch(/\[x\].*Phase 1/i)
    expect(content).toMatch(/\[x\].*Phase 2/i)
  })

  test("phases 4 and 5 remain incomplete ([ ])", () => {
    const content = readFileSync("task_plan.md", "utf-8")
    expect(content).toMatch(/\[ \].*Phase 4/i)
    expect(content).toMatch(/\[ \].*Phase 5/i)
  })

  test("Decisions section preserved with task field names", () => {
    const content = readFileSync("task_plan.md", "utf-8")
    expect(content).toMatch(/id.*title.*status|status.*title.*id/i)
  })
})

describe("api_spec.json", () => {
  test("file exists", () => {
    expect(existsSync("api_spec.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadApiSpec()).not.toThrow()
  })

  test("has endpoints array", () => {
    const s = loadApiSpec()
    expect(s).toHaveProperty("endpoints")
    expect(Array.isArray(s.endpoints)).toBe(true)
  })

  test("exactly 2 endpoints", () => {
    const s = loadApiSpec()
    expect(s.endpoints.length).toBe(2)
  })

  test("GET /tasks and GET /tasks/:id are present", () => {
    const s = loadApiSpec()
    const paths = s.endpoints.map((e: any) => e.path)
    expect(paths).toContain("/tasks")
    expect(paths).toContain("/tasks/:id")
    for (const e of s.endpoints) {
      expect(e.method).toBe("GET")
    }
  })

  test("each endpoint has method, path, and description", () => {
    const s = loadApiSpec()
    for (const e of s.endpoints) {
      expect(e).toHaveProperty("method")
      expect(e).toHaveProperty("path")
      expect(e).toHaveProperty("description")
      expect(typeof e.description).toBe("string")
      expect(e.description.length).toBeGreaterThan(5)
    }
  })

  test("response schemas include all 4 task fields (id, title, status, created_at)", () => {
    const s = loadApiSpec()
    const specStr = JSON.stringify(s)
    expect(specStr).toContain("id")
    expect(specStr).toContain("title")
    expect(specStr).toContain("status")
    expect(specStr).toContain("created_at")
  })

  test("GET /tasks/:id endpoint includes a 404 response", () => {
    const s = loadApiSpec()
    const byId = s.endpoints.find((e: any) => e.path === "/tasks/:id")
    expect(byId).toBeDefined()
    expect(byId).toHaveProperty("response_404")
  })
})

describe("progress.md", () => {
  test("file exists", () => {
    expect(existsSync("progress.md")).toBe(true)
  })

  test("progress.md has at least one timestamped entry", () => {
    const content = readFileSync("progress.md", "utf-8")
    const entries = content.match(/\[\d{4}-\d{2}-\d{2}/g) || []
    expect(entries.length).toBeGreaterThanOrEqual(1)
  })

  test("progress entry mentions Phase 3 completion", () => {
    const content = readFileSync("progress.md", "utf-8")
    expect(content).toMatch(/phase 3|Phase 3/i)
  })
})

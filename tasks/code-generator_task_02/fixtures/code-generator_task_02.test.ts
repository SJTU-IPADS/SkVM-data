import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"
import { execSync } from "child_process"

function loadSpec(): any {
  return JSON.parse(readFileSync("api_spec.json", "utf-8"))
}

describe("api_handler.py", () => {
  test("file exists", () => {
    expect(existsSync("api_handler.py")).toBe(true)
  })

  test("contains TaskAPIHandler class", () => {
    const content = readFileSync("api_handler.py", "utf-8")
    expect(content).toMatch(/class TaskAPIHandler/)
  })

  test("contains TASKS module-level list", () => {
    const content = readFileSync("api_handler.py", "utf-8")
    expect(content).toMatch(/TASKS\s*=\s*\[/)
  })

  test("handles all 4 routes", () => {
    const content = readFileSync("api_handler.py", "utf-8")
    expect(content).toMatch(/\/tasks/)
    expect(content).toMatch(/\/health/)
    expect(content).toMatch(/do_GET|do_POST/)
  })

  test("is importable with no errors", () => {
    const result = execSync(
      "python3 -c \"from api_handler import TaskAPIHandler, TASKS; print('PASS')\"",
      { encoding: "utf-8" }
    ).trim()
    expect(result).toBe("PASS")
  })

  test("TASKS starts as an empty list", () => {
    const result = execSync(
      "python3 -c \"from api_handler import TASKS; assert TASKS == [], f'Expected [], got {TASKS}'; print('PASS')\"",
      { encoding: "utf-8" }
    ).trim()
    expect(result).toBe("PASS")
  })
})

describe("api_spec.json", () => {
  test("file exists", () => {
    expect(existsSync("api_spec.json")).toBe(true)
  })

  test("has all required top-level keys", () => {
    const s = loadSpec()
    expect(s).toHaveProperty("api_name")
    expect(s).toHaveProperty("language")
    expect(s).toHaveProperty("framework")
    expect(s).toHaveProperty("endpoints")
    expect(s).toHaveProperty("storage")
    expect(s).toHaveProperty("response_format")
  })

  test("fixed fields have correct values", () => {
    const s = loadSpec()
    expect(s.api_name).toBe("Task API")
    expect(s.language).toBe("python")
    expect(s.storage).toBe("in-memory")
    expect(s.response_format).toBe("JSON")
  })

  test("endpoints array has 4 entries with method, path, description", () => {
    const s = loadSpec()
    expect(Array.isArray(s.endpoints)).toBe(true)
    expect(s.endpoints.length).toBe(4)
    for (const ep of s.endpoints) {
      expect(typeof ep.method).toBe("string")
      expect(typeof ep.path).toBe("string")
      expect(typeof ep.description).toBe("string")
      expect(ep.path.startsWith("/")).toBe(true)
    }
  })

  test("endpoints include GET and POST methods", () => {
    const s = loadSpec()
    const methods = s.endpoints.map((e: any) => e.method.toUpperCase())
    expect(methods).toContain("GET")
    expect(methods).toContain("POST")
  })
})

describe("test_api.py", () => {
  test("file exists", () => {
    expect(existsSync("test_api.py")).toBe(true)
  })

  test("contains at least 3 test methods", () => {
    const content = readFileSync("test_api.py", "utf-8")
    const testMethods = content.match(/def test_\w+/g) || []
    expect(testMethods.length).toBeGreaterThanOrEqual(3)
  })

  test("all api tests pass", () => {
    const result = execSync(
      "python3 -m unittest test_api.py -v 2>&1 || true",
      { encoding: "utf-8" }
    )
    expect(result).toMatch(/OK/)
    expect(result).not.toMatch(/FAILED/)
  })
})

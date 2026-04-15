import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadResult(): any {
  return JSON.parse(readFileSync("scan_result.json", "utf-8"))
}

function loadScript(): string {
  return readFileSync("scan.js", "utf-8")
}

describe("scan.js", () => {
  test("file exists", () => {
    expect(existsSync("scan.js")).toBe(true)
  })

  test("does not use network APIs or child_process", () => {
    const src = loadScript()
    expect(src).not.toMatch(/fetch\(|http\.|https\.|WebSocket|child_process|exec\(|spawn\(/)
  })

  test("reads from sessions directory", () => {
    const src = loadScript()
    expect(src).toMatch(/sessions/)
  })
})

describe("scan_result.json", () => {
  test("file exists", () => {
    expect(existsSync("scan_result.json")).toBe(true)
  })

  test("has leaks array and summary object", () => {
    const r = loadResult()
    expect(r).toHaveProperty("leaks")
    expect(r).toHaveProperty("summary")
    expect(Array.isArray(r.leaks)).toBe(true)
  })

  test("leaks array has exactly 2 entries", () => {
    const r = loadResult()
    expect(r.leaks.length).toBe(2)
  })

  test("each leak has credential, session, timestamp, provider fields", () => {
    const r = loadResult()
    for (const leak of r.leaks) {
      expect(leak).toHaveProperty("credential")
      expect(leak).toHaveProperty("session")
      expect(leak).toHaveProperty("timestamp")
      expect(leak).toHaveProperty("provider")
    }
  })

  test("MyToken leak is found in session-aaa.jsonl with provider anthropic", () => {
    const r = loadResult()
    const tokenLeak = r.leaks.find((l: any) => l.credential === "MyToken")
    expect(tokenLeak).toBeDefined()
    expect(tokenLeak.session).toContain("session-aaa")
    expect(tokenLeak.provider).toBe("anthropic")
  })

  test("APIKey leak is found in session-ccc.jsonl with provider openai", () => {
    const r = loadResult()
    const apiLeak = r.leaks.find((l: any) => l.credential === "APIKey")
    expect(apiLeak).toBeDefined()
    expect(apiLeak.session).toContain("session-ccc")
    expect(apiLeak.provider).toBe("openai")
  })

  test("summary.files_scanned is 3", () => {
    const r = loadResult()
    expect(Number(r.summary.files_scanned)).toBe(3)
  })

  test("summary.credentials_checked is 2 and leaks_found is 2", () => {
    const r = loadResult()
    expect(Number(r.summary.credentials_checked)).toBe(2)
    expect(Number(r.summary.leaks_found)).toBe(2)
  })
})

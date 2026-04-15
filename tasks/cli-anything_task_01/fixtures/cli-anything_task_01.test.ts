import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"
import { execSync } from "child_process"

function loadSpec(): any {
  return JSON.parse(readFileSync("harness_spec.json", "utf-8"))
}

function runCLI(args: string): { stdout: string; exitCode: number } {
  try {
    const stdout = execSync(`python3 calc_cli.py ${args}`, { encoding: "utf-8" }).trim()
    return { stdout, exitCode: 0 }
  } catch (e: any) {
    return { stdout: (e.stdout || e.stderr || "").trim(), exitCode: e.status || 1 }
  }
}

describe("calculator.py", () => {
  test("file exists", () => {
    expect(existsSync("calculator.py")).toBe(true)
  })

  test("contains the four required functions", () => {
    const content = readFileSync("calculator.py", "utf-8")
    expect(content).toMatch(/def add\s*\(/)
    expect(content).toMatch(/def subtract\s*\(/)
    expect(content).toMatch(/def multiply\s*\(/)
    expect(content).toMatch(/def divide\s*\(/)
  })
})

describe("calc_cli.py", () => {
  test("file exists", () => {
    expect(existsSync("calc_cli.py")).toBe(true)
  })

  test("add 15 27 returns 42", () => {
    const r = runCLI("add 15 27")
    expect(r.exitCode).toBe(0)
    expect(parseFloat(r.stdout)).toBe(42)
  })

  test("multiply 6 7 returns 42", () => {
    const r = runCLI("multiply 6 7")
    expect(r.exitCode).toBe(0)
    expect(parseFloat(r.stdout)).toBe(42)
  })

  test("subtract 100 38 returns 62", () => {
    const r = runCLI("subtract 100 38")
    expect(r.exitCode).toBe(0)
    expect(parseFloat(r.stdout)).toBe(62)
  })

  test("divide 144 12 returns 12", () => {
    const r = runCLI("divide 144 12")
    expect(r.exitCode).toBe(0)
    expect(parseFloat(r.stdout)).toBe(12)
  })

  test("unknown operation exits with code 1 and prints error", () => {
    const r = runCLI("modulo 10 3")
    expect(r.exitCode).toBe(1)
    expect(r.stdout.toLowerCase()).toContain("error")
  })

  test("divide by zero exits with code 1 and prints error", () => {
    const r = runCLI("divide 10 0")
    expect(r.exitCode).toBe(1)
    expect(r.stdout.toLowerCase()).toContain("error")
  })
})

describe("harness_spec.json", () => {
  test("file exists", () => {
    expect(existsSync("harness_spec.json")).toBe(true)
  })

  test("has all required top-level fields", () => {
    const s = loadSpec()
    expect(s).toHaveProperty("name")
    expect(s).toHaveProperty("version")
    expect(s).toHaveProperty("entry_point")
    expect(s).toHaveProperty("commands")
    expect(s).toHaveProperty("error_handling")
  })

  test("name, version, and entry_point are correct", () => {
    const s = loadSpec()
    expect(s.name).toBe("calculator-harness")
    expect(s.version).toBe("1.0.0")
    expect(s.entry_point).toContain("calc_cli.py")
  })

  test("commands array has 4 entries with name and description", () => {
    const s = loadSpec()
    expect(Array.isArray(s.commands)).toBe(true)
    expect(s.commands.length).toBe(4)
    for (const cmd of s.commands) {
      expect(typeof cmd.name).toBe("string")
      expect(cmd.name.length).toBeGreaterThan(0)
      expect(typeof cmd.description).toBe("string")
      expect(cmd.description.length).toBeGreaterThan(0)
    }
  })
})

describe("test_results.txt", () => {
  test("file exists", () => {
    expect(existsSync("test_results.txt")).toBe(true)
  })

  test("contains results for all four operations", () => {
    const content = readFileSync("test_results.txt", "utf-8")
    expect(content).toContain("42")
    expect(content).toContain("62")
    expect(content).toContain("12")
  })
})

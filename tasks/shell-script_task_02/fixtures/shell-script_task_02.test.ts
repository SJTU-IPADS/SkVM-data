import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync, readdirSync } from "fs"
import { spawnSync } from "child_process"

function loadScript(): string {
  return readFileSync("backup.sh", "utf-8")
}

function loadResult(): any {
  return JSON.parse(readFileSync("backup_result.json", "utf-8"))
}

const REQUIRED_SOURCE_FILES = ["file1.txt", "file2.txt", "file3.log", "config.json", "README.md"]

describe("backup.sh", () => {
  test("file exists", () => {
    expect(existsSync("backup.sh")).toBe(true)
  })

  test("contains 'set -euo pipefail'", () => {
    const script = loadScript()
    expect(script).toContain("set -euo pipefail")
  })

  test("exits with code 1 when no arguments are provided", () => {
    const result = spawnSync("bash", ["backup.sh"], { cwd: process.cwd() })
    expect(result.status).toBe(1)
  })

  test("prints error to stderr when no arguments are provided", () => {
    const result = spawnSync("bash", ["backup.sh"], { cwd: process.cwd() })
    const stderr = result.stderr.toString()
    expect(stderr.length).toBeGreaterThan(0)
  })

  test("exits with code 2 when source directory does not exist", () => {
    const result = spawnSync("bash", ["backup.sh", "/nonexistent_source_xyz/", "/tmp/dest/"], { cwd: process.cwd() })
    expect(result.status).toBe(2)
  })

  test("prints file not found or directory error to stderr for missing source", () => {
    const result = spawnSync("bash", ["backup.sh", "/nonexistent_source_xyz/", "/tmp/dest/"], { cwd: process.cwd() })
    const stderr = result.stderr.toString()
    expect(stderr.length).toBeGreaterThan(0)
  })
})

describe("test_source/", () => {
  test("test_source directory exists", () => {
    expect(existsSync("test_source")).toBe(true)
  })

  test("test_source contains all 5 required files", () => {
    const files = readdirSync("test_source")
    for (const f of REQUIRED_SOURCE_FILES) {
      expect(files).toContain(f)
    }
  })

  test("each source file has content", () => {
    for (const f of REQUIRED_SOURCE_FILES) {
      const content = readFileSync(`test_source/${f}`, "utf-8")
      expect(content.trim().length).toBeGreaterThan(0)
    }
  })
})

describe("backup_result.json", () => {
  test("file exists", () => {
    expect(existsSync("backup_result.json")).toBe(true)
  })

  test("has required fields: exit_code, backup_path, manifest_content, files_backed_up", () => {
    const r = loadResult()
    expect(r).toHaveProperty("exit_code")
    expect(r).toHaveProperty("backup_path")
    expect(r).toHaveProperty("manifest_content")
    expect(r).toHaveProperty("files_backed_up")
  })

  test("exit_code is 0 (successful run)", () => {
    const r = loadResult()
    expect(r.exit_code).toBe(0)
  })

  test("files_backed_up is 5", () => {
    const r = loadResult()
    expect(r.files_backed_up).toBe(5)
  })

  test("manifest_content contains 'Total files:' line", () => {
    const r = loadResult()
    expect(typeof r.manifest_content).toBe("string")
    expect(r.manifest_content.toLowerCase()).toContain("total files:")
  })

  test("manifest_content lists 5 files before the Total files line", () => {
    const r = loadResult()
    const lines = r.manifest_content.split("\n").map((l: string) => l.trim()).filter((l: string) => l.length > 0)
    const fileLines = lines.filter((l: string) => !l.toLowerCase().startsWith("total"))
    expect(fileLines.length).toBe(5)
  })

  test("backup directory exists on the filesystem", () => {
    const r = loadResult()
    expect(typeof r.backup_path).toBe("string")
    expect(r.backup_path.length).toBeGreaterThan(0)
    expect(existsSync(r.backup_path)).toBe(true)
  })
})

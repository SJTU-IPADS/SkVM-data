import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync, statSync } from "fs"

const ROOT = "datautils-project"

function read(relPath: string): string {
  return readFileSync(`${ROOT}/${relPath}`, "utf-8")
}

describe("project root directory", () => {
  test("project root directory exists", () => {
    expect(existsSync(ROOT)).toBe(true)
  })

  test("src/datautils/ directory exists", () => {
    expect(existsSync(`${ROOT}/src/datautils`)).toBe(true)
  })

  test("tests/ directory exists", () => {
    expect(existsSync(`${ROOT}/tests`)).toBe(true)
  })
})

describe("src/datautils/__init__.py", () => {
  test("src/datautils/__init__.py exists", () => {
    expect(existsSync(`${ROOT}/src/datautils/__init__.py`)).toBe(true)
  })

  test("__version__ string is '0.1.0'", () => {
    const content = read("src/datautils/__init__.py")
    expect(content).toContain('__version__ = "0.1.0"')
  })
})

describe("tests/__init__.py", () => {
  test("tests/__init__.py exists", () => {
    expect(existsSync(`${ROOT}/tests/__init__.py`)).toBe(true)
  })
})

describe("pyproject.toml exists", () => {
  test("pyproject.toml exists", () => {
    expect(existsSync(`${ROOT}/pyproject.toml`)).toBe(true)
  })

  test("project name is datautils", () => {
    const content = read("pyproject.toml")
    expect(content).toContain('name = "datautils"')
  })

  test("version is 0.1.0", () => {
    const content = read("pyproject.toml")
    expect(content).toContain('version = "0.1.0"')
  })

  test("requires-python is >=3.10", () => {
    const content = read("pyproject.toml")
    expect(content).toContain("requires-python")
    expect(content).toContain("3.10")
  })

  test("[build-system] section with requires and build-backend", () => {
    const content = read("pyproject.toml")
    expect(content).toContain("[build-system]")
    expect(content).toContain("requires")
    expect(content).toContain("build-backend")
  })
})

describe("README.md headings", () => {
  test("README.md exists", () => {
    expect(existsSync(`${ROOT}/README.md`)).toBe(true)
  })

  test("README starts with # datautils heading", () => {
    const content = read("README.md")
    expect(content.trim().startsWith("# datautils")).toBe(true)
  })

  test("README has Installation and Usage section headings", () => {
    const content = read("README.md")
    expect(content).toContain("## Installation")
    expect(content).toContain("## Usage")
  })
})

describe("manifest.json", () => {
  test("manifest.json exists in project root", () => {
    expect(existsSync(`${ROOT}/manifest.json`)).toBe(true)
  })

  test("manifest has a 'files' array", () => {
    const m = JSON.parse(read("manifest.json"))
    expect(m).toHaveProperty("files")
    expect(Array.isArray(m.files)).toBe(true)
  })

  test("manifest files array is sorted alphabetically", () => {
    const m = JSON.parse(read("manifest.json"))
    const files: string[] = m.files
    const sorted = [...files].sort()
    expect(files).toEqual(sorted)
  })

  test("manifest includes key files", () => {
    const m = JSON.parse(read("manifest.json"))
    const files: string[] = m.files
    const hasInit = files.some(f => f.includes("__init__.py") && f.includes("datautils"))
    const hasPyproject = files.some(f => f.includes("pyproject.toml"))
    const hasReadme = files.some(f => f.toLowerCase().includes("readme"))
    expect(hasInit).toBe(true)
    expect(hasPyproject).toBe(true)
    expect(hasReadme).toBe(true)
  })
})

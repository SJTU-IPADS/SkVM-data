import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync, statSync } from "fs"

function loadMakefile(): string {
  return readFileSync("Makefile", "utf-8")
}

function loadRef(): string {
  return readFileSync("build_reference.md", "utf-8")
}

describe("Makefile", () => {
  test("file exists", () => {
    expect(existsSync("Makefile")).toBe(true)
  })

  test("defines CC variable as gcc", () => {
    const mk = loadMakefile()
    expect(mk).toMatch(/^\s*CC\s*[:?]?=\s*gcc/m)
  })

  test("defines CFLAGS with -Wall and -O2", () => {
    const mk = loadMakefile()
    expect(mk).toMatch(/CFLAGS\s*[:?]?=.*-Wall/m)
    expect(mk).toMatch(/CFLAGS\s*[:?]?=.*-O2/m)
  })

  test("defines TARGET variable as myapp", () => {
    const mk = loadMakefile()
    expect(mk).toMatch(/TARGET\s*[:?]?=\s*myapp/m)
  })

  test("defines BUILD_DIR and SRC_DIR variables", () => {
    const mk = loadMakefile()
    expect(mk).toMatch(/BUILD_DIR\s*[:?]?=\s*build/m)
    expect(mk).toMatch(/SRC_DIR\s*[:?]?=\s*src/m)
  })

  test("has 'all' target as default", () => {
    const mk = loadMakefile()
    expect(mk).toMatch(/^all\s*:/m)
  })

  test("has pattern rule for .o files", () => {
    const mk = loadMakefile()
    // Match pattern rule: %.o: or build/%.o:
    expect(mk).toMatch(/%.o\s*:/m)
  })

  test("has 'clean' target with rm command", () => {
    const mk = loadMakefile()
    expect(mk).toMatch(/^clean\s*:/m)
    expect(mk).toMatch(/rm\s+-rf/m)
  })

  test("has 'install' target", () => {
    const mk = loadMakefile()
    expect(mk).toMatch(/^install\s*:/m)
  })

  test("has .PHONY declaration with all, clean, install", () => {
    const mk = loadMakefile()
    expect(mk).toMatch(/\.PHONY/m)
    const phonyLine = mk.match(/\.PHONY.*$/m)?.[0] ?? ""
    expect(phonyLine.toLowerCase()).toContain("all")
    expect(phonyLine.toLowerCase()).toContain("clean")
    expect(phonyLine.toLowerCase()).toContain("install")
  })
})

describe("build_reference.md", () => {
  test("file exists", () => {
    expect(existsSync("build_reference.md")).toBe(true)
  })

  test("is at least 150 words", () => {
    const content = loadRef()
    const wordCount = content.trim().split(/\s+/).length
    expect(wordCount).toBeGreaterThanOrEqual(150)
  })

  test("mentions .PHONY", () => {
    const content = loadRef()
    expect(content.toLowerCase()).toContain("phony")
  })

  test("mentions optimization (-O2 or optimization level)", () => {
    const content = loadRef()
    const hasOptimization = content.includes("-O2") || content.toLowerCase().includes("optim")
    expect(hasOptimization).toBe(true)
  })
})

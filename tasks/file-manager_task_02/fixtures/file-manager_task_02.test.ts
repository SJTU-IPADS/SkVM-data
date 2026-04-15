import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadSummary(): any {
  return JSON.parse(readFileSync("organize_summary.json", "utf-8"))
}

describe("organize_summary.json", () => {
  test("summary file exists", () => {
    expect(existsSync("organize_summary.json")).toBe(true)
  })

  test("parses as valid JSON", () => {
    expect(() => loadSummary()).not.toThrow()
  })

  test("has required fields: source_dir, output_dir, total_moved, categories", () => {
    const s = loadSummary()
    expect(s).toHaveProperty("source_dir")
    expect(s).toHaveProperty("output_dir")
    expect(s).toHaveProperty("total_moved")
    expect(s).toHaveProperty("categories")
  })

  test("total_moved is 8", () => {
    const s = loadSummary()
    expect(s.total_moved).toBe(8)
  })

  test("categories has documents, images, and data keys", () => {
    const s = loadSummary()
    expect(s.categories).toHaveProperty("documents")
    expect(s.categories).toHaveProperty("images")
    expect(s.categories).toHaveProperty("data")
  })
})

describe("organized/documents directory", () => {
  test("documents directory exists under organized/", () => {
    expect(existsSync("organized/documents")).toBe(true)
  })

  test("organized/documents contains notes.txt, readme.txt, report.pdf", () => {
    expect(existsSync("organized/documents/notes.txt")).toBe(true)
    expect(existsSync("organized/documents/readme.txt")).toBe(true)
    expect(existsSync("organized/documents/report.pdf")).toBe(true)
  })

  test("documents array in summary contains 3 entries sorted alphabetically", () => {
    const s = loadSummary()
    const docs: string[] = s.categories.documents
    expect(docs.length).toBe(3)
    const sorted = [...docs].sort()
    expect(docs).toEqual(sorted)
    expect(docs).toContain("notes.txt")
    expect(docs).toContain("readme.txt")
    expect(docs).toContain("report.pdf")
  })
})

describe("organized/images directory", () => {
  test("images directory exists under organized/", () => {
    expect(existsSync("organized/images")).toBe(true)
  })

  test("organized/images contains banner.png, logo.jpg, photo.jpg", () => {
    expect(existsSync("organized/images/banner.png")).toBe(true)
    expect(existsSync("organized/images/logo.jpg")).toBe(true)
    expect(existsSync("organized/images/photo.jpg")).toBe(true)
  })

  test("images array in summary sorted alphabetically", () => {
    const s = loadSummary()
    const imgs: string[] = s.categories.images
    expect(imgs.length).toBe(3)
    const sorted = [...imgs].sort()
    expect(imgs).toEqual(sorted)
  })
})

describe("organized/data directory", () => {
  test("data directory exists under organized/", () => {
    expect(existsSync("organized/data")).toBe(true)
  })

  test("organized/data contains budget.csv and data.csv", () => {
    expect(existsSync("organized/data/budget.csv")).toBe(true)
    expect(existsSync("organized/data/data.csv")).toBe(true)
  })

  test("data array in summary sorted alphabetically", () => {
    const s = loadSummary()
    const data: string[] = s.categories.data
    expect(data.length).toBe(2)
    const sorted = [...data].sort()
    expect(data).toEqual(sorted)
    expect(data).toContain("budget.csv")
    expect(data).toContain("data.csv")
  })
})

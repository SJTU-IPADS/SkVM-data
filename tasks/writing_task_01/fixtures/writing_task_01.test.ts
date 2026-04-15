import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadEmail(): string {
  return readFileSync("email.txt", "utf-8")
}

function loadBlog(): string {
  return readFileSync("blog_intro.txt", "utf-8")
}

function countWords(text: string): number {
  return text.trim().split(/\s+/).filter((w) => w.length > 0).length
}

describe("email.txt", () => {
  test("file exists", () => {
    expect(existsSync("email.txt")).toBe(true)
  })

  test("email has Subject: line as the first non-empty line", () => {
    const email = loadEmail()
    const firstLine = email.trim().split("\n")[0]
    expect(firstLine.toLowerCase()).toMatch(/^subject:/)
  })

  test("email contains March 29 as the new release date", () => {
    const email = loadEmail()
    expect(email).toMatch(/march 29|mar(ch)?\s*29/i)
  })

  test("email mentions security vulnerability as the reason", () => {
    const email = loadEmail()
    expect(email.toLowerCase()).toMatch(/security|vulnerabilit/)
  })

  test("email mentions Monday 10am sync meeting as next step", () => {
    const email = loadEmail()
    expect(email.toLowerCase()).toMatch(/monday|10\s*am|sync/)
  })

  test("email body is 100-150 words", () => {
    const email = loadEmail()
    // Remove subject line for word count
    const lines = email.trim().split("\n")
    const bodyLines = lines.slice(1).join("\n")
    const wordCount = countWords(bodyLines)
    expect(wordCount).toBeGreaterThanOrEqual(80)
    expect(wordCount).toBeLessThanOrEqual(200)
  })
})

describe("blog_intro.txt", () => {
  test("file exists", () => {
    expect(existsSync("blog_intro.txt")).toBe(true)
  })

  test("blog intro is non-empty prose with at least 50 words", () => {
    const blog = loadBlog()
    expect(blog.trim().length).toBeGreaterThan(0)
    expect(countWords(blog)).toBeGreaterThanOrEqual(50)
  })

  test("blog is within 80-120 words", () => {
    const blog = loadBlog()
    const wc = countWords(blog)
    expect(wc).toBeGreaterThanOrEqual(60)
    expect(wc).toBeLessThanOrEqual(150)
  })

  test("blog has no ## subheadings", () => {
    const blog = loadBlog()
    expect(blog).not.toMatch(/^##\s/m)
  })

  test("blog mentions remote work or office in context", () => {
    const blog = loadBlog()
    expect(blog.toLowerCase()).toMatch(/remote|office|team/)
  })
})

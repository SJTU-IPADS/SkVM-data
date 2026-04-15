import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadPlaybook(): any {
  return JSON.parse(readFileSync("email_playbook.json", "utf-8"))
}

describe("email_playbook.json", () => {
  test("file exists", () => {
    expect(existsSync("email_playbook.json")).toBe(true)
  })

  test("valid JSON and parseable", () => {
    expect(() => loadPlaybook()).not.toThrow()
  })

  test("has required top-level fields: goal, emails, principles_used", () => {
    const p = loadPlaybook()
    expect(p).toHaveProperty("goal")
    expect(p).toHaveProperty("emails")
    expect(p).toHaveProperty("principles_used")
  })

  test("contains exactly 5 emails", () => {
    const p = loadPlaybook()
    expect(Array.isArray(p.emails)).toBe(true)
    expect(p.emails.length).toBe(5)
  })

  test("each email has required fields: position, subject_line, primary_principle, principle_application, cta_text", () => {
    const p = loadPlaybook()
    for (const email of p.emails) {
      expect(typeof email.position).toBe("number")
      expect(typeof email.subject_line).toBe("string")
      expect(typeof email.primary_principle).toBe("string")
      expect(typeof email.principle_application).toBe("string")
      expect(typeof email.cta_text).toBe("string")
    }
  })

  test("positions are 1 through 5 in sequence", () => {
    const p = loadPlaybook()
    const positions = p.emails.map((e: any) => e.position).sort((a: number, b: number) => a - b)
    expect(positions).toEqual([1, 2, 3, 4, 5])
  })

  test("all 5 principles are distinct (no repeated primary_principle)", () => {
    const p = loadPlaybook()
    const principles = p.emails.map((e: any) => e.primary_principle.toLowerCase().trim())
    const unique = new Set(principles)
    expect(unique.size).toBe(5)
  })

  test("at least one email uses Loss Aversion", () => {
    const p = loadPlaybook()
    const hasLossAversion = p.emails.some((e: any) =>
      e.primary_principle.toLowerCase().includes("loss aversion")
    )
    expect(hasLossAversion).toBe(true)
  })

  test("at least one email uses Goal-Gradient Effect", () => {
    const p = loadPlaybook()
    const hasGoalGradient = p.emails.some((e: any) =>
      e.primary_principle.toLowerCase().includes("goal") &&
      e.primary_principle.toLowerCase().includes("gradient")
    )
    expect(hasGoalGradient).toBe(true)
  })

  test("each subject line is 10 words or fewer", () => {
    const p = loadPlaybook()
    for (const email of p.emails) {
      const wordCount = email.subject_line.trim().split(/\s+/).length
      expect(wordCount).toBeLessThanOrEqual(10)
    }
  })

  test("principles_used lists exactly 5 distinct entries matching the emails", () => {
    const p = loadPlaybook()
    expect(Array.isArray(p.principles_used)).toBe(true)
    expect(p.principles_used.length).toBe(5)
    const emailPrinciples = new Set(p.emails.map((e: any) => e.primary_principle.toLowerCase().trim()))
    for (const listed of p.principles_used) {
      expect(emailPrinciples.has(listed.toLowerCase().trim())).toBe(true)
    }
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadInventory(): any {
  return JSON.parse(readFileSync("tech_debt_inventory.json", "utf-8"))
}

function loadPlan(): string {
  return readFileSync("remediation_plan.md", "utf-8")
}

// Expected severity assignments based on risk
// P0: hardcoded API keys (security)
// P1: DB indexes (SLA violation - 850ms vs 200ms target)
// P2: auth v1 API (deprecated), Python 2.7 EOL
// P3: monolithic deploy pipeline (slowness)

describe("tech_debt_inventory.json", () => {
  test("file exists", () => {
    expect(existsSync("tech_debt_inventory.json")).toBe(true)
  })

  test("is valid JSON with required top-level keys", () => {
    const inv = loadInventory()
    expect(inv).toHaveProperty("team_size")
    expect(inv).toHaveProperty("items")
    expect(inv).toHaveProperty("sorted_by_priority")
    expect(inv).toHaveProperty("debt_ratio_pct")
    expect(inv).toHaveProperty("immediate_sprint")
    expect(inv).toHaveProperty("next_quarter")
    expect(inv).toHaveProperty("tracked_backlog")
  })

  test("team_size is 45", () => {
    const inv = loadInventory()
    expect(inv.team_size).toBe(45)
  })

  test("items array has exactly 5 entries with required fields", () => {
    const inv = loadInventory()
    expect(Array.isArray(inv.items)).toBe(true)
    expect(inv.items.length).toBe(5)
    const validSeverities = ["P0", "P1", "P2", "P3"]
    for (const item of inv.items) {
      expect(typeof item.name).toBe("string")
      expect(validSeverities).toContain(item.severity)
      expect(typeof item.cost_to_fix_days).toBe("number")
      expect(item.cost_to_fix_days).toBeGreaterThan(0)
      expect(typeof item.blast_radius).toBe("number")
      expect(item.blast_radius).toBeGreaterThan(0)
      expect(typeof item.priority_score).toBe("number")
      expect(item.priority_score).toBeGreaterThan(0)
    }
  })

  test("priority_score computation is correct for each item (±0.1 tolerance)", () => {
    const inv = loadInventory()
    const severityWeights: Record<string, number> = { P0: 4, P1: 3, P2: 2, P3: 1 }
    for (const item of inv.items) {
      const weight = severityWeights[item.severity]
      const expected = (weight * item.blast_radius) / item.cost_to_fix_days
      expect(Math.abs(item.priority_score - expected)).toBeLessThan(0.1)
    }
  })

  test("sorted_by_priority has 5 entries in descending priority order", () => {
    const inv = loadInventory()
    expect(Array.isArray(inv.sorted_by_priority)).toBe(true)
    expect(inv.sorted_by_priority.length).toBe(5)
    // Verify order: each item's priority_score >= next item's
    for (let i = 0; i < inv.sorted_by_priority.length - 1; i++) {
      const current = inv.items.find((it: any) => it.name === inv.sorted_by_priority[i])
      const next = inv.items.find((it: any) => it.name === inv.sorted_by_priority[i + 1])
      if (current && next) {
        expect(current.priority_score).toBeGreaterThanOrEqual(next.priority_score)
      }
    }
  })

  test("debt_ratio_pct is correct (sum of days / 450 * 100, ±0.5 tolerance)", () => {
    const inv = loadInventory()
    // Items: 10 + 2 + 15 + 5 + 3 = 35 days total
    // 35 / (45 * 10) * 100 = 35 / 450 * 100 = 7.778...% ≈ 7.8%
    const totalDays = inv.items.reduce((sum: number, it: any) => sum + it.cost_to_fix_days, 0)
    const expected = (totalDays / (45 * 10)) * 100
    expect(Math.abs(inv.debt_ratio_pct - expected)).toBeLessThan(0.5)
  })

  test("immediate_sprint contains only P0 and P1 items", () => {
    const inv = loadInventory()
    expect(Array.isArray(inv.immediate_sprint)).toBe(true)
    for (const name of inv.immediate_sprint) {
      const item = inv.items.find((it: any) => it.name === name)
      expect(item).toBeDefined()
      expect(["P0", "P1"]).toContain(item.severity)
    }
  })

  test("next_quarter contains only P2 items", () => {
    const inv = loadInventory()
    for (const name of inv.next_quarter) {
      const item = inv.items.find((it: any) => it.name === name)
      expect(item).toBeDefined()
      expect(item.severity).toBe("P2")
    }
  })

  test("all items appear in exactly one of the three tiers", () => {
    const inv = loadInventory()
    const allTiered = [...inv.immediate_sprint, ...inv.next_quarter, ...inv.tracked_backlog]
    expect(allTiered.length).toBe(5)
    const uniqueNames = new Set(allTiered)
    expect(uniqueNames.size).toBe(5)
  })
})

describe("remediation_plan.md", () => {
  test("file exists", () => {
    expect(existsSync("remediation_plan.md")).toBe(true)
  })

  test("plan is at least 150 words", () => {
    const text = loadPlan()
    const words = text.trim().split(/\s+/).length
    expect(words).toBeGreaterThanOrEqual(150)
  })

  test("plan mentions security and performance issues", () => {
    const text = loadPlan().toLowerCase()
    expect(text).toMatch(/security|api key/)
    expect(text).toMatch(/performance|latency|sla/)
  })
})

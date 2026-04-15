import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadState(): any[] {
  return JSON.parse(readFileSync("need_state.json", "utf-8"))
}

function loadLog(): any[] {
  return JSON.parse(readFileSync("sim_log.json", "utf-8"))
}

// Expected final values (manual trace):
// Initial: connection=2.8/8h, coherence=2.5/24h, autonomy=1.2/36h
// Step 1 - decay 12h:
//   connection = max(0.5, 2.8 - 12/8) = max(0.5, 1.3) = 1.3
//   coherence  = max(0.5, 2.5 - 12/24) = max(0.5, 2.0) = 2.0
//   autonomy   = max(0.5, 1.2 - 12/36) = max(0.5, 0.8667) ≈ 0.8667
// Step 2 - mark connection +1.4:
//   connection = min(3.0, 1.3 + 1.4) = 2.7
// Step 3 - decay 6h:
//   connection = max(0.5, 2.7 - 6/8)  = max(0.5, 1.95) = 1.95
//   coherence  = max(0.5, 2.0 - 6/24) = max(0.5, 1.75) = 1.75
//   autonomy   = max(0.5, 0.8667 - 6/36) = max(0.5, 0.7) = 0.7
// Step 4 - mark autonomy +2.0:
//   autonomy   = min(3.0, 0.7 + 2.0) = 2.7

describe("need_decay.py", () => {
  test("file exists", () => {
    expect(existsSync("need_decay.py")).toBe(true)
  })
})

describe("need_state.json", () => {
  test("file exists", () => {
    expect(existsSync("need_state.json")).toBe(true)
  })

  test("need_state has 3 needs", () => {
    const state = loadState()
    expect(Array.isArray(state)).toBe(true)
    expect(state.length).toBe(3)
  })

  test("each need has required fields: need, satisfaction, decay_rate_hours", () => {
    const state = loadState()
    for (const n of state) {
      expect(n).toHaveProperty("need")
      expect(n).toHaveProperty("satisfaction")
      expect(n).toHaveProperty("decay_rate_hours")
    }
  })

  test("connection final satisfaction is approximately 1.95", () => {
    const state = loadState()
    const conn = state.find((n: any) => n.need === "connection")
    expect(conn).toBeDefined()
    expect(conn.satisfaction).toBeCloseTo(1.95, 2)
  })

  test("coherence final satisfaction is approximately 1.75", () => {
    const state = loadState()
    const coh = state.find((n: any) => n.need === "coherence")
    expect(coh).toBeDefined()
    expect(coh.satisfaction).toBeCloseTo(1.75, 2)
  })

  test("autonomy final satisfaction is approximately 2.7", () => {
    const state = loadState()
    const aut = state.find((n: any) => n.need === "autonomy")
    expect(aut).toBeDefined()
    expect(aut.satisfaction).toBeCloseTo(2.7, 2)
  })

  test("all satisfaction values are within [0.5, 3.0] bounds", () => {
    const state = loadState()
    for (const n of state) {
      expect(n.satisfaction).toBeGreaterThanOrEqual(0.5)
      expect(n.satisfaction).toBeLessThanOrEqual(3.0)
    }
  })
})

describe("sim_log.json", () => {
  test("file exists", () => {
    expect(existsSync("sim_log.json")).toBe(true)
  })

  test("sim_log has 4 events", () => {
    const log = loadLog()
    expect(Array.isArray(log)).toBe(true)
    expect(log.length).toBe(4)
  })

  test("steps are numbered 1 through 4", () => {
    const log = loadLog()
    const steps = log.map((e: any) => e.step)
    expect(steps).toContain(1)
    expect(steps).toContain(2)
    expect(steps).toContain(3)
    expect(steps).toContain(4)
  })

  test("each event has a snapshot field that is an array", () => {
    const log = loadLog()
    for (const event of log) {
      expect(event).toHaveProperty("snapshot")
      expect(Array.isArray(event.snapshot)).toBe(true)
    }
  })
})

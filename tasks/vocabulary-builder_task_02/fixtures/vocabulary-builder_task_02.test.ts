import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadSchedule(): any {
  return JSON.parse(readFileSync("review_schedule.json", "utf-8"))
}

// Precomputed expected dates
// ephemeral learned 2026-04-01: +1=04-02, +3=04-04, +7=04-08, +14=04-15, +30=05-01, +90=06-30
// cacophony learned 2026-04-05: +1=04-06, +3=04-08, +7=04-12, +14=04-19, +30=05-05, +90=07-04
// sycophant learned 2026-04-08: +1=04-09, +3=04-11, +7=04-15, +14=04-22, +30=05-08, +90=07-07

const EXPECTED: Record<string, {learned: string, reviews: string[], mastery: string}> = {
  "ephemeral": {
    learned: "2026-04-01",
    reviews: ["2026-04-02", "2026-04-04", "2026-04-08", "2026-04-15", "2026-05-01", "2026-06-30"],
    mastery: "2026-06-30"
  },
  "cacophony": {
    learned: "2026-04-05",
    reviews: ["2026-04-06", "2026-04-08", "2026-04-12", "2026-04-19", "2026-05-05", "2026-07-04"],
    mastery: "2026-07-04"
  },
  "sycophant": {
    learned: "2026-04-08",
    reviews: ["2026-04-09", "2026-04-11", "2026-04-15", "2026-04-22", "2026-05-08", "2026-07-07"],
    mastery: "2026-07-07"
  }
}

const INTERVALS = ["1d", "3d", "7d", "14d", "30d", "90d"]

describe("review_schedule.json", () => {
  test("file exists", () => {
    expect(existsSync("review_schedule.json")).toBe(true)
  })

  test("has words array, next_due, next_word fields", () => {
    const s = loadSchedule()
    expect(s).toHaveProperty("words")
    expect(s).toHaveProperty("next_due")
    expect(s).toHaveProperty("next_word")
    expect(Array.isArray(s.words)).toBe(true)
  })

  test("contains 3 word entries", () => {
    const s = loadSchedule()
    expect(s.words.length).toBe(3)
  })

  test("each word has 6 review milestones with interval labels", () => {
    const s = loadSchedule()
    for (const w of s.words) {
      expect(Array.isArray(w.reviews)).toBe(true)
      expect(w.reviews.length).toBe(6)
      const labels = w.reviews.map((r: any) => r.interval)
      for (const iv of INTERVALS) {
        expect(labels).toContain(iv)
      }
    }
  })

  test("ephemeral review dates are correct", () => {
    const s = loadSchedule()
    const e = s.words.find((w: any) => w.word === "ephemeral")
    expect(e).toBeDefined()
    expect(e.learned).toBe("2026-04-01")
    const dues = e.reviews.map((r: any) => r.due)
    for (const d of EXPECTED["ephemeral"].reviews) {
      expect(dues).toContain(d)
    }
  })

  test("cacophony review dates are correct", () => {
    const s = loadSchedule()
    const c = s.words.find((w: any) => w.word === "cacophony")
    expect(c).toBeDefined()
    expect(c.learned).toBe("2026-04-05")
    const dues = c.reviews.map((r: any) => r.due)
    for (const d of EXPECTED["cacophony"].reviews) {
      expect(dues).toContain(d)
    }
  })

  test("sycophant review dates are correct", () => {
    const s = loadSchedule()
    const sy = s.words.find((w: any) => w.word === "sycophant")
    expect(sy).toBeDefined()
    expect(sy.learned).toBe("2026-04-08")
    const dues = sy.reviews.map((r: any) => r.due)
    for (const d of EXPECTED["sycophant"].reviews) {
      expect(dues).toContain(d)
    }
  })

  test("mastery_date equals 90d review date for each word", () => {
    const s = loadSchedule()
    for (const w of s.words) {
      const review90 = w.reviews.find((r: any) => r.interval === "90d")
      expect(review90).toBeDefined()
      expect(w.mastery_date).toBe(review90.due)
    }
  })

  test("next_due and next_word correct: sycophant due 2026-04-11", () => {
    const s = loadSchedule()
    // On 2026-04-11, sycophant's 3d review is due (earliest on or after 04-11)
    expect(s.next_due).toBe("2026-04-11")
    expect(s.next_word).toBe("sycophant")
  })
})

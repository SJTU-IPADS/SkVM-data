import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadSplits(): any {
  return JSON.parse(readFileSync("dataset_splits.json", "utf-8"))
}

function loadAugPlan(): any {
  return JSON.parse(readFileSync("augmentation_plan.json", "utf-8"))
}

const VALID_CATEGORIES = new Set(["geometric", "color", "advanced"])

describe("dataset_splits.json", () => {
  test("file exists", () => {
    expect(existsSync("dataset_splits.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const d = loadSplits()
    expect(d).toHaveProperty("total_images")
    expect(d).toHaveProperty("split_ratios")
    expect(d).toHaveProperty("split_counts")
    expect(d).toHaveProperty("classes")
    expect(d).toHaveProperty("class_distribution")
    expect(d).toHaveProperty("most_common_class")
    expect(d).toHaveProperty("least_common_class")
    expect(d).toHaveProperty("imbalance_ratio")
  })

  test("total_images is 8500", () => {
    const d = loadSplits()
    expect(d.total_images).toBe(8500)
  })

  test("split_counts sum to 8500", () => {
    const d = loadSplits()
    const total = d.split_counts.train + d.split_counts.val + d.split_counts.test
    expect(total).toBe(8500)
  })

  test("split counts are correct: train=6800, val=850, test=850", () => {
    const d = loadSplits()
    expect(d.split_counts.train).toBe(6800)
    expect(d.split_counts.val).toBe(850)
    expect(d.split_counts.test).toBe(850)
  })

  test("classes array contains all 5 expected classes", () => {
    const d = loadSplits()
    expect(Array.isArray(d.classes)).toBe(true)
    expect(d.classes).toContain("car")
    expect(d.classes).toContain("pedestrian")
    expect(d.classes).toContain("cyclist")
    expect(d.classes).toContain("truck")
    expect(d.classes).toContain("bus")
  })

  test("most_common_class is 'car' and least_common_class is 'bus'", () => {
    const d = loadSplits()
    expect(d.most_common_class).toBe("car")
    expect(d.least_common_class).toBe("bus")
  })

  test("imbalance_ratio is correct: 18000/2800 ≈ 6.43", () => {
    const d = loadSplits()
    expect(typeof d.imbalance_ratio).toBe("number")
    // 18000 / 2800 = 6.4285..., rounded to 2 decimal places = 6.43
    expect(Math.abs(d.imbalance_ratio - 6.43)).toBeLessThan(0.01)
  })
})

describe("augmentation_plan.json", () => {
  test("file exists", () => {
    expect(existsSync("augmentation_plan.json")).toBe(true)
  })

  test("is an array with at least 5 augmentation entries", () => {
    const d = loadAugPlan()
    expect(Array.isArray(d)).toBe(true)
    expect(d.length).toBeGreaterThanOrEqual(5)
  })

  test("each entry has required fields", () => {
    const d = loadAugPlan()
    for (const entry of d) {
      expect(typeof entry.name).toBe("string")
      expect(typeof entry.category).toBe("string")
      expect(typeof entry.probability).toBe("number")
      expect(typeof entry.recommended_for_detection).toBe("boolean")
      expect(typeof entry.rationale).toBe("string")
    }
  })

  test("category values are 'geometric', 'color', or 'advanced'", () => {
    const d = loadAugPlan()
    for (const entry of d) {
      expect(VALID_CATEGORIES.has(entry.category)).toBe(true)
    }
  })

  test("probability values are between 0 and 1 (exclusive)", () => {
    const d = loadAugPlan()
    for (const entry of d) {
      expect(entry.probability).toBeGreaterThan(0)
      expect(entry.probability).toBeLessThanOrEqual(1)
    }
  })

  test("plan includes at least one geometric and one color augmentation", () => {
    const d = loadAugPlan()
    const categories = d.map((e: any) => e.category)
    expect(categories).toContain("geometric")
    expect(categories).toContain("color")
  })

  test("rationale strings are non-empty (at least 10 chars each)", () => {
    const d = loadAugPlan()
    for (const entry of d) {
      expect(entry.rationale.length).toBeGreaterThan(10)
    }
  })
})

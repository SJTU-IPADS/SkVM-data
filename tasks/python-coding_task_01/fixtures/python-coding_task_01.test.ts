import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadResults(): any {
  return JSON.parse(readFileSync("results.json", "utf-8"))
}

function loadScript(): string {
  return readFileSync("process_sales.py", "utf-8")
}

// Expected values computed from the CSV data:
// Widget A: 10+8+6=24 units, revenue = 24*25.99 = 623.76
// Widget B: 5+12=17 units, revenue = 17*49.99 = 849.83
// Widget C: 3 units, revenue = 3*99.99 = 299.97
// total_units_sold = 24+17+3 = 44
// total_revenue = 623.76 + 849.83 + 299.97 = 1773.56
// best_selling_product = Widget A (24 units)
// unique_products = 3

describe("results.json", () => {
  test("file exists", () => {
    expect(existsSync("results.json")).toBe(true)
  })

  test("has all required fields", () => {
    const r = loadResults()
    expect(r).toHaveProperty("total_revenue")
    expect(r).toHaveProperty("total_units_sold")
    expect(r).toHaveProperty("unique_products")
    expect(r).toHaveProperty("best_selling_product")
    expect(r).toHaveProperty("revenue_by_product")
  })

  test("total_units_sold is 44", () => {
    const r = loadResults()
    expect(r.total_units_sold).toBe(44)
  })

  test("total_revenue is 1773.56", () => {
    const r = loadResults()
    expect(r.total_revenue).toBe(1773.56)
  })

  test("unique_products is 3", () => {
    const r = loadResults()
    expect(r.unique_products).toBe(3)
  })

  test("best_selling_product is Widget A", () => {
    const r = loadResults()
    expect(r.best_selling_product).toBe("Widget A")
  })

  test("revenue_by_product has entries for Widget A, Widget B, Widget C", () => {
    const r = loadResults()
    expect(r.revenue_by_product).toHaveProperty("Widget A")
    expect(r.revenue_by_product).toHaveProperty("Widget B")
    expect(r.revenue_by_product).toHaveProperty("Widget C")
  })

  test("revenue_by_product values are correct", () => {
    const r = loadResults()
    expect(r.revenue_by_product["Widget A"]).toBe(623.76)
    expect(r.revenue_by_product["Widget B"]).toBe(849.83)
    expect(r.revenue_by_product["Widget C"]).toBe(299.97)
  })
})

describe("process_sales.py", () => {
  test("script file exists", () => {
    expect(existsSync("process_sales.py")).toBe(true)
  })

  test("script contains a main() function", () => {
    const src = loadScript()
    expect(src).toContain("def main(")
  })

  test("script contains if __name__ == '__main__' guard", () => {
    const src = loadScript()
    expect(src).toContain("__name__")
    expect(src).toContain("__main__")
  })

  test("script does not import pandas or numpy", () => {
    const src = loadScript()
    expect(src).not.toContain("import pandas")
    expect(src).not.toContain("import numpy")
    expect(src).not.toContain("from pandas")
    expect(src).not.toContain("from numpy")
  })
})

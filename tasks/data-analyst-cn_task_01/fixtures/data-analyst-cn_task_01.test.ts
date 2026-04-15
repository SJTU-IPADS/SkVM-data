import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const OUTPUT_FILE = "output/sales_report.json";

function loadOutput(workspace: string) {
  const filePath = join(workspace, OUTPUT_FILE);
  const content = readFileSync(filePath, "utf-8");
  return JSON.parse(content);
}

const workspace = process.env.WORKSPACE_PATH || ".";

// Expected values:
// total_sales = 1200+800+3000+2500+1500+700+900+4000+600+1100 = 16300
// total_profit = 300+200+600+500+375+140+180+800+150+220 = 3465
// profit_margin = 3465/16300 = 0.2125...
// Food: sales=4100, profit=1025, count=4
// Electronics: sales=9500, profit=1900, count=3
// Clothing: sales=2700, profit=540, count=3
// top_category = Electronics

describe("output/sales_report.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, OUTPUT_FILE))).toBe(true);
  });

  test("valid JSON format", () => {
    expect(() => loadOutput(workspace)).not.toThrow();
  });

  test("has all required top-level keys", () => {
    const data = loadOutput(workspace);
    expect(data).toHaveProperty("total_sales");
    expect(data).toHaveProperty("total_profit");
    expect(data).toHaveProperty("profit_margin");
    expect(data).toHaveProperty("category_summary");
    expect(data).toHaveProperty("top_category_by_sales");
  });

  test("total_sales is 16300", () => {
    const data = loadOutput(workspace);
    expect(Number(data.total_sales)).toBe(16300);
  });

  test("total_profit is 3465", () => {
    const data = loadOutput(workspace);
    expect(Number(data.total_profit)).toBe(3465);
  });

  test("profit_margin is approximately 0.2125", () => {
    const data = loadOutput(workspace);
    expect(Math.abs(Number(data.profit_margin) - 0.2125)).toBeLessThan(0.001);
  });

  test("category_summary has correct categories", () => {
    const data = loadOutput(workspace);
    expect(data.category_summary).toHaveProperty("Food");
    expect(data.category_summary).toHaveProperty("Electronics");
    expect(data.category_summary).toHaveProperty("Clothing");
  });

  test("Electronics category totals are correct", () => {
    const data = loadOutput(workspace);
    const elec = data.category_summary["Electronics"];
    expect(Number(elec.total_sales)).toBe(9500);
    expect(Number(elec.total_profit)).toBe(1900);
    expect(Number(elec.item_count)).toBe(3);
  });

  test("top_category_by_sales is Electronics", () => {
    const data = loadOutput(workspace);
    expect(data.top_category_by_sales).toBe("Electronics");
  });
});

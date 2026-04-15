import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const OUTPUT_FILE = "output/stats_report.json";

function loadOutput(workspace: string) {
  const filePath = join(workspace, OUTPUT_FILE);
  const content = readFileSync(filePath, "utf-8");
  return JSON.parse(content);
}

const workspace = process.env.WORKSPACE_PATH || ".";

// Expected values:
// ad_spend: [500,600,550,700,800,650,750,900,850,1000]
// mean = 7300/10 = 730, min=500, max=1000
// revenue: [2100,2400,2200,2800,3200,2600,3000,3600,3400,4000]
// total revenue = 29300, mean = 2930, min=2100, max=4000
// revenue_per_spend = 29300/7300 = 4.0137...
// Pearson corr(ad_spend, revenue): since revenue = 4*ad_spend + 100, correlation should be 1.0
// Pearson corr(ad_spend, orders): since orders = revenue/50, also 1.0

describe("output/stats_report.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, OUTPUT_FILE))).toBe(true);
  });

  test("valid JSON format", () => {
    expect(() => loadOutput(workspace)).not.toThrow();
  });

  test("has all required keys", () => {
    const data = loadOutput(workspace);
    expect(data).toHaveProperty("ad_spend_stats");
    expect(data).toHaveProperty("revenue_stats");
    expect(data).toHaveProperty("correlation_ad_revenue");
    expect(data).toHaveProperty("correlation_ad_orders");
    expect(data).toHaveProperty("revenue_per_spend");
  });

  test("ad_spend_stats has correct structure", () => {
    const data = loadOutput(workspace);
    const stats = data.ad_spend_stats;
    expect(stats).toHaveProperty("mean");
    expect(stats).toHaveProperty("std");
    expect(stats).toHaveProperty("min");
    expect(stats).toHaveProperty("max");
  });

  test("ad_spend_stats mean is 730 and range is correct", () => {
    const data = loadOutput(workspace);
    const stats = data.ad_spend_stats;
    expect(Math.abs(Number(stats.mean) - 730)).toBeLessThan(0.1);
    expect(Number(stats.min)).toBe(500);
    expect(Number(stats.max)).toBe(1000);
  });

  test("revenue_stats mean is 2930 and range is correct", () => {
    const data = loadOutput(workspace);
    const stats = data.revenue_stats;
    expect(Math.abs(Number(stats.mean) - 2930)).toBeLessThan(0.1);
    expect(Number(stats.min)).toBe(2100);
    expect(Number(stats.max)).toBe(4000);
  });

  test("correlation_ad_revenue is close to 1.0", () => {
    const data = loadOutput(workspace);
    expect(Math.abs(Number(data.correlation_ad_revenue) - 1.0)).toBeLessThan(0.001);
  });

  test("correlation_ad_orders is close to 1.0", () => {
    const data = loadOutput(workspace);
    expect(Math.abs(Number(data.correlation_ad_orders) - 1.0)).toBeLessThan(0.001);
  });

  test("revenue_per_spend is approximately 4.0137", () => {
    const data = loadOutput(workspace);
    expect(Math.abs(Number(data.revenue_per_spend) - 4.0137)).toBeLessThan(0.01);
  });
});

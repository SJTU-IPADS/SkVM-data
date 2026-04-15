import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const OUTPUT_FILE = "output/cleaning_report.json";

function loadOutput(workspace: string) {
  const filePath = join(workspace, OUTPUT_FILE);
  const content = readFileSync(filePath, "utf-8");
  return JSON.parse(content);
}

const workspace = process.env.WORKSPACE_PATH || ".";

// Expected computation:
// Values: 12.5,13.1,11.8,250.0,12.9,14.2,13.5,0.1,11.5,12.0
// Sorted: 0.1,11.5,11.8,12.0,12.5,12.9,13.1,13.5,14.2,250.0
// Q1 (25th pct) = 11.875, Q3 (75th pct) = 13.4
// IQR = 1.525, lower = 11.875 - 2.2875 = 9.5875, upper = 13.4 + 2.2875 = 15.6875
// Outliers: id=4 (250.0), id=8 (0.1)
// Clean values: 12.5,13.1,11.8,12.9,14.2,13.5,11.5,12.0 (8 rows)
// clean_mean = (12.5+13.1+11.8+12.9+14.2+13.5+11.5+12.0)/8 = 101.5/8 = 12.6875
// clean_median = (12.5+12.9)/2 = 12.7
// clean_std (sample, ddof=1): compute from the 8 values

describe("output/cleaning_report.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, OUTPUT_FILE))).toBe(true);
  });

  test("valid JSON format", () => {
    expect(() => loadOutput(workspace)).not.toThrow();
  });

  test("has all required keys", () => {
    const data = loadOutput(workspace);
    expect(data).toHaveProperty("original_row_count");
    expect(data).toHaveProperty("removed_row_ids");
    expect(data).toHaveProperty("clean_row_count");
    expect(data).toHaveProperty("clean_mean");
    expect(data).toHaveProperty("clean_median");
    expect(data).toHaveProperty("clean_std");
  });

  test("original_row_count is 10", () => {
    const data = loadOutput(workspace);
    expect(Number(data.original_row_count)).toBe(10);
  });

  test("removed_row_ids contains outlier rows 4 and 8", () => {
    const data = loadOutput(workspace);
    expect(Array.isArray(data.removed_row_ids)).toBe(true);
    const ids = data.removed_row_ids.map(Number).sort((a: number, b: number) => a - b);
    expect(ids).toContain(4);
    expect(ids).toContain(8);
    expect(ids.length).toBe(2);
  });

  test("clean_row_count is 8", () => {
    const data = loadOutput(workspace);
    expect(Number(data.clean_row_count)).toBe(8);
  });

  test("clean_mean is approximately 12.6875", () => {
    const data = loadOutput(workspace);
    expect(Math.abs(Number(data.clean_mean) - 12.6875)).toBeLessThan(0.001);
  });

  test("clean_median is approximately 12.7", () => {
    const data = loadOutput(workspace);
    expect(Math.abs(Number(data.clean_median) - 12.7)).toBeLessThan(0.001);
  });

  test("clean_std is a positive number", () => {
    const data = loadOutput(workspace);
    expect(Number(data.clean_std)).toBeGreaterThan(0);
    expect(Number(data.clean_std)).toBeLessThan(5);
  });
});

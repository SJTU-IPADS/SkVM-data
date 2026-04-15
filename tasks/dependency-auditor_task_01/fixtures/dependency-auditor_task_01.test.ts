import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const OUTPUT_FILE = "output/audit_report.json";
const workspace = process.env.WORKSPACE_PATH || ".";

function loadOutput(workspace: string) {
  const content = readFileSync(join(workspace, OUTPUT_FILE), "utf-8");
  return JSON.parse(content);
}

describe("output/audit_report.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, OUTPUT_FILE))).toBe(true);
  });

  test("valid JSON format", () => {
    expect(() => loadOutput(workspace)).not.toThrow();
  });

  test("has all required keys", () => {
    const data = loadOutput(workspace);
    expect(data).toHaveProperty("package_name");
    expect(data).toHaveProperty("total_dependencies");
    expect(data).toHaveProperty("production_dependencies");
    expect(data).toHaveProperty("dev_dependencies");
    expect(data).toHaveProperty("potentially_outdated");
    expect(data).toHaveProperty("risk_summary");
    expect(data).toHaveProperty("recommendations");
  });

  test("package_name is sample-app", () => {
    const data = loadOutput(workspace);
    expect(data.package_name).toBe("sample-app");
  });

  test("total_dependencies is 8", () => {
    const data = loadOutput(workspace);
    expect(Number(data.total_dependencies)).toBe(8);
  });

  test("production_dependencies is 6", () => {
    const data = loadOutput(workspace);
    expect(Number(data.production_dependencies)).toBe(6);
  });

  test("dev_dependencies is 2", () => {
    const data = loadOutput(workspace);
    expect(Number(data.dev_dependencies)).toBe(2);
  });

  test("potentially_outdated is a non-empty array with correct structure", () => {
    const data = loadOutput(workspace);
    expect(Array.isArray(data.potentially_outdated)).toBe(true);
    expect(data.potentially_outdated.length).toBeGreaterThan(0);
    for (const entry of data.potentially_outdated) {
      expect(entry).toHaveProperty("name");
      expect(entry).toHaveProperty("current_version");
      expect(entry).toHaveProperty("concern");
      expect(typeof entry.name).toBe("string");
      expect(typeof entry.concern).toBe("string");
    }
  });

  test("risk_summary has high, medium, low keys with non-negative integers", () => {
    const data = loadOutput(workspace);
    expect(data.risk_summary).toHaveProperty("high");
    expect(data.risk_summary).toHaveProperty("medium");
    expect(data.risk_summary).toHaveProperty("low");
    expect(Number(data.risk_summary.high)).toBeGreaterThanOrEqual(0);
    expect(Number(data.risk_summary.medium)).toBeGreaterThanOrEqual(0);
    expect(Number(data.risk_summary.low)).toBeGreaterThanOrEqual(0);
  });

  test("recommendations is a non-empty array of strings", () => {
    const data = loadOutput(workspace);
    expect(Array.isArray(data.recommendations)).toBe(true);
    expect(data.recommendations.length).toBeGreaterThan(0);
    for (const rec of data.recommendations) {
      expect(typeof rec).toBe("string");
      expect(rec.length).toBeGreaterThan(5);
    }
  });
});

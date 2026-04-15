import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const workspace = process.env.WORKSPACE_PATH || ".";

function loadJSON(filename: string) {
  const p = join(workspace, filename);
  if (!existsSync(p)) return null;
  try {
    return JSON.parse(readFileSync(p, "utf-8"));
  } catch {
    return null;
  }
}

function fileExists(filename: string) {
  return existsSync(join(workspace, filename));
}

describe("comparison_report.json", () => {
  test("comparison_report.json exists", () => {
    expect(fileExists("comparison_report.json")).toBe(true);
  });

  test("comparison_report.json has required top-level keys", () => {
    const data = loadJSON("comparison_report.json");
    expect(data).not.toBeNull();
    expect(data).toHaveProperty("failures");
    expect(data).toHaveProperty("common_patterns");
    expect(data).toHaveProperty("key_differences");
    expect(data).toHaveProperty("priority_recommendation");
  });

  test("failures array contains exactly 2 entries", () => {
    const data = loadJSON("comparison_report.json");
    expect(Array.isArray(data.failures)).toBe(true);
    expect(data.failures.length).toBe(2);
  });

  test("each failure has all required fields", () => {
    const data = loadJSON("comparison_report.json");
    for (const f of data.failures) {
      expect(f).toHaveProperty("id");
      expect(f).toHaveProperty("name");
      expect(f).toHaveProperty("mttd_minutes");
      expect(f).toHaveProperty("mttr_minutes");
      expect(f).toHaveProperty("root_cause_category");
      expect(f).toHaveProperty("key_vulnerabilities");
    }
  });

  test("failure IDs are A and B", () => {
    const data = loadJSON("comparison_report.json");
    const ids = data.failures.map((f: any) => f.id).sort();
    expect(ids).toEqual(["A", "B"]);
  });

  test("mttd and mttr are positive integers", () => {
    const data = loadJSON("comparison_report.json");
    for (const f of data.failures) {
      expect(typeof f.mttd_minutes).toBe("number");
      expect(typeof f.mttr_minutes).toBe("number");
      expect(f.mttd_minutes).toBeGreaterThan(0);
      expect(f.mttr_minutes).toBeGreaterThan(0);
    }
  });

  test("Failure A mttd_minutes is approximately 150 (±10)", () => {
    const data = loadJSON("comparison_report.json");
    const failureA = data.failures.find((f: any) => f.id === "A");
    expect(failureA).not.toBeUndefined();
    expect(Math.abs(failureA.mttd_minutes - 150)).toBeLessThanOrEqual(10);
  });

  test("key_vulnerabilities has at least 2 entries per failure", () => {
    const data = loadJSON("comparison_report.json");
    for (const f of data.failures) {
      expect(Array.isArray(f.key_vulnerabilities)).toBe(true);
      expect(f.key_vulnerabilities.length).toBeGreaterThanOrEqual(2);
    }
  });

  test("common_patterns has at least 2 entries", () => {
    const data = loadJSON("comparison_report.json");
    expect(Array.isArray(data.common_patterns)).toBe(true);
    expect(data.common_patterns.length).toBeGreaterThanOrEqual(2);
  });

  test("key_differences has at least 2 entries", () => {
    const data = loadJSON("comparison_report.json");
    expect(Array.isArray(data.key_differences)).toBe(true);
    expect(data.key_differences.length).toBeGreaterThanOrEqual(2);
  });

  test("priority_recommendation is a non-empty string", () => {
    const data = loadJSON("comparison_report.json");
    expect(typeof data.priority_recommendation).toBe("string");
    expect(data.priority_recommendation.length).toBeGreaterThan(10);
  });
});

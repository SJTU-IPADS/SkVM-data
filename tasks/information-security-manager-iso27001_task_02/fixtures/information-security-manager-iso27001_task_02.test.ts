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

const VALID_CATEGORIES = ["Security Breach", "Malware", "Data Leakage", "System Compromise", "Policy Violation", "Configuration Error"];
const VALID_SEVERITIES = ["Critical", "High", "Medium", "Low"];

describe("incidents.json", () => {
  test("incidents.json exists", () => {
    expect(fileExists("incidents.json")).toBe(true);
  });

  test("incidents.json contains exactly 4 incidents", () => {
    const data = loadJSON("incidents.json");
    expect(Array.isArray(data)).toBe(true);
    expect(data.length).toBe(4);
  });

  test("incident IDs are INC-001 through INC-004", () => {
    const data = loadJSON("incidents.json");
    const ids = data.map((i: any) => i.id).sort();
    expect(ids).toEqual(["INC-001", "INC-002", "INC-003", "INC-004"]);
  });

  test("each incident has all required fields", () => {
    const data = loadJSON("incidents.json");
    for (const inc of data) {
      expect(inc).toHaveProperty("id");
      expect(inc).toHaveProperty("title");
      expect(inc).toHaveProperty("category");
      expect(inc).toHaveProperty("severity");
      expect(inc).toHaveProperty("response_time_hours");
      expect(inc).toHaveProperty("containment_actions");
      expect(inc).toHaveProperty("affected_data");
    }
  });

  test("category values are valid enum members", () => {
    const data = loadJSON("incidents.json");
    for (const inc of data) {
      expect(VALID_CATEGORIES).toContain(inc.category);
    }
  });

  test("severity values are valid enum members", () => {
    const data = loadJSON("incidents.json");
    for (const inc of data) {
      expect(VALID_SEVERITIES).toContain(inc.severity);
    }
  });

  test("containment_actions is an array with at least 2 items per incident", () => {
    const data = loadJSON("incidents.json");
    for (const inc of data) {
      expect(Array.isArray(inc.containment_actions)).toBe(true);
      expect(inc.containment_actions.length).toBeGreaterThanOrEqual(2);
    }
  });

  test("affected_data is boolean for all incidents", () => {
    const data = loadJSON("incidents.json");
    for (const inc of data) {
      expect(typeof inc.affected_data).toBe("boolean");
    }
  });
});

describe("response_stats.json", () => {
  test("response_stats.json exists", () => {
    expect(fileExists("response_stats.json")).toBe(true);
  });

  test("response_stats.json has all required fields", () => {
    const data = loadJSON("response_stats.json");
    expect(data).toHaveProperty("total_incidents");
    expect(data).toHaveProperty("critical_count");
    expect(data).toHaveProperty("high_count");
    expect(data).toHaveProperty("medium_count");
    expect(data).toHaveProperty("low_count");
    expect(data).toHaveProperty("data_breach_incidents");
    expect(data).toHaveProperty("average_response_time_hours");
  });

  test("total_incidents is 4", () => {
    const data = loadJSON("response_stats.json");
    expect(data.total_incidents).toBe(4);
  });

  test("severity counts sum to 4", () => {
    const data = loadJSON("response_stats.json");
    const sum = data.critical_count + data.high_count + data.medium_count + data.low_count;
    expect(sum).toBe(4);
  });

  test("data_breach_incidents matches affected_data count in incidents.json", () => {
    const incidents = loadJSON("incidents.json");
    const stats = loadJSON("response_stats.json");
    const expectedBreaches = incidents.filter((i: any) => i.affected_data === true).length;
    expect(stats.data_breach_incidents).toBe(expectedBreaches);
  });

  test("average_response_time_hours matches computed mean", () => {
    const incidents = loadJSON("incidents.json");
    const stats = loadJSON("response_stats.json");
    const times = incidents.map((i: any) => i.response_time_hours);
    const mean = Math.round((times.reduce((a: number, b: number) => a + b, 0) / times.length) * 100) / 100;
    expect(Math.abs(stats.average_response_time_hours - mean)).toBeLessThan(0.01);
  });
});

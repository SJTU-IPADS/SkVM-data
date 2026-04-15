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

describe("analysis_report.json", () => {
  test("analysis_report.json exists", () => {
    expect(fileExists("analysis_report.json")).toBe(true);
  });

  test("analysis_report.json is valid JSON with required top-level keys", () => {
    const data = loadJSON("analysis_report.json");
    expect(data).not.toBeNull();
    expect(data).toHaveProperty("incident_name");
    expect(data).toHaveProperty("duration_minutes");
    expect(data).toHaveProperty("users_affected");
    expect(data).toHaveProperty("timeline");
    expect(data).toHaveProperty("trigger");
    expect(data).toHaveProperty("cascade_chain");
    expect(data).toHaveProperty("root_causes");
    expect(data).toHaveProperty("recommendations");
    expect(data).toHaveProperty("mttd_minutes");
    expect(data).toHaveProperty("mttr_minutes");
  });

  test("duration_minutes is 97", () => {
    const data = loadJSON("analysis_report.json");
    expect(data.duration_minutes).toBe(97);
  });

  test("users_affected is 450000", () => {
    const data = loadJSON("analysis_report.json");
    expect(data.users_affected).toBe(450000);
  });

  test("mttd_minutes is 5", () => {
    const data = loadJSON("analysis_report.json");
    expect(data.mttd_minutes).toBe(5);
  });

  test("mttr_minutes is 97", () => {
    const data = loadJSON("analysis_report.json");
    expect(data.mttr_minutes).toBe(97);
  });

  test("timeline contains at least 5 entries with required fields", () => {
    const data = loadJSON("analysis_report.json");
    expect(Array.isArray(data.timeline)).toBe(true);
    expect(data.timeline.length).toBeGreaterThanOrEqual(5);
    for (const entry of data.timeline) {
      expect(entry).toHaveProperty("time");
      expect(entry).toHaveProperty("event");
    }
  });

  test("root_causes has human_factors and organizational_factors arrays", () => {
    const data = loadJSON("analysis_report.json");
    expect(data.root_causes).toHaveProperty("human_factors");
    expect(data.root_causes).toHaveProperty("organizational_factors");
    expect(Array.isArray(data.root_causes.human_factors)).toBe(true);
    expect(Array.isArray(data.root_causes.organizational_factors)).toBe(true);
  });

  test("human_factors has at least 2 entries", () => {
    const data = loadJSON("analysis_report.json");
    expect(data.root_causes.human_factors.length).toBeGreaterThanOrEqual(2);
  });

  test("organizational_factors has at least 2 entries", () => {
    const data = loadJSON("analysis_report.json");
    expect(data.root_causes.organizational_factors.length).toBeGreaterThanOrEqual(2);
  });

  test("recommendations has at least 3 entries with priority and action", () => {
    const data = loadJSON("analysis_report.json");
    expect(Array.isArray(data.recommendations)).toBe(true);
    expect(data.recommendations.length).toBeGreaterThanOrEqual(3);
    const validPriorities = ["Urgent", "Important", "Long-term"];
    for (const rec of data.recommendations) {
      expect(rec).toHaveProperty("action");
      expect(rec).toHaveProperty("priority");
      expect(validPriorities).toContain(rec.priority);
    }
  });

  test("cascade_chain is a non-empty array", () => {
    const data = loadJSON("analysis_report.json");
    expect(Array.isArray(data.cascade_chain)).toBe(true);
    expect(data.cascade_chain.length).toBeGreaterThan(0);
  });
});

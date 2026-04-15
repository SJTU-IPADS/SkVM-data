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

describe("interview_loop.json", () => {
  test("interview_loop.json exists", () => {
    expect(fileExists("interview_loop.json")).toBe(true);
  });

  test("file has all required top-level fields", () => {
    const data = loadJSON("interview_loop.json");
    expect(data).not.toBeNull();
    expect(data).toHaveProperty("role");
    expect(data).toHaveProperty("level");
    expect(data).toHaveProperty("rounds");
    expect(data).toHaveProperty("total_rounds");
    expect(data).toHaveProperty("total_duration_minutes");
    expect(data).toHaveProperty("required_competencies");
    expect(data).toHaveProperty("hiring_committee_size");
    expect(data).toHaveProperty("pass_rate_target_percent");
  });

  test("role is Senior Software Engineer and level is Senior", () => {
    const data = loadJSON("interview_loop.json");
    expect(data.role).toBe("Senior Software Engineer");
    expect(data.level).toBe("Senior");
  });

  test("rounds array has exactly 4 entries", () => {
    const data = loadJSON("interview_loop.json");
    expect(Array.isArray(data.rounds)).toBe(true);
    expect(data.rounds.length).toBe(4);
  });

  test("round 1 is Technical Phone Screen with 45 minutes", () => {
    const data = loadJSON("interview_loop.json");
    const r = data.rounds.find((r: any) => r.round_number === 1);
    expect(r).not.toBeUndefined();
    expect(r.duration_minutes).toBe(45);
    expect(r.name.toLowerCase()).toContain("phone");
  });

  test("round 2 is System Design with 60 minutes", () => {
    const data = loadJSON("interview_loop.json");
    const r = data.rounds.find((r: any) => r.round_number === 2);
    expect(r).not.toBeUndefined();
    expect(r.duration_minutes).toBe(60);
    expect(r.name.toLowerCase()).toContain("system");
  });

  test("round 3 is Coding with 60 minutes", () => {
    const data = loadJSON("interview_loop.json");
    const r = data.rounds.find((r: any) => r.round_number === 3);
    expect(r).not.toBeUndefined();
    expect(r.duration_minutes).toBe(60);
  });

  test("round 4 is Behavioral with 30 minutes", () => {
    const data = loadJSON("interview_loop.json");
    const r = data.rounds.find((r: any) => r.round_number === 4);
    expect(r).not.toBeUndefined();
    expect(r.duration_minutes).toBe(30);
  });

  test("total_rounds is 4", () => {
    const data = loadJSON("interview_loop.json");
    expect(data.total_rounds).toBe(4);
  });

  test("total_duration_minutes equals sum of round durations", () => {
    const data = loadJSON("interview_loop.json");
    const sum = data.rounds.reduce((a: number, r: any) => a + r.duration_minutes, 0);
    expect(data.total_duration_minutes).toBe(sum);
    expect(data.total_duration_minutes).toBe(195);
  });

  test("each round has at least 2 focus_areas and 2 scorecard_dimensions", () => {
    const data = loadJSON("interview_loop.json");
    for (const round of data.rounds) {
      expect(Array.isArray(round.focus_areas)).toBe(true);
      expect(round.focus_areas.length).toBeGreaterThanOrEqual(2);
      expect(Array.isArray(round.scorecard_dimensions)).toBe(true);
      expect(round.scorecard_dimensions.length).toBeGreaterThanOrEqual(2);
    }
  });

  test("required_competencies has at least 4 entries", () => {
    const data = loadJSON("interview_loop.json");
    expect(Array.isArray(data.required_competencies)).toBe(true);
    expect(data.required_competencies.length).toBeGreaterThanOrEqual(4);
  });

  test("hiring_committee_size is between 3 and 6 inclusive", () => {
    const data = loadJSON("interview_loop.json");
    expect(data.hiring_committee_size).toBeGreaterThanOrEqual(3);
    expect(data.hiring_committee_size).toBeLessThanOrEqual(6);
  });

  test("pass_rate_target_percent is between 10 and 30 inclusive", () => {
    const data = loadJSON("interview_loop.json");
    expect(data.pass_rate_target_percent).toBeGreaterThanOrEqual(10);
    expect(data.pass_rate_target_percent).toBeLessThanOrEqual(30);
  });
});

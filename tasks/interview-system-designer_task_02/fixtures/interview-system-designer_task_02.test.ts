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

// Expected values computed from the input data
const EXPECTED_CANDIDATES: Record<string, { avg: number; rec: string; agreement: boolean }> = {
  "C1": { avg: 3.7, rec: "Hire", agreement: true },       // (4+4+3)/3 = 3.667 -> 3.7, max-min=1 <=1
  "C2": { avg: 2.3, rec: "No Hire", agreement: true },    // (2+3+2)/3 = 2.333 -> 2.3, max-min=1 <=1
  "C3": { avg: 2.7, rec: "No Hire", agreement: true },    // (3+2+3)/3 = 2.667 -> 2.7, max-min=1 <=1
  "C4": { avg: 1.3, rec: "No Hire", agreement: true },    // (1+1+2)/3 = 1.333 -> 1.3, max-min=1 <=1
  "C5": { avg: 3.7, rec: "Hire", agreement: true },       // (4+3+4)/3 = 3.667 -> 3.7, max-min=1 <=1
};

describe("calibration_report.json", () => {
  test("calibration_report.json exists", () => {
    expect(fileExists("calibration_report.json")).toBe(true);
  });

  test("file has required top-level keys", () => {
    const data = loadJSON("calibration_report.json");
    expect(data).not.toBeNull();
    expect(data).toHaveProperty("candidates");
    expect(data).toHaveProperty("interviewers");
    expect(data).toHaveProperty("summary");
  });

  test("candidates array has exactly 5 entries", () => {
    const data = loadJSON("calibration_report.json");
    expect(Array.isArray(data.candidates)).toBe(true);
    expect(data.candidates.length).toBe(5);
  });

  test("candidate IDs are C1 through C5", () => {
    const data = loadJSON("calibration_report.json");
    const ids = data.candidates.map((c: any) => c.id).sort();
    expect(ids).toEqual(["C1", "C2", "C3", "C4", "C5"]);
  });

  test("candidate C1 average is 3.7 and recommendation is Hire", () => {
    const data = loadJSON("calibration_report.json");
    const c = data.candidates.find((c: any) => c.id === "C1");
    expect(c).not.toBeUndefined();
    expect(Math.abs(c.average_score - 3.7)).toBeLessThan(0.1);
    expect(c.recommendation).toBe("Hire");
  });

  test("candidate C4 average is 1.3 and recommendation is No Hire", () => {
    const data = loadJSON("calibration_report.json");
    const c = data.candidates.find((c: any) => c.id === "C4");
    expect(c).not.toBeUndefined();
    expect(Math.abs(c.average_score - 1.3)).toBeLessThan(0.1);
    expect(c.recommendation).toBe("No Hire");
  });

  test("interviewers array has exactly 3 entries with IDs A, B, C", () => {
    const data = loadJSON("calibration_report.json");
    expect(Array.isArray(data.interviewers)).toBe(true);
    expect(data.interviewers.length).toBe(3);
    const ids = data.interviewers.map((i: any) => i.id).sort();
    expect(ids).toEqual(["A", "B", "C"]);
  });

  test("summary total_candidates is 5", () => {
    const data = loadJSON("calibration_report.json");
    expect(data.summary.total_candidates).toBe(5);
  });

  test("summary hire_count is 2 and no_hire_count is 3", () => {
    const data = loadJSON("calibration_report.json");
    expect(data.summary.hire_count).toBe(2);
    expect(data.summary.no_hire_count).toBe(3);
  });

  test("overall_team_average is approximately 2.73 (±0.05)", () => {
    // sum of all 15 scores: 4+4+3+2+3+2+3+2+3+1+1+2+4+3+4 = 41, /15 = 2.7333
    const data = loadJSON("calibration_report.json");
    expect(Math.abs(data.summary.overall_team_average - 2.73)).toBeLessThan(0.05);
  });

  test("full_agreement_rate_percent is 100.0 (all candidates within 1 point)", () => {
    const data = loadJSON("calibration_report.json");
    expect(Math.abs(data.summary.full_agreement_rate_percent - 100.0)).toBeLessThan(0.1);
  });
});

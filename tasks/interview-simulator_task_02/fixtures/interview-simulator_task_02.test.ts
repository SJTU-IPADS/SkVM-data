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

const EXPECTED_MODULES = ["Product Sense", "Analytical Thinking", "Behavioral", "Execution"];
const MODULE_TIME: Record<string, number> = {
  "Product Sense": 15,
  "Analytical Thinking": 10,
  "Behavioral": 10,
  "Execution": 10,
};
const MODULE_PREFIX: Record<string, string> = {
  "Product Sense": "PS",
  "Analytical Thinking": "AT",
  "Behavioral": "BH",
  "Execution": "EX",
};

describe("pm_interview_questions.json", () => {
  test("pm_interview_questions.json exists", () => {
    expect(fileExists("pm_interview_questions.json")).toBe(true);
  });

  test("file has required top-level fields", () => {
    const data = loadJSON("pm_interview_questions.json");
    expect(data).not.toBeNull();
    expect(data).toHaveProperty("role");
    expect(data).toHaveProperty("level");
    expect(data).toHaveProperty("context");
    expect(data).toHaveProperty("modules");
    expect(data).toHaveProperty("total_questions");
    expect(data).toHaveProperty("estimated_duration_minutes");
  });

  test("role is Product Manager, level is Mid", () => {
    const data = loadJSON("pm_interview_questions.json");
    expect(data.role).toBe("Product Manager");
    expect(data.level).toBe("Mid");
  });

  test("modules array has exactly 4 entries", () => {
    const data = loadJSON("pm_interview_questions.json");
    expect(Array.isArray(data.modules)).toBe(true);
    expect(data.modules.length).toBe(4);
  });

  test("module names match expected values", () => {
    const data = loadJSON("pm_interview_questions.json");
    const names = data.modules.map((m: any) => m.name);
    for (const expected of EXPECTED_MODULES) {
      expect(names).toContain(expected);
    }
  });

  test("each module has exactly 2 questions", () => {
    const data = loadJSON("pm_interview_questions.json");
    for (const mod of data.modules) {
      expect(Array.isArray(mod.questions)).toBe(true);
      expect(mod.questions.length).toBe(2);
    }
  });

  test("question IDs follow correct prefix pattern per module", () => {
    const data = loadJSON("pm_interview_questions.json");
    for (const mod of data.modules) {
      const prefix = MODULE_PREFIX[mod.name];
      if (!prefix) continue;
      const ids = mod.questions.map((q: any) => q.id);
      expect(ids).toContain(`${prefix}-01`);
      expect(ids).toContain(`${prefix}-02`);
    }
  });

  test("time_minutes per question matches expected values by module", () => {
    const data = loadJSON("pm_interview_questions.json");
    for (const mod of data.modules) {
      const expectedTime = MODULE_TIME[mod.name];
      if (expectedTime === undefined) continue;
      for (const q of mod.questions) {
        expect(q.time_minutes).toBe(expectedTime);
      }
    }
  });

  test("each question has at least 2 evaluation_criteria", () => {
    const data = loadJSON("pm_interview_questions.json");
    for (const mod of data.modules) {
      for (const q of mod.questions) {
        expect(Array.isArray(q.evaluation_criteria)).toBe(true);
        expect(q.evaluation_criteria.length).toBeGreaterThanOrEqual(2);
      }
    }
  });

  test("total_questions is 8", () => {
    const data = loadJSON("pm_interview_questions.json");
    expect(data.total_questions).toBe(8);
  });

  test("estimated_duration_minutes equals sum of all time_minutes", () => {
    const data = loadJSON("pm_interview_questions.json");
    let totalTime = 0;
    for (const mod of data.modules) {
      for (const q of mod.questions) {
        totalTime += q.time_minutes;
      }
    }
    expect(data.estimated_duration_minutes).toBe(totalTime);
  });
});

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

const VALID_VERDICTS = ["Strong Hire", "Hire", "Lean Hire", "Lean No Hire", "No Hire"];

describe("interview_scorecard.json", () => {
  test("interview_scorecard.json exists", () => {
    expect(fileExists("interview_scorecard.json")).toBe(true);
  });

  test("scorecard has required top-level fields", () => {
    const data = loadJSON("interview_scorecard.json");
    expect(data).not.toBeNull();
    expect(data).toHaveProperty("role");
    expect(data).toHaveProperty("level");
    expect(data).toHaveProperty("focus");
    expect(data).toHaveProperty("questions");
    expect(data).toHaveProperty("overall_score");
    expect(data).toHaveProperty("verdict");
    expect(data).toHaveProperty("key_strengths");
    expect(data).toHaveProperty("areas_for_improvement");
    expect(data).toHaveProperty("recommended_study_topics");
  });

  test("role, level, focus match expected values", () => {
    const data = loadJSON("interview_scorecard.json");
    expect(data.role).toBe("Senior Backend Engineer");
    expect(data.level).toBe("Senior");
    expect(data.focus).toBe("Distributed Systems");
  });

  test("questions array has exactly 3 entries", () => {
    const data = loadJSON("interview_scorecard.json");
    expect(Array.isArray(data.questions)).toBe(true);
    expect(data.questions.length).toBe(3);
  });

  test("each question has required fields with valid types", () => {
    const data = loadJSON("interview_scorecard.json");
    for (const q of data.questions) {
      expect(q).toHaveProperty("number");
      expect(q).toHaveProperty("module");
      expect(q).toHaveProperty("score");
      expect(q).toHaveProperty("strengths");
      expect(q).toHaveProperty("improvements");
      expect(typeof q.score).toBe("number");
      expect(q.score).toBeGreaterThanOrEqual(1);
      expect(q.score).toBeLessThanOrEqual(10);
    }
  });

  test("question numbers are 1, 2, 3", () => {
    const data = loadJSON("interview_scorecard.json");
    const numbers = data.questions.map((q: any) => q.number).sort();
    expect(numbers).toEqual([1, 2, 3]);
  });

  test("overall_score is the average of question scores (±0.5 tolerance)", () => {
    const data = loadJSON("interview_scorecard.json");
    const scores = data.questions.map((q: any) => q.score);
    const avg = scores.reduce((a: number, b: number) => a + b, 0) / scores.length;
    expect(Math.abs(data.overall_score - avg)).toBeLessThanOrEqual(0.5);
  });

  test("verdict is a valid enum value", () => {
    const data = loadJSON("interview_scorecard.json");
    expect(VALID_VERDICTS).toContain(data.verdict);
  });

  test("key_strengths has at least 2 entries", () => {
    const data = loadJSON("interview_scorecard.json");
    expect(Array.isArray(data.key_strengths)).toBe(true);
    expect(data.key_strengths.length).toBeGreaterThanOrEqual(2);
  });

  test("areas_for_improvement has at least 2 entries", () => {
    const data = loadJSON("interview_scorecard.json");
    expect(Array.isArray(data.areas_for_improvement)).toBe(true);
    expect(data.areas_for_improvement.length).toBeGreaterThanOrEqual(2);
  });

  test("recommended_study_topics has at least 2 entries", () => {
    const data = loadJSON("interview_scorecard.json");
    expect(Array.isArray(data.recommended_study_topics)).toBe(true);
    expect(data.recommended_study_topics.length).toBeGreaterThanOrEqual(2);
  });
});

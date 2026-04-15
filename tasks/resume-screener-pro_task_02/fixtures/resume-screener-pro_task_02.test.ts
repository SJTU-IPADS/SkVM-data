import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const workspace = process.cwd();

function loadJson(filename: string) {
  const p = join(workspace, filename);
  if (!existsSync(p)) return null;
  try { return JSON.parse(readFileSync(p, "utf-8")); } catch { return null; }
}

describe("scorecard.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "scorecard.json"))).toBe(true);
  });

  test("has mission field as a non-empty string", () => {
    const data = loadJson("scorecard.json");
    expect(data).not.toBeNull();
    expect(typeof data.mission).toBe("string");
    expect(data.mission.length).toBeGreaterThan(15);
  });

  test("has exactly 3 outcomes", () => {
    const data = loadJson("scorecard.json");
    expect(Array.isArray(data?.outcomes)).toBe(true);
    expect(data?.outcomes?.length).toBe(3);
  });

  test("outcomes are non-empty strings", () => {
    const data = loadJson("scorecard.json");
    for (const outcome of data?.outcomes ?? []) {
      expect(typeof outcome).toBe("string");
      expect(outcome.length).toBeGreaterThan(10);
    }
  });

  test("has exactly 4 competencies", () => {
    const data = loadJson("scorecard.json");
    expect(Array.isArray(data?.competencies)).toBe(true);
    expect(data?.competencies?.length).toBe(4);
  });

  test("each competency has name, description, level_required", () => {
    const data = loadJson("scorecard.json");
    const validLevels = ["Must Have", "Nice to Have"];
    for (const comp of data?.competencies ?? []) {
      expect(typeof comp.name).toBe("string");
      expect(typeof comp.description).toBe("string");
      expect(validLevels).toContain(comp.level_required);
    }
  });
});

describe("interview_questions.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "interview_questions.json"))).toBe(true);
  });

  test("has questions array with exactly 8 entries", () => {
    const data = loadJson("interview_questions.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.questions)).toBe(true);
    expect(data.questions.length).toBe(8);
  });

  test("question IDs are Q1 through Q8", () => {
    const data = loadJson("interview_questions.json");
    const ids = (data?.questions ?? []).map((q: any) => q.question_id);
    for (let i = 1; i <= 8; i++) {
      expect(ids).toContain(`Q${i}`);
    }
  });

  test("sections A, B, C, D are all represented", () => {
    const data = loadJson("interview_questions.json");
    const sections = new Set((data?.questions ?? []).map((q: any) => q.section));
    expect(sections.has("A")).toBe(true);
    expect(sections.has("B")).toBe(true);
    expect(sections.has("C")).toBe(true);
    expect(sections.has("D")).toBe(true);
  });

  test("each question has question_text and probe_focus fields", () => {
    const data = loadJson("interview_questions.json");
    for (const q of data?.questions ?? []) {
      expect(typeof q.question_text).toBe("string");
      expect(q.question_text.length).toBeGreaterThan(10);
      expect(typeof q.probe_focus).toBe("string");
    }
  });

  test("section B questions have follow_up set (not null)", () => {
    const data = loadJson("interview_questions.json");
    const sectionB = (data?.questions ?? []).filter((q: any) => q.section === "B");
    expect(sectionB.length).toBe(2);
    for (const q of sectionB) {
      expect(q.follow_up).not.toBeNull();
      expect(typeof q.follow_up).toBe("string");
      expect(q.follow_up.length).toBeGreaterThan(10);
    }
  });

  test("section A and C questions exist with correct counts", () => {
    const data = loadJson("interview_questions.json");
    const sectionA = (data?.questions ?? []).filter((q: any) => q.section === "A");
    const sectionC = (data?.questions ?? []).filter((q: any) => q.section === "C");
    expect(sectionA.length).toBe(2);
    expect(sectionC.length).toBe(2);
  });
});

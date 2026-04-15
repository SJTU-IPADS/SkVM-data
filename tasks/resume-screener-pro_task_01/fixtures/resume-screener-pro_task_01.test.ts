import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const workspace = process.cwd();

function loadJson(filename: string) {
  const p = join(workspace, filename);
  if (!existsSync(p)) return null;
  try { return JSON.parse(readFileSync(p, "utf-8")); } catch { return null; }
}

describe("screening_report.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "screening_report.json"))).toBe(true);
  });

  test("has candidates array", () => {
    const data = loadJson("screening_report.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.candidates)).toBe(true);
  });

  test("has exactly 3 candidates", () => {
    const data = loadJson("screening_report.json");
    expect(data?.candidates?.length).toBe(3);
  });

  test("required fields: id, name, match_score, ats_score, core_strengths, risk_points, recommendation", () => {
    const data = loadJson("screening_report.json");
    for (const c of data?.candidates ?? []) {
      expect(typeof c.id).toBe("string");
      expect(typeof c.name).toBe("string");
      expect(typeof c.match_score).toBe("number");
      expect(typeof c.ats_score).toBe("number");
      expect(Array.isArray(c.core_strengths)).toBe(true);
      expect(Array.isArray(c.risk_points)).toBe(true);
      expect(["Advance", "Maybe", "Pass"]).toContain(c.recommendation);
    }
  });

  test("match_score is between 0 and 10 for all candidates", () => {
    const data = loadJson("screening_report.json");
    for (const c of data?.candidates ?? []) {
      expect(c.match_score).toBeGreaterThanOrEqual(0);
      expect(c.match_score).toBeLessThanOrEqual(10);
    }
  });

  test("Alex Chen (C1) gets Advance recommendation", () => {
    const data = loadJson("screening_report.json");
    const alex = (data?.candidates ?? []).find((c: any) => c.id === "C1" || /alex/i.test(c.name ?? ""));
    expect(alex).toBeDefined();
    expect(alex?.recommendation).toBe("Advance");
    expect(alex?.match_score).toBeGreaterThanOrEqual(7.0);
  });

  test("James Park (C3) gets Advance recommendation", () => {
    const data = loadJson("screening_report.json");
    const james = (data?.candidates ?? []).find((c: any) => c.id === "C3" || /james/i.test(c.name ?? ""));
    expect(james).toBeDefined();
    expect(james?.recommendation).toBe("Advance");
    expect(james?.match_score).toBeGreaterThanOrEqual(7.0);
  });

  test("Maria Gomez (C2) gets Pass or Maybe (not Advance)", () => {
    const data = loadJson("screening_report.json");
    const maria = (data?.candidates ?? []).find((c: any) => c.id === "C2" || /maria/i.test(c.name ?? ""));
    expect(maria).toBeDefined();
    expect(maria?.recommendation).not.toBe("Advance");
    expect(maria?.match_score).toBeLessThan(7.0);
  });
});

describe("shortlist.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "shortlist.json"))).toBe(true);
  });

  test("has shortlist array with 3 entries", () => {
    const data = loadJson("shortlist.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.shortlist)).toBe(true);
    expect(data.shortlist.length).toBe(3);
  });

  test("entries have rank, id, name, match_score, recommendation", () => {
    const data = loadJson("shortlist.json");
    for (const s of data?.shortlist ?? []) {
      expect(typeof s.rank).toBe("number");
      expect(typeof s.id).toBe("string");
      expect(typeof s.match_score).toBe("number");
    }
  });

  test("sorted by match_score descending", () => {
    const data = loadJson("shortlist.json");
    const scores = (data?.shortlist ?? []).map((s: any) => s.match_score);
    for (let i = 0; i < scores.length - 1; i++) {
      expect(scores[i]).toBeGreaterThanOrEqual(scores[i + 1]);
    }
  });

  test("Maria Gomez is ranked last (rank 3)", () => {
    const data = loadJson("shortlist.json");
    const last = (data?.shortlist ?? []).find((s: any) => s.rank === 3);
    expect(last).toBeDefined();
    expect(/maria|C2/i.test(last?.name ?? last?.id ?? "")).toBe(true);
  });
});

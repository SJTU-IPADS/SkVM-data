import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const workspace = process.cwd();

function loadJson(filename: string) {
  const p = join(workspace, filename);
  if (!existsSync(p)) return null;
  try { return JSON.parse(readFileSync(p, "utf-8")); } catch { return null; }
}

function approxEqual(a: number, b: number, tol = 0.05): boolean {
  return Math.abs(a - b) <= tol;
}

describe("investment_scores.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "investment_scores.json"))).toBe(true);
  });

  test("has proposals array with 4 entries", () => {
    const data = loadJson("investment_scores.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.proposals)).toBe(true);
    expect(data.proposals.length).toBe(4);
  });

  test("INV-001 total_score is approximately 7.75", () => {
    const data = loadJson("investment_scores.json");
    const p = (data?.proposals ?? []).find((x: any) => x.id === "INV-001");
    expect(p).toBeDefined();
    expect(approxEqual(p?.total_score ?? 0, 7.75, 0.1)).toBe(true);
  });

  test("INV-002 total_score is approximately 5.25", () => {
    const data = loadJson("investment_scores.json");
    const p = (data?.proposals ?? []).find((x: any) => x.id === "INV-002");
    expect(p).toBeDefined();
    expect(approxEqual(p?.total_score ?? 0, 5.25, 0.1)).toBe(true);
  });

  test("INV-003 total_score is approximately 6.40", () => {
    const data = loadJson("investment_scores.json");
    const p = (data?.proposals ?? []).find((x: any) => x.id === "INV-003");
    expect(p).toBeDefined();
    expect(approxEqual(p?.total_score ?? 0, 6.40, 0.1)).toBe(true);
  });

  test("INV-004 total_score is approximately 6.75", () => {
    const data = loadJson("investment_scores.json");
    const p = (data?.proposals ?? []).find((x: any) => x.id === "INV-004");
    expect(p).toBeDefined();
    expect(approxEqual(p?.total_score ?? 0, 6.75, 0.1)).toBe(true);
  });
});

describe("investment_ranking.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "investment_ranking.json"))).toBe(true);
  });

  test("has ranked_proposals array with 4 entries", () => {
    const data = loadJson("investment_ranking.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.ranked_proposals)).toBe(true);
    expect(data.ranked_proposals.length).toBe(4);
  });

  test("INV-001 is rank 1", () => {
    const data = loadJson("investment_ranking.json");
    const top = (data?.ranked_proposals ?? [])[0];
    expect(top?.id).toBe("INV-001");
    expect(top?.rank).toBe(1);
  });

  test("INV-001 recommendation is Approve", () => {
    const data = loadJson("investment_ranking.json");
    const p = (data?.ranked_proposals ?? []).find((x: any) => x.id === "INV-001");
    expect(p?.recommendation).toBe("Approve");
  });

  test("INV-002 is ranked last (rank 4)", () => {
    const data = loadJson("investment_ranking.json");
    const ranked = data?.ranked_proposals ?? [];
    const inv002 = ranked.find((x: any) => x.id === "INV-002");
    expect(inv002?.rank).toBe(4);
  });

  test("proposals have rank, id, name, total_score, recommendation fields", () => {
    const data = loadJson("investment_ranking.json");
    for (const p of data?.ranked_proposals ?? []) {
      expect(typeof p.rank).toBe("number");
      expect(typeof p.id).toBe("string");
      expect(typeof p.total_score).toBe("number");
      expect(typeof p.recommendation).toBe("string");
    }
  });
});

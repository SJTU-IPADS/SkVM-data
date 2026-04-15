import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const workspace = process.cwd();

function loadJson(filename: string) {
  const p = join(workspace, filename);
  if (!existsSync(p)) return null;
  try { return JSON.parse(readFileSync(p, "utf-8")); } catch { return null; }
}

const EXPECTED_MARKETS = ["USA", "EU", "Canada", "Australia", "Japan"];

describe("market_matrix.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "market_matrix.json"))).toBe(true);
  });

  test("has markets array with 5 entries", () => {
    const data = loadJson("market_matrix.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.markets)).toBe(true);
    expect(data.markets.length).toBe(5);
  });

  test("all 5 expected markets are present", () => {
    const data = loadJson("market_matrix.json");
    const markets = (data?.markets ?? []).map((m: any) => m.market);
    for (const expected of EXPECTED_MARKETS) {
      expect(markets).toContain(expected);
    }
  });

  test("USA and EU are phase 1", () => {
    const data = loadJson("market_matrix.json");
    const markets = data?.markets ?? [];
    const usa = markets.find((m: any) => m.market === "USA");
    const eu = markets.find((m: any) => m.market === "EU");
    expect(usa?.phase).toBe(1);
    expect(eu?.phase).toBe(1);
  });

  test("Canada and Australia are phase 2", () => {
    const data = loadJson("market_matrix.json");
    const markets = data?.markets ?? [];
    const canada = markets.find((m: any) => m.market === "Canada");
    const aus = markets.find((m: any) => m.market === "Australia");
    expect(canada?.phase).toBe(2);
    expect(aus?.phase).toBe(2);
  });

  test("Japan is phase 3", () => {
    const data = loadJson("market_matrix.json");
    const japan = (data?.markets ?? []).find((m: any) => m.market === "Japan");
    expect(japan?.phase).toBe(3);
  });

  test("EU requires local representative", () => {
    const data = loadJson("market_matrix.json");
    const eu = (data?.markets ?? []).find((m: any) => m.market === "EU");
    expect(eu?.local_rep_required).toBe(true);
  });

  test("USA does not require local representative", () => {
    const data = loadJson("market_matrix.json");
    const usa = (data?.markets ?? []).find((m: any) => m.market === "USA");
    expect(usa?.local_rep_required).toBe(false);
  });
});

describe("documentation_plan.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "documentation_plan.json"))).toBe(true);
  });

  test("has documents array with 6 entries", () => {
    const data = loadJson("documentation_plan.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.documents)).toBe(true);
    expect(data.documents.length).toBe(6);
  });

  test("each document entry has doc_type, single_source, localization_needed", () => {
    const data = loadJson("documentation_plan.json");
    for (const d of data?.documents ?? []) {
      expect(typeof d.doc_type).toBe("string");
      expect(typeof d.single_source).toBe("boolean");
      expect(Array.isArray(d.localization_needed) || typeof d.localization_needed === "string").toBe(true);
    }
  });
});

describe("regulatory_risks.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "regulatory_risks.json"))).toBe(true);
  });

  test("has risks array with 3 entries", () => {
    const data = loadJson("regulatory_risks.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.risks)).toBe(true);
    expect(data.risks.length).toBe(3);
  });

  test("risk IDs are R1, R2, R3", () => {
    const data = loadJson("regulatory_risks.json");
    const ids = (data?.risks ?? []).map((r: any) => r.risk_id);
    expect(ids).toContain("R1");
    expect(ids).toContain("R2");
    expect(ids).toContain("R3");
  });

  test("each risk has probability, impact, and mitigation", () => {
    const data = loadJson("regulatory_risks.json");
    const validLevels = ["Low", "Medium", "High"];
    for (const r of data?.risks ?? []) {
      expect(validLevels).toContain(r.probability);
      expect(validLevels).toContain(r.impact);
      expect(typeof r.mitigation).toBe("string");
      expect(r.mitigation.length).toBeGreaterThan(10);
    }
  });
});

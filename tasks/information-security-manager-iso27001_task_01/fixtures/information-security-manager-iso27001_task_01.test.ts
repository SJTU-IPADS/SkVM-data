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

const VALID_TYPES = ["Information", "Software", "Hardware", "Service", "People"];
const VALID_CLASSIFICATIONS = ["Confidential", "Critical", "High", "Medium", "Low"];
const VALID_TREATMENTS = ["Mitigate", "Accept", "Transfer", "Avoid"];
const VALID_RISK_LEVELS = ["Critical", "High", "Medium", "Low", "Minimal"];

describe("assets.json", () => {
  test("assets.json exists", () => {
    expect(fileExists("assets.json")).toBe(true);
  });

  test("assets.json contains exactly 5 assets", () => {
    const data = loadJSON("assets.json");
    expect(Array.isArray(data)).toBe(true);
    expect(data.length).toBe(5);
  });

  test("each asset has required fields", () => {
    const data = loadJSON("assets.json");
    for (const asset of data) {
      expect(asset).toHaveProperty("id");
      expect(asset).toHaveProperty("name");
      expect(asset).toHaveProperty("type");
      expect(asset).toHaveProperty("owner");
      expect(asset).toHaveProperty("classification");
    }
  });

  test("asset types are valid enum values", () => {
    const data = loadJSON("assets.json");
    for (const asset of data) {
      expect(VALID_TYPES).toContain(asset.type);
    }
  });

  test("asset classifications are valid enum values", () => {
    const data = loadJSON("assets.json");
    for (const asset of data) {
      expect(VALID_CLASSIFICATIONS).toContain(asset.classification);
    }
  });
});

describe("risk_register.json", () => {
  test("risk_register.json exists", () => {
    expect(fileExists("risk_register.json")).toBe(true);
  });

  test("risk_register.json contains exactly 5 risks", () => {
    const data = loadJSON("risk_register.json");
    expect(Array.isArray(data)).toBe(true);
    expect(data.length).toBe(5);
  });

  test("each risk has required fields with correct types", () => {
    const data = loadJSON("risk_register.json");
    for (const risk of data) {
      expect(risk).toHaveProperty("id");
      expect(risk).toHaveProperty("asset_id");
      expect(risk).toHaveProperty("threat");
      expect(risk).toHaveProperty("vulnerability");
      expect(typeof risk.likelihood).toBe("number");
      expect(typeof risk.impact).toBe("number");
      expect(typeof risk.risk_score).toBe("number");
      expect(VALID_RISK_LEVELS).toContain(risk.risk_level);
      expect(VALID_TREATMENTS).toContain(risk.treatment);
    }
  });

  test("risk_score equals likelihood * impact for all risks", () => {
    const data = loadJSON("risk_register.json");
    for (const risk of data) {
      expect(risk.risk_score).toBe(risk.likelihood * risk.impact);
    }
  });

  test("risk_level matches score band correctly", () => {
    const data = loadJSON("risk_register.json");
    for (const risk of data) {
      const s = risk.risk_score;
      let expected: string;
      if (s >= 20) expected = "Critical";
      else if (s >= 15) expected = "High";
      else if (s >= 10) expected = "Medium";
      else if (s >= 5) expected = "Low";
      else expected = "Minimal";
      expect(risk.risk_level).toBe(expected);
    }
  });
});

describe("high_priority_risks.json", () => {
  test("high_priority_risks.json exists", () => {
    expect(fileExists("high_priority_risks.json")).toBe(true);
  });

  test("high_priority_risks.json contains only Critical/High risk IDs", () => {
    const risks = loadJSON("risk_register.json");
    const highPriority = loadJSON("high_priority_risks.json");
    expect(Array.isArray(highPriority)).toBe(true);
    const expectedIds = risks
      .filter((r: any) => r.risk_level === "Critical" || r.risk_level === "High")
      .map((r: any) => r.id);
    expect(highPriority.sort()).toEqual(expectedIds.sort());
  });
});

describe("risk_summary.json", () => {
  test("risk_summary.json exists", () => {
    expect(fileExists("risk_summary.json")).toBe(true);
  });

  test("risk_summary totals are consistent with risk_register", () => {
    const risks = loadJSON("risk_register.json");
    const summary = loadJSON("risk_summary.json");
    expect(summary.total_assets).toBe(5);
    expect(summary.total_risks).toBe(5);
    const criticalCount = risks.filter((r: any) => r.risk_level === "Critical").length;
    const highCount = risks.filter((r: any) => r.risk_level === "High").length;
    expect(summary.critical_count).toBe(criticalCount);
    expect(summary.high_count).toBe(highCount);
  });
});

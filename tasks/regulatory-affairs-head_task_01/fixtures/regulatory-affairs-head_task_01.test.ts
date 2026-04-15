import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const workspace = process.cwd();

function loadJson(filename: string) {
  const p = join(workspace, filename);
  if (!existsSync(p)) return null;
  try { return JSON.parse(readFileSync(p, "utf-8")); } catch { return null; }
}

describe("pathway_analysis.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "pathway_analysis.json"))).toBe(true);
  });

  test("has products array", () => {
    const data = loadJson("pathway_analysis.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.products)).toBe(true);
  });

  test("has 3 products with IDs P1, P2, P3", () => {
    const data = loadJson("pathway_analysis.json");
    const ids = (data?.products ?? []).map((p: any) => p.product_id);
    expect(ids).toContain("P1");
    expect(ids).toContain("P2");
    expect(ids).toContain("P3");
  });

  test("P1 SurgiGrip Clamp pathway is 510(k)", () => {
    const data = loadJson("pathway_analysis.json");
    const p1 = (data?.products ?? []).find((p: any) => p.product_id === "P1");
    expect(p1).toBeDefined();
    expect(p1?.pathway).toBe("510(k)");
    expect(p1?.estimated_review_days).toBe(90);
  });

  test("P2 NeuralScan AI pathway is De Novo", () => {
    const data = loadJson("pathway_analysis.json");
    const p2 = (data?.products ?? []).find((p: any) => p.product_id === "P2");
    expect(p2).toBeDefined();
    expect(p2?.pathway).toBe("De Novo");
    expect(p2?.estimated_review_days).toBe(150);
  });

  test("P3 CardioValve Pro pathway is PMA", () => {
    const data = loadJson("pathway_analysis.json");
    const p3 = (data?.products ?? []).find((p: any) => p.product_id === "P3");
    expect(p3).toBeDefined();
    expect(p3?.pathway).toBe("PMA");
    expect(p3?.estimated_review_days).toBe(180);
  });

  test("each product has rationale and requires_presub_meeting fields", () => {
    const data = loadJson("pathway_analysis.json");
    for (const p of data?.products ?? []) {
      expect(typeof p.rationale).toBe("string");
      expect(p.rationale.length).toBeGreaterThan(20);
      expect(typeof p.requires_presub_meeting).toBe("boolean");
    }
  });
});

describe("submission_checklist.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "submission_checklist.json"))).toBe(true);
  });

  test("has sections array", () => {
    const data = loadJson("submission_checklist.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.sections)).toBe(true);
  });

  test("has exactly 9 sections", () => {
    const data = loadJson("submission_checklist.json");
    expect(data?.sections?.length).toBe(9);
  });

  test("sections are numbered 1 through 9", () => {
    const data = loadJson("submission_checklist.json");
    const nums = (data?.sections ?? []).map((s: any) => s.section_number).sort((a: number, b: number) => a - b);
    expect(nums).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9]);
  });

  test("each section has title, status Required, and description", () => {
    const data = loadJson("submission_checklist.json");
    for (const s of data?.sections ?? []) {
      expect(typeof s.title).toBe("string");
      expect(s.status).toBe("Required");
      expect(typeof s.description).toBe("string");
      expect(s.description.length).toBeGreaterThan(10);
    }
  });

  test("submission_type is 510(k) and product is SurgiGrip Clamp", () => {
    const data = loadJson("submission_checklist.json");
    expect(data?.submission_type).toBe("510(k)");
    expect(data?.product).toMatch(/SurgiGrip/i);
  });
});

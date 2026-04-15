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

describe("kpi_report.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "kpi_report.json"))).toBe(true);
  });

  test("has period and kpis object", () => {
    const data = loadJson("kpi_report.json");
    expect(data).not.toBeNull();
    expect(typeof data.kpis).toBe("object");
  });

  test("first_pass_yield value is approximately 94.50%", () => {
    const data = loadJson("kpi_report.json");
    const val = data?.kpis?.first_pass_yield?.value ?? data?.kpis?.first_pass_yield;
    expect(typeof val).toBe("number");
    expect(approxEqual(val, 94.50, 0.1)).toBe(true);
  });

  test("nonconformance_rate is approximately 0.70%", () => {
    const data = loadJson("kpi_report.json");
    const val = data?.kpis?.nonconformance_rate?.value ?? data?.kpis?.nonconformance_rate;
    expect(typeof val).toBe("number");
    expect(approxEqual(val, 0.7016, 0.02)).toBe(true);
  });

  test("capa_closure_rate is approximately 88.89%", () => {
    const data = loadJson("kpi_report.json");
    const val = data?.kpis?.capa_closure_rate?.value ?? data?.kpis?.capa_closure_rate;
    expect(typeof val).toBe("number");
    expect(approxEqual(val, 88.89, 0.1)).toBe(true);
  });

  test("complaint_rate is approximately 0.0726%", () => {
    const data = loadJson("kpi_report.json");
    const val = data?.kpis?.complaint_rate?.value ?? data?.kpis?.complaint_rate;
    expect(typeof val).toBe("number");
    expect(approxEqual(val, 0.0726, 0.005)).toBe(true);
  });

  test("audit_finding_closure_rate is approximately 86.36%", () => {
    const data = loadJson("kpi_report.json");
    const val = data?.kpis?.audit_finding_closure_rate?.value ?? data?.kpis?.audit_finding_closure_rate;
    expect(typeof val).toBe("number");
    expect(approxEqual(val, 86.36, 0.1)).toBe(true);
  });

  test("repeat_finding_rate is approximately 13.64%", () => {
    const data = loadJson("kpi_report.json");
    const val = data?.kpis?.repeat_finding_rate?.value ?? data?.kpis?.repeat_finding_rate;
    expect(typeof val).toBe("number");
    expect(approxEqual(val, 13.64, 0.1)).toBe(true);
  });

  test("each KPI has a status field", () => {
    const data = loadJson("kpi_report.json");
    const kpis = data?.kpis ?? {};
    const validStatuses = ["Meeting", "Below", "Critical", "Exceeding", "Approaching"];
    for (const [key, val] of Object.entries(kpis)) {
      const kpiObj = val as any;
      if (typeof kpiObj === "object" && kpiObj !== null) {
        expect(typeof kpiObj.status).toBe("string");
        expect(kpiObj.status.length).toBeGreaterThan(0);
      }
    }
  });
});

describe("kpi_actions.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "kpi_actions.json"))).toBe(true);
  });

  test("has actions_required array", () => {
    const data = loadJson("kpi_actions.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.actions_required)).toBe(true);
  });

  test("has underperforming KPIs identified", () => {
    const data = loadJson("kpi_actions.json");
    // first_pass_yield (94.5% vs >95%), capa_closure_rate (88.89% vs >90%), repeat_finding_rate (13.64% vs <10%) are below target
    expect(data?.actions_required?.length).toBeGreaterThanOrEqual(1);
  });

  test("each action has kpi and recommendation fields", () => {
    const data = loadJson("kpi_actions.json");
    for (const action of data?.actions_required ?? []) {
      expect(typeof action.kpi).toBe("string");
      expect(typeof action.recommendation).toBe("string");
      expect(action.recommendation.length).toBeGreaterThan(10);
    }
  });
});

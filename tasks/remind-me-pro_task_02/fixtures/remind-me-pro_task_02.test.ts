import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const workspace = process.cwd();

function loadJson(filename: string) {
  const p = join(workspace, filename);
  if (!existsSync(p)) return null;
  try { return JSON.parse(readFileSync(p, "utf-8")); } catch { return null; }
}

describe("reminder_analysis.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "reminder_analysis.json"))).toBe(true);
  });

  test("has requests array with 6 entries", () => {
    const data = loadJson("reminder_analysis.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.requests)).toBe(true);
    expect(data.requests.length).toBe(6);
  });

  test("REQ-A status is NEEDS_CLARIFICATION", () => {
    const data = loadJson("reminder_analysis.json");
    const req = (data?.requests ?? []).find((r: any) => r.id === "REQ-A");
    expect(req).toBeDefined();
    expect(req?.status).toBe("NEEDS_CLARIFICATION");
  });

  test("REQ-B status is READY", () => {
    const data = loadJson("reminder_analysis.json");
    const req = (data?.requests ?? []).find((r: any) => r.id === "REQ-B");
    expect(req).toBeDefined();
    expect(req?.status).toBe("READY");
  });

  test("REQ-C status is NEEDS_CLARIFICATION", () => {
    const data = loadJson("reminder_analysis.json");
    const req = (data?.requests ?? []).find((r: any) => r.id === "REQ-C");
    expect(req).toBeDefined();
    expect(req?.status).toBe("NEEDS_CLARIFICATION");
  });

  test("REQ-D status is READY with schedule at:45m", () => {
    const data = loadJson("reminder_analysis.json");
    const req = (data?.requests ?? []).find((r: any) => r.id === "REQ-D");
    expect(req).toBeDefined();
    expect(req?.status).toBe("READY");
    expect(req?.schedule_string).toBe("at:45m");
  });

  test("REQ-F status is NEEDS_CLARIFICATION", () => {
    const data = loadJson("reminder_analysis.json");
    const req = (data?.requests ?? []).find((r: any) => r.id === "REQ-F");
    expect(req).toBeDefined();
    expect(req?.status).toBe("NEEDS_CLARIFICATION");
  });

  test("NEEDS_CLARIFICATION requests have clarification_question set", () => {
    const data = loadJson("reminder_analysis.json");
    const needsClarify = (data?.requests ?? []).filter((r: any) => r.status === "NEEDS_CLARIFICATION");
    expect(needsClarify.length).toBeGreaterThanOrEqual(3);
    for (const req of needsClarify) {
      expect(typeof req.clarification_question).toBe("string");
      expect(req.clarification_question.length).toBeGreaterThan(10);
    }
  });

  test("READY requests have schedule_string set", () => {
    const data = loadJson("reminder_analysis.json");
    const ready = (data?.requests ?? []).filter((r: any) => r.status === "READY");
    expect(ready.length).toBeGreaterThanOrEqual(2);
    for (const req of ready) {
      expect(typeof req.schedule_string).toBe("string");
      expect(req.schedule_string).toMatch(/^(at:|every:|cron:)/);
    }
  });
});

describe("reminder_summary.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "reminder_summary.json"))).toBe(true);
  });

  test("has correct total of 6", () => {
    const data = loadJson("reminder_summary.json");
    expect(data).not.toBeNull();
    expect(data.total).toBe(6);
  });

  test("ready_count and needs_clarification_count sum to 6", () => {
    const data = loadJson("reminder_summary.json");
    expect(data?.ready_count + data?.needs_clarification_count).toBe(6);
  });

  test("ready_ids and clarification_ids are arrays", () => {
    const data = loadJson("reminder_summary.json");
    expect(Array.isArray(data?.ready_ids)).toBe(true);
    expect(Array.isArray(data?.clarification_ids)).toBe(true);
  });
});

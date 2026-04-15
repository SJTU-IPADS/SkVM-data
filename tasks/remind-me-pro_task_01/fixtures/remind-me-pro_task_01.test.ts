import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const workspace = process.cwd();

function loadJson(filename: string) {
  const p = join(workspace, filename);
  if (!existsSync(p)) return null;
  try { return JSON.parse(readFileSync(p, "utf-8")); } catch { return null; }
}

describe("reminders_parsed.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, "reminders_parsed.json"))).toBe(true);
  });

  test("has reminders array", () => {
    const data = loadJson("reminders_parsed.json");
    expect(data).not.toBeNull();
    expect(Array.isArray(data.reminders)).toBe(true);
  });

  test("has exactly 5 reminder entries", () => {
    const data = loadJson("reminders_parsed.json");
    expect(data?.reminders?.length).toBe(5);
  });

  test("R1 schedule_string is cron for Monday at 9 AM", () => {
    const data = loadJson("reminders_parsed.json");
    const r1 = (data?.reminders ?? []).find((r: any) => r.id === "R1");
    expect(r1).toBeDefined();
    // Accept cron:0 9 * * 1 or equivalent
    expect(r1?.schedule_string).toMatch(/^cron:/);
    expect(r1?.schedule_string).toMatch(/\b9\b/);
    expect(r1?.schedule_string).toMatch(/\b1\b/);
  });

  test("R2 schedule_string is every:30m", () => {
    const data = loadJson("reminders_parsed.json");
    const r2 = (data?.reminders ?? []).find((r: any) => r.id === "R2");
    expect(r2).toBeDefined();
    expect(r2?.schedule_string).toBe("every:30m");
  });

  test("R3 schedule_string is cron for Friday at 5 PM", () => {
    const data = loadJson("reminders_parsed.json");
    const r3 = (data?.reminders ?? []).find((r: any) => r.id === "R3");
    expect(r3).toBeDefined();
    expect(r3?.schedule_string).toMatch(/^cron:/);
    expect(r3?.schedule_string).toMatch(/\b17\b/);
    expect(r3?.schedule_string).toMatch(/\b5\b/);
  });

  test("R4 schedule_string is cron for daily at 8 AM", () => {
    const data = loadJson("reminders_parsed.json");
    const r4 = (data?.reminders ?? []).find((r: any) => r.id === "R4");
    expect(r4).toBeDefined();
    expect(r4?.schedule_string).toMatch(/^cron:/);
    expect(r4?.schedule_string).toMatch(/\b8\b/);
  });

  test("all reminders are marked as recurring", () => {
    const data = loadJson("reminders_parsed.json");
    for (const r of data?.reminders ?? []) {
      expect(r.is_recurring).toBe(true);
    }
  });

  test("job_name is a non-empty string under 30 chars for all", () => {
    const data = loadJson("reminders_parsed.json");
    for (const r of data?.reminders ?? []) {
      expect(typeof r.job_name).toBe("string");
      expect(r.job_name.length).toBeGreaterThan(0);
      expect(r.job_name.length).toBeLessThanOrEqual(30);
    }
  });

  test("what field is a non-empty reminder message for all", () => {
    const data = loadJson("reminders_parsed.json");
    for (const r of data?.reminders ?? []) {
      expect(typeof r.what).toBe("string");
      expect(r.what.length).toBeGreaterThan(5);
    }
  });
});

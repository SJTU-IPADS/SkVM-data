import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const workspace = process.env.WORKSPACE_PATH || ".";

function readFile(relPath: string): string {
  return readFileSync(join(workspace, relPath), "utf-8");
}

describe("workspace/decide/memory.md", () => {
  test("memory.md file exists", () => {
    expect(existsSync(join(workspace, "workspace/decide/memory.md"))).toBe(true);
  });

  test("memory.md contains Decision Rules section", () => {
    const content = readFile("workspace/decide/memory.md");
    expect(content).toMatch(/##\s+Decision Rules/i);
  });

  test("memory.md contains Confirmed Defaults section", () => {
    const content = readFile("workspace/decide/memory.md");
    expect(content).toMatch(/##\s+Confirmed Defaults/i);
  });

  test("memory.md mentions framework selection approval boundary", () => {
    const content = readFile("workspace/decide/memory.md").toLowerCase();
    expect(content).toMatch(/framework|architecture/);
    expect(content).toMatch(/human|confirm|approval/);
  });
});

describe("workspace/decide/decisions.md", () => {
  test("decisions.md file exists", () => {
    expect(existsSync(join(workspace, "workspace/decide/decisions.md"))).toBe(true);
  });

  test("decisions.md contains a JSON code block", () => {
    const content = readFile("workspace/decide/decisions.md");
    expect(content).toContain("```json");
  });

  test("decisions.md JSON block has required fields", () => {
    const content = readFile("workspace/decide/decisions.md");
    const jsonMatch = content.match(/```json\s*([\s\S]*?)```/);
    expect(jsonMatch).not.toBeNull();
    const parsed = JSON.parse(jsonMatch![1]);
    expect(parsed).toHaveProperty("id");
    expect(parsed).toHaveProperty("question");
    expect(parsed).toHaveProperty("components");
    expect(parsed).toHaveProperty("chosen_option");
    expect(parsed).toHaveProperty("rationale");
    expect(parsed).toHaveProperty("confidence");
    expect(parsed).toHaveProperty("outcome");
  });

  test("decision confidence is between 0 and 1", () => {
    const content = readFile("workspace/decide/decisions.md");
    const jsonMatch = content.match(/```json\s*([\s\S]*?)```/);
    expect(jsonMatch).not.toBeNull();
    const parsed = JSON.parse(jsonMatch![1]);
    expect(Number(parsed.confidence)).toBeGreaterThanOrEqual(0);
    expect(Number(parsed.confidence)).toBeLessThanOrEqual(1);
  });

  test("decision is about PostgreSQL vs SQLite", () => {
    const content = readFile("workspace/decide/decisions.md").toLowerCase();
    expect(content).toMatch(/postgresql|postgres/);
    expect(content).toMatch(/sqlite/);
  });
});

describe("workspace/decide/domains/database.md", () => {
  test("database.md domain file exists", () => {
    expect(existsSync(join(workspace, "workspace/decide/domains/database.md"))).toBe(true);
  });

  test("database.md mentions SQLite appropriateness", () => {
    const content = readFile("workspace/decide/domains/database.md").toLowerCase();
    expect(content).toContain("sqlite");
  });
});

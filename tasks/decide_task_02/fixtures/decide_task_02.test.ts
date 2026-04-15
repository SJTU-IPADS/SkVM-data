import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const OUTPUT_FILE = "output/decision_evaluation.json";
const workspace = process.env.WORKSPACE_PATH || ".";

function loadOutput(workspace: string) {
  const content = readFileSync(join(workspace, OUTPUT_FILE), "utf-8");
  return JSON.parse(content);
}

describe("output/decision_evaluation.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, OUTPUT_FILE))).toBe(true);
  });

  test("valid JSON format", () => {
    expect(() => loadOutput(workspace)).not.toThrow();
  });

  test("has all required keys", () => {
    const data = loadOutput(workspace);
    expect(data).toHaveProperty("scenario_summary");
    expect(data).toHaveProperty("matching_rules");
    expect(data).toHaveProperty("rule_reusable");
    expect(data).toHaveProperty("reuse_reason");
    expect(data).toHaveProperty("recommended_action");
    expect(data).toHaveProperty("confidence");
  });

  test("scenario_summary is a non-empty string", () => {
    const data = loadOutput(workspace);
    expect(typeof data.scenario_summary).toBe("string");
    expect(data.scenario_summary.length).toBeGreaterThan(10);
  });

  test("matching_rules is an array", () => {
    const data = loadOutput(workspace);
    expect(Array.isArray(data.matching_rules)).toBe(true);
  });

  test("rule_reusable is a boolean", () => {
    const data = loadOutput(workspace);
    expect(typeof data.rule_reusable).toBe("boolean");
  });

  test("recommended_action is one of the valid options", () => {
    const data = loadOutput(workspace);
    const validOptions = ["reuse_rule", "ask_human", "create_new_rule"];
    expect(validOptions).toContain(data.recommended_action);
  });

  test("confidence is between 0 and 1", () => {
    const data = loadOutput(workspace);
    expect(Number(data.confidence)).toBeGreaterThanOrEqual(0);
    expect(Number(data.confidence)).toBeLessThanOrEqual(1);
  });

  test("reuse_reason is a non-empty string", () => {
    const data = loadOutput(workspace);
    expect(typeof data.reuse_reason).toBe("string");
    expect(data.reuse_reason.length).toBeGreaterThan(10);
  });
});

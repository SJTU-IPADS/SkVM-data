import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const OUTPUT_FILE = "output/index_recommendations.json";

const workspace = process.env.WORKSPACE_PATH || ".";

function loadOutput(workspace: string) {
  const content = readFileSync(join(workspace, OUTPUT_FILE), "utf-8");
  return JSON.parse(content);
}

describe("output/index_recommendations.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, OUTPUT_FILE))).toBe(true);
  });

  test("valid JSON format", () => {
    expect(() => loadOutput(workspace)).not.toThrow();
  });

  test("has all required keys", () => {
    const data = loadOutput(workspace);
    expect(data).toHaveProperty("missing_foreign_keys");
    expect(data).toHaveProperty("recommended_indexes");
    expect(data).toHaveProperty("existing_issues");
    expect(data).toHaveProperty("issue_count");
  });

  test("missing_foreign_keys is an array with at least 3 entries", () => {
    const data = loadOutput(workspace);
    expect(Array.isArray(data.missing_foreign_keys)).toBe(true);
    // posts.user_id, comments.post_id, comments.user_id, post_tags.post_id, post_tags.tag_id
    expect(data.missing_foreign_keys.length).toBeGreaterThanOrEqual(3);
  });

  test("missing_foreign_keys entries have table and column fields", () => {
    const data = loadOutput(workspace);
    for (const entry of data.missing_foreign_keys) {
      expect(entry).toHaveProperty("table");
      expect(entry).toHaveProperty("column");
      expect(typeof entry.table).toBe("string");
      expect(typeof entry.column).toBe("string");
    }
  });

  test("recommended_indexes is a non-empty array", () => {
    const data = loadOutput(workspace);
    expect(Array.isArray(data.recommended_indexes)).toBe(true);
    expect(data.recommended_indexes.length).toBeGreaterThanOrEqual(2);
  });

  test("recommended_indexes entries have table, columns, and reason", () => {
    const data = loadOutput(workspace);
    for (const entry of data.recommended_indexes) {
      expect(entry).toHaveProperty("table");
      expect(entry).toHaveProperty("columns");
      expect(entry).toHaveProperty("reason");
      expect(Array.isArray(entry.columns)).toBe(true);
      expect(entry.columns.length).toBeGreaterThan(0);
    }
  });

  test("existing_issues is an array", () => {
    const data = loadOutput(workspace);
    expect(Array.isArray(data.existing_issues)).toBe(true);
  });

  test("issue_count is a positive integer", () => {
    const data = loadOutput(workspace);
    expect(Number.isInteger(Number(data.issue_count))).toBe(true);
    expect(Number(data.issue_count)).toBeGreaterThan(0);
  });
});

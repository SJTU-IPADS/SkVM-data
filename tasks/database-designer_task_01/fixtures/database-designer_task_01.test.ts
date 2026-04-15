import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const SQL_FILE = "output/schema.sql";
const JSON_FILE = "output/schema_analysis.json";

const workspace = process.env.WORKSPACE_PATH || ".";

function loadJson(workspace: string) {
  const content = readFileSync(join(workspace, JSON_FILE), "utf-8");
  return JSON.parse(content);
}

function loadSql(workspace: string): string {
  return readFileSync(join(workspace, SQL_FILE), "utf-8");
}

describe("output/schema.sql", () => {
  test("SQL file exists", () => {
    expect(existsSync(join(workspace, SQL_FILE))).toBe(true);
  });

  test("contains all 5 required tables", () => {
    const sql = loadSql(workspace).toLowerCase();
    expect(sql).toContain("create table");
    const requiredTables = ["categories", "products", "customers", "orders", "order_items"];
    for (const table of requiredTables) {
      expect(sql).toContain(table);
    }
  });

  test("contains PRIMARY KEY definitions", () => {
    const sql = loadSql(workspace).toLowerCase();
    expect(sql).toContain("primary key");
  });

  test("contains FOREIGN KEY or REFERENCES constraints", () => {
    const sql = loadSql(workspace).toLowerCase();
    expect(sql).toContain("references");
  });

  test("products table references categories", () => {
    const sql = loadSql(workspace).toLowerCase();
    expect(sql).toContain("category_id");
    expect(sql).toContain("categories");
  });

  test("order_items table has quantity and unit_price columns", () => {
    const sql = loadSql(workspace).toLowerCase();
    expect(sql).toContain("quantity");
    expect(sql).toContain("unit_price");
  });
});

describe("output/schema_analysis.json", () => {
  test("JSON file exists", () => {
    expect(existsSync(join(workspace, JSON_FILE))).toBe(true);
  });

  test("valid JSON format", () => {
    expect(() => loadJson(workspace)).not.toThrow();
  });

  test("table_count is 5", () => {
    const data = loadJson(workspace);
    expect(Number(data.table_count)).toBe(5);
  });

  test("tables array contains all required table names", () => {
    const data = loadJson(workspace);
    expect(Array.isArray(data.tables)).toBe(true);
    const tables = data.tables.map((t: string) => t.toLowerCase());
    expect(tables).toContain("categories");
    expect(tables).toContain("products");
    expect(tables).toContain("customers");
    expect(tables).toContain("orders");
    expect(tables).toContain("order_items");
  });

  test("foreign_keys array is non-empty", () => {
    const data = loadJson(workspace);
    expect(Array.isArray(data.foreign_keys)).toBe(true);
    expect(data.foreign_keys.length).toBeGreaterThanOrEqual(3);
  });

  test("normalization_form is present and non-empty", () => {
    const data = loadJson(workspace);
    expect(typeof data.normalization_form).toBe("string");
    expect(data.normalization_form.length).toBeGreaterThan(0);
  });
});

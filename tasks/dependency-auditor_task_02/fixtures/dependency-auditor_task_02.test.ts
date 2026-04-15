import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const OUTPUT_FILE = "output/license_report.json";
const workspace = process.env.WORKSPACE_PATH || ".";

function loadOutput(workspace: string) {
  const content = readFileSync(join(workspace, OUTPUT_FILE), "utf-8");
  return JSON.parse(content);
}

describe("output/license_report.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, OUTPUT_FILE))).toBe(true);
  });

  test("valid JSON format", () => {
    expect(() => loadOutput(workspace)).not.toThrow();
  });

  test("has all required top-level keys", () => {
    const data = loadOutput(workspace);
    expect(data).toHaveProperty("project_type");
    expect(data).toHaveProperty("dependency_count");
    expect(data).toHaveProperty("license_inventory");
    expect(data).toHaveProperty("license_conflicts");
    expect(data).toHaveProperty("compliance_status");
    expect(data).toHaveProperty("permissive_count");
    expect(data).toHaveProperty("copyleft_count");
  });

  test("dependency_count is 8", () => {
    const data = loadOutput(workspace);
    expect(Number(data.dependency_count)).toBe(8);
  });

  test("license_inventory has 8 entries", () => {
    const data = loadOutput(workspace);
    expect(Array.isArray(data.license_inventory)).toBe(true);
    expect(data.license_inventory.length).toBe(8);
  });

  test("each license_inventory entry has required fields", () => {
    const data = loadOutput(workspace);
    for (const entry of data.license_inventory) {
      expect(entry).toHaveProperty("package");
      expect(entry).toHaveProperty("version");
      expect(entry).toHaveProperty("license");
      expect(entry).toHaveProperty("license_type");
      expect(typeof entry.package).toBe("string");
      expect(typeof entry.license).toBe("string");
      const validTypes = ["permissive", "copyleft", "unknown"];
      expect(validTypes).toContain(entry.license_type);
    }
  });

  test("compliance_status is one of the valid options", () => {
    const data = loadOutput(workspace);
    const validOptions = ["compliant", "review_required", "non_compliant"];
    expect(validOptions).toContain(data.compliance_status);
  });

  test("permissive_count is a non-negative integer", () => {
    const data = loadOutput(workspace);
    expect(Number.isInteger(Number(data.permissive_count))).toBe(true);
    expect(Number(data.permissive_count)).toBeGreaterThan(0);
  });

  test("copyleft_count is a non-negative integer", () => {
    const data = loadOutput(workspace);
    expect(Number.isInteger(Number(data.copyleft_count))).toBe(true);
    expect(Number(data.copyleft_count)).toBeGreaterThanOrEqual(0);
  });

  test("license_conflicts is an array", () => {
    const data = loadOutput(workspace);
    expect(Array.isArray(data.license_conflicts)).toBe(true);
  });

  test("all packages are represented in license_inventory", () => {
    const data = loadOutput(workspace);
    const packages = data.license_inventory.map((e: { package: string }) => e.package.toLowerCase());
    const required = ["requests", "numpy", "pandas", "scikit-learn", "flask", "sqlalchemy", "pytest", "cryptography"];
    for (const pkg of required) {
      expect(packages.some((p: string) => p.includes(pkg.replace("-", "_")) || p.includes(pkg))).toBe(true);
    }
  });
});

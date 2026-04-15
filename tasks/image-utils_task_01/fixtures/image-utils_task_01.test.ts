import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync, statSync } from "fs";
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

describe("image_info.json", () => {
  test("image_info.json exists", () => {
    expect(fileExists("image_info.json")).toBe(true);
  });

  test("image_info.json is valid JSON with required keys", () => {
    const data = loadJSON("image_info.json");
    expect(data).not.toBeNull();
    expect(data).toHaveProperty("source");
    expect(data).toHaveProperty("resized");
    expect(data).toHaveProperty("cropped");
    expect(data).toHaveProperty("bordered");
  });

  test("source image dimensions are 400x300", () => {
    const data = loadJSON("image_info.json");
    expect(data.source.width).toBe(400);
    expect(data.source.height).toBe(300);
  });

  test("source image mode is RGB", () => {
    const data = loadJSON("image_info.json");
    expect(data.source.mode).toBe("RGB");
  });

  test("resized image dimensions are 200x150", () => {
    const data = loadJSON("image_info.json");
    expect(data.resized.width).toBe(200);
    expect(data.resized.height).toBe(150);
  });

  test("cropped image dimensions are 200x150", () => {
    const data = loadJSON("image_info.json");
    // crop region: right-left=250-50=200, bottom-top=200-50=150
    expect(data.cropped.width).toBe(200);
    expect(data.cropped.height).toBe(150);
  });

  test("bordered image dimensions are 420x320", () => {
    const data = loadJSON("image_info.json");
    expect(data.bordered.width).toBe(420);
    expect(data.bordered.height).toBe(320);
  });
});

describe("output files", () => {
  test("source.png exists", () => {
    expect(fileExists("source.png")).toBe(true);
  });

  test("resized.png exists", () => {
    expect(fileExists("resized.png")).toBe(true);
  });

  test("cropped.png exists", () => {
    expect(fileExists("cropped.png")).toBe(true);
  });

  test("output.jpg exists", () => {
    expect(fileExists("output.jpg")).toBe(true);
  });

  test("bordered.png exists", () => {
    expect(fileExists("bordered.png")).toBe(true);
  });
});

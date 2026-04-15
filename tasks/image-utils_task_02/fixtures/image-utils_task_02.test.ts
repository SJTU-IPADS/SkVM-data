import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const workspace = process.env.WORKSPACE_PATH || ".";

function fileExists(filename: string) {
  return existsSync(join(workspace, filename));
}

function loadJSON(filename: string) {
  const p = join(workspace, filename);
  if (!existsSync(p)) return null;
  try {
    return JSON.parse(readFileSync(p, "utf-8"));
  } catch {
    return null;
  }
}

describe("pixel_check.json", () => {
  test("pixel_check.json exists", () => {
    expect(fileExists("pixel_check.json")).toBe(true);
  });

  test("pixel_check.json has all required keys", () => {
    const data = loadJSON("pixel_check.json");
    expect(data).not.toBeNull();
    expect(data).toHaveProperty("original_top_left_pixel");
    expect(data).toHaveProperty("original_bottom_left_pixel");
    expect(data).toHaveProperty("flipped_v_top_left_pixel");
    expect(data).toHaveProperty("gray_mode");
    expect(data).toHaveProperty("gray_size");
  });

  test("original top-left pixel is red (255,0,0)", () => {
    const data = loadJSON("pixel_check.json");
    const px = data.original_top_left_pixel;
    expect(Array.isArray(px)).toBe(true);
    expect(px[0]).toBe(255);
    expect(px[1]).toBe(0);
    expect(px[2]).toBe(0);
  });

  test("original bottom-left pixel is green (0,128,0)", () => {
    const data = loadJSON("pixel_check.json");
    const px = data.original_bottom_left_pixel;
    expect(Array.isArray(px)).toBe(true);
    expect(px[0]).toBe(0);
    expect(px[1]).toBe(128);
    expect(px[2]).toBe(0);
  });

  test("flipped_v top-left pixel is green after vertical flip", () => {
    const data = loadJSON("pixel_check.json");
    const px = data.flipped_v_top_left_pixel;
    expect(Array.isArray(px)).toBe(true);
    // After vertical flip, top becomes bottom: green row should now be at top
    expect(px[1]).toBeGreaterThan(px[0]);
    expect(px[1]).toBeGreaterThan(px[2]);
  });

  test("grayscale mode is L", () => {
    const data = loadJSON("pixel_check.json");
    expect(data.gray_mode).toBe("L");
  });

  test("grayscale size is [300, 300]", () => {
    const data = loadJSON("pixel_check.json");
    expect(data.gray_size).toEqual([300, 300]);
  });
});

describe("output image files", () => {
  test("original.png exists", () => {
    expect(fileExists("original.png")).toBe(true);
  });

  test("bright.png exists", () => {
    expect(fileExists("bright.png")).toBe(true);
  });

  test("low_contrast.png exists", () => {
    expect(fileExists("low_contrast.png")).toBe(true);
  });

  test("gray.png exists", () => {
    expect(fileExists("gray.png")).toBe(true);
  });

  test("flipped_h.png exists", () => {
    expect(fileExists("flipped_h.png")).toBe(true);
  });

  test("flipped_v.png exists", () => {
    expect(fileExists("flipped_v.png")).toBe(true);
  });
});

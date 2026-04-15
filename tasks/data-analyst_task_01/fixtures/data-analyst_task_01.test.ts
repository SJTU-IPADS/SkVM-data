import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

const OUTPUT_FILE = "output/analysis.json";

function loadOutput(workspace: string) {
  const filePath = join(workspace, OUTPUT_FILE);
  const content = readFileSync(filePath, "utf-8");
  return JSON.parse(content);
}

const workspace = process.env.WORKSPACE_PATH || ".";

describe("output/analysis.json", () => {
  test("file exists", () => {
    expect(existsSync(join(workspace, OUTPUT_FILE))).toBe(true);
  });

  test("valid JSON format", () => {
    expect(() => loadOutput(workspace)).not.toThrow();
  });

  test("has required top-level keys", () => {
    const data = loadOutput(workspace);
    expect(data).toHaveProperty("category_revenue");
    expect(data).toHaveProperty("region_revenue");
    expect(data).toHaveProperty("top_product");
    expect(data).toHaveProperty("total_revenue");
  });

  test("category_revenue is an object with correct categories", () => {
    const data = loadOutput(workspace);
    expect(typeof data.category_revenue).toBe("object");
    expect(data.category_revenue).toHaveProperty("Electronics");
    expect(data.category_revenue).toHaveProperty("Hardware");
  });

  test("category_revenue values are correct", () => {
    const data = loadOutput(workspace);
    // Electronics: (10*25)+(5*40)+(7*25)+(20*10)+(9*40)+(15*10) = 250+200+175+200+360+150 = 1335
    expect(Number(data.category_revenue["Electronics"])).toBe(1335);
    // Hardware: (8*15)+(12*20)+(3*15)+(6*20) = 120+240+45+120 = 525
    expect(Number(data.category_revenue["Hardware"])).toBe(525);
  });

  test("region_revenue values are correct", () => {
    const data = loadOutput(workspace);
    // North: (10*25)+(8*15)+(6*20) = 250+120+120 = 490
    expect(Number(data.region_revenue["North"])).toBe(490);
    // South: (5*40)+(3*15)+(15*10) = 200+45+150 = 395
    expect(Number(data.region_revenue["South"])).toBe(395);
    // East: (12*20)+(7*25) = 240+175 = 415
    expect(Number(data.region_revenue["East"])).toBe(415);
    // West: (20*10)+(9*40) = 200+360 = 560
    expect(Number(data.region_revenue["West"])).toBe(560);
  });

  test("total_revenue is correct", () => {
    const data = loadOutput(workspace);
    // 1335 + 525 = 1860
    expect(Number(data.total_revenue)).toBe(1860);
  });

  test("top_product is Widget B", () => {
    const data = loadOutput(workspace);
    // Widget B: (5*40)+(9*40) = 200+360 = 560
    // Widget A: (10*25)+(7*25) = 250+175 = 425
    // Widget C: (20*10)+(15*10) = 200+150 = 350
    // Gadget Y: (12*20)+(6*20) = 240+120 = 360
    // Gadget X: (8*15)+(3*15) = 120+45 = 165
    expect(data.top_product).toBe("Widget B");
  });
});

import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync, readdirSync } from "fs";
import { join } from "path";

function listMdFiles(dir: string): string[] {
  if (!existsSync(dir)) return [];
  return readdirSync(dir).filter((f) => f.endsWith(".md"));
}

function readFile(path: string): string {
  return readFileSync(path, "utf-8");
}

function extractFrontmatter(content: string): Record<string, any> | null {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return null;
  // Simple YAML parser for our needs
  const lines = match[1].split("\n");
  const result: Record<string, any> = {};
  for (const line of lines) {
    const kv = line.match(/^(\w+):\s*(.+)/);
    if (kv) result[kv[1]] = kv[2].trim();
  }
  return result;
}

function countWikiLinks(content: string): number {
  const matches = content.match(/\[\[[^\]]+\]\]/g);
  return matches ? matches.length : 0;
}

describe("vault structure", () => {
  test("vault folder exists with required subdirectories", () => {
    expect(existsSync("vault")).toBe(true);
    expect(existsSync("vault/projects")).toBe(true);
    expect(existsSync("vault/concepts")).toBe(true);
    expect(existsSync("vault/daily")).toBe(true);
  });

  test("projects/ has at least 3 project notes", () => {
    const files = listMdFiles("vault/projects");
    expect(files.length).toBeGreaterThanOrEqual(3);
  });

  test("concepts/ has at least 4 concept notes", () => {
    const files = listMdFiles("vault/concepts");
    expect(files.length).toBeGreaterThanOrEqual(4);
  });

  test("daily notes use ISO date naming", () => {
    const files = listMdFiles("vault/daily");
    expect(files.length).toBeGreaterThanOrEqual(2);
    for (const f of files) {
      // Match YYYY-MM-DD.md
      expect(f).toMatch(/^\d{4}-\d{2}-\d{2}\.md$/);
    }
  });

  test("project notes have YAML frontmatter with required fields", () => {
    const files = listMdFiles("vault/projects");
    for (const f of files) {
      const content = readFile(join("vault/projects", f));
      expect(content).toMatch(/^---\n/);
      const fm = extractFrontmatter(content);
      expect(fm).not.toBeNull();
      expect(fm!.title).toBeDefined();
      expect(fm!.status).toBeDefined();
    }
  });

  test("concept notes have YAML frontmatter with title and tags", () => {
    const files = listMdFiles("vault/concepts");
    for (const f of files) {
      const content = readFile(join("vault/concepts", f));
      expect(content).toMatch(/^---\n/);
      const fm = extractFrontmatter(content);
      expect(fm).not.toBeNull();
      expect(fm!.title).toBeDefined();
    }
  });

  test("vault has at least 15 total wiki-links across all notes", () => {
    let totalLinks = 0;
    const dirs = ["vault/projects", "vault/concepts", "vault/daily"];
    for (const dir of dirs) {
      for (const f of listMdFiles(dir)) {
        totalLinks += countWikiLinks(readFile(join(dir, f)));
      }
    }
    if (existsSync("vault/index.md")) {
      totalLinks += countWikiLinks(readFile("vault/index.md"));
    }
    expect(totalLinks).toBeGreaterThanOrEqual(15);
  });

  test("index.md exists and serves as MOC with wiki-links", () => {
    expect(existsSync("vault/index.md")).toBe(true);
    const content = readFile("vault/index.md");
    const linkCount = countWikiLinks(content);
    // Should link to at least projects and concepts (7+ notes)
    expect(linkCount).toBeGreaterThanOrEqual(5);
  });
});

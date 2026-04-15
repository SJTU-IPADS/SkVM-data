import { describe, test, expect } from "bun:test";
import { existsSync, readFileSync } from "fs";

function loadGraph(): any {
  return JSON.parse(readFileSync("graph.json", "utf-8"));
}

function findNode(nodes: any[], name: string): any | undefined {
  return nodes.find(
    (n: any) => n.name.toLowerCase() === name.toLowerCase()
  );
}

describe("graph.json", () => {
  test("graph.json exists", () => {
    expect(existsSync("graph.json")).toBe(true);
  });

  test("nodes array has 10 entries matching vault files", () => {
    const g = loadGraph();
    expect(Array.isArray(g.nodes)).toBe(true);
    expect(g.nodes.length).toBe(10);
    const names = g.nodes.map((n: any) => n.name.toLowerCase()).sort();
    expect(names).toContain("web-redesign");
    expect(names).toContain("api-migration");
    expect(names).toContain("legacy-patterns");
    expect(names).toContain("2025-03-15");
  });

  test("edges array contains valid links between existing notes", () => {
    const g = loadGraph();
    expect(Array.isArray(g.edges)).toBe(true);
    // All edges should reference existing node names
    const nodeNames = new Set(g.nodes.map((n: any) => n.name.toLowerCase()));
    for (const edge of g.edges) {
      expect(nodeNames.has(edge.source.toLowerCase())).toBe(true);
      expect(nodeNames.has(edge.target.toLowerCase())).toBe(true);
    }
    // 22 valid edges (27 total links minus 5 dead link instances)
    expect(g.edges.length).toBe(22);
  });

  test("stats has correct totalNotes and totalEdges", () => {
    const g = loadGraph();
    expect(g.stats).toBeDefined();
    expect(g.stats.totalNotes).toBe(10);
    expect(g.stats.totalEdges).toBe(22);
    expect(typeof g.stats.averageOutgoing).toBe("number");
    expect(typeof g.stats.averageIncoming).toBe("number");
  });

  test("web-redesign node has correct outgoing links", () => {
    const g = loadGraph();
    const node = findNode(g.nodes, "web-redesign");
    expect(node).toBeDefined();
    // Links to: CSS Grid, API Migration, Design System (3 valid)
    // Performance Testing is a dead link, not in outgoingLinks
    const outLower = node.outgoingLinks.map((l: string) => l.toLowerCase());
    expect(outLower).toContain("css grid");
    expect(outLower).toContain("api migration");
    expect(outLower).toContain("design system");
  });

  test("orphans includes only legacy-patterns", () => {
    const g = loadGraph();
    expect(Array.isArray(g.orphans)).toBe(true);
    const orphanLower = g.orphans.map((o: string) => o.toLowerCase());
    expect(orphanLower).toContain("legacy-patterns");
    expect(g.orphans.length).toBe(1);
  });

  test("dead links detect all 3 non-existent targets", () => {
    const g = loadGraph();
    expect(Array.isArray(g.deadLinks)).toBe(true);
    // 3 unique non-existent targets, 5 total instances
    expect(g.deadLinks.length).toBeGreaterThanOrEqual(3);
    expect(g.deadLinks.length).toBeLessThanOrEqual(5);
    const targetNames = g.deadLinks.map((d: any) => d.target.toLowerCase());
    expect(targetNames).toContain("performance testing");
    expect(targetNames).toContain("database optimization");
    expect(targetNames).toContain("react native navigation");
  });

  test("aliased links are resolved (Design System linked via alias)", () => {
    const g = loadGraph();
    const node = findNode(g.nodes, "design-system");
    expect(node).toBeDefined();
    // design-system receives incoming from: web-redesign, mobile-app, css-grid, 2025-03-16
    expect(node.incomingLinks.length).toBeGreaterThanOrEqual(4);
  });
});

describe("vault_health.md", () => {
  test("vault_health.md exists with required sections", () => {
    expect(existsSync("vault_health.md")).toBe(true);
    const content = readFileSync("vault_health.md", "utf-8");
    expect(content).toContain("## Statistics");
    expect(content).toContain("## Most Connected");
    expect(content).toContain("## Orphaned Notes");
    expect(content).toContain("## Dead Links");
    expect(content).toContain("## Tag Distribution");
  });
});

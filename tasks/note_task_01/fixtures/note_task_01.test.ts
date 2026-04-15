import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadNotes(): any[] {
  return JSON.parse(readFileSync("memory/notes/notes.json", "utf-8"))
}

function loadTopics(): any {
  return JSON.parse(readFileSync("memory/notes/topics.json", "utf-8"))
}

function loadProjects(): any {
  return JSON.parse(readFileSync("memory/notes/projects.json", "utf-8"))
}

function loadIndex(): any {
  return JSON.parse(readFileSync("memory/notes/search_index.json", "utf-8"))
}

describe("memory/notes/notes.json", () => {
  test("notes file exists", () => {
    expect(existsSync("memory/notes/notes.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadNotes()).not.toThrow()
  })

  test("contains exactly 4 notes", () => {
    const notes = loadNotes()
    expect(Array.isArray(notes)).toBe(true)
    expect(notes.length).toBe(4)
  })

  test("each note has id, content, topic, project, created_at, and tags fields", () => {
    const notes = loadNotes()
    for (const note of notes) {
      expect(typeof note.id).toBe("string")
      expect(typeof note.content).toBe("string")
      expect(note.content.length).toBeGreaterThan(0)
      expect(typeof note.topic).toBe("string")
      expect(typeof note.project).toBe("string")
      expect(typeof note.created_at).toBe("string")
      expect(Array.isArray(note.tags)).toBe(true)
    }
  })

  test("note IDs are NOTE-001 through NOTE-004", () => {
    const notes = loadNotes()
    const ids = notes.map((n: any) => n.id).sort()
    expect(ids).toContain("NOTE-001")
    expect(ids).toContain("NOTE-002")
    expect(ids).toContain("NOTE-003")
    expect(ids).toContain("NOTE-004")
  })

  test("each note has created_at of 2026-04-11", () => {
    const notes = loadNotes()
    for (const note of notes) {
      expect(note.created_at).toBe("2026-04-11")
    }
  })

  test("each note has 1 to 3 tags", () => {
    const notes = loadNotes()
    for (const note of notes) {
      expect(note.tags.length).toBeGreaterThanOrEqual(1)
      expect(note.tags.length).toBeLessThanOrEqual(3)
    }
  })
})

describe("memory/notes/topics.json", () => {
  test("topics file exists", () => {
    expect(existsSync("memory/notes/topics.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadTopics()).not.toThrow()
  })

  test("topics mapping: each note appears under exactly one topic key", () => {
    const t = loadTopics()
    expect(t).toHaveProperty("topics")
    const allMapped: string[] = []
    for (const noteIds of Object.values(t.topics) as string[][]) {
      for (const id of noteIds) {
        allMapped.push(id)
      }
    }
    const required = ["NOTE-001", "NOTE-002", "NOTE-003", "NOTE-004"]
    for (const id of required) {
      const count = allMapped.filter(x => x === id).length
      expect(count).toBe(1)
    }
  })
})

describe("memory/notes/projects.json", () => {
  test("projects file exists", () => {
    expect(existsSync("memory/notes/projects.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadProjects()).not.toThrow()
  })

  test("projects mapping: each note appears under at least one project key", () => {
    const p = loadProjects()
    expect(p).toHaveProperty("projects")
    const allMapped: string[] = []
    for (const noteIds of Object.values(p.projects) as string[][]) {
      for (const id of noteIds) {
        allMapped.push(id)
      }
    }
    const required = ["NOTE-001", "NOTE-002", "NOTE-003", "NOTE-004"]
    for (const id of required) {
      expect(allMapped.includes(id)).toBe(true)
    }
  })
})

describe("memory/notes/search_index.json", () => {
  test("index file exists", () => {
    expect(existsSync("memory/notes/search_index.json")).toBe(true)
  })

  test("valid JSON", () => {
    expect(() => loadIndex()).not.toThrow()
  })

  test("index has entries for all 4 notes with at least 3 keywords each", () => {
    const idx = loadIndex()
    expect(idx).toHaveProperty("index")
    expect(Array.isArray(idx.index)).toBe(true)
    expect(idx.index.length).toBe(4)
    for (const entry of idx.index) {
      expect(typeof entry.note_id).toBe("string")
      expect(Array.isArray(entry.keywords)).toBe(true)
      expect(entry.keywords.length).toBeGreaterThanOrEqual(3)
    }
  })
})

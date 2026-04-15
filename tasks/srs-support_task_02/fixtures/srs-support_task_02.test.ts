import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadData(): any {
  return JSON.parse(readFileSync("codec_matrix.json", "utf-8"))
}

describe("codec_matrix.json", () => {
  test("file exists", () => {
    expect(existsSync("codec_matrix.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadData()).not.toThrow()
  })

  test("has required top-level keys", () => {
    const d = loadData()
    expect(d).toHaveProperty("codecs")
    expect(d).toHaveProperty("transcoding_note")
    expect(d).toHaveProperty("focus")
  })

  test("codecs is an array of at least 6 entries", () => {
    const d = loadData()
    expect(Array.isArray(d.codecs)).toBe(true)
    expect(d.codecs.length).toBeGreaterThanOrEqual(6)
  })

  test("each codec has name, type, supported, notes fields", () => {
    const d = loadData()
    for (const c of d.codecs) {
      expect(typeof c.name).toBe("string")
      expect(typeof c.type).toBe("string")
      expect(typeof c.supported).toBe("boolean")
      expect(typeof c.notes).toBe("string")
    }
  })

  test("focus is transmuxing", () => {
    const d = loadData()
    expect(d.focus).toBe("transmuxing")
  })

  test("H.264 is supported", () => {
    const d = loadData()
    const h264 = d.codecs.find((c: any) => /h\.?264/i.test(c.name))
    expect(h264).toBeDefined()
    expect(h264.supported).toBe(true)
    expect(h264.type).toBe("video")
  })

  test("VP8 is not supported", () => {
    const d = loadData()
    const vp8 = d.codecs.find((c: any) => /vp8/i.test(c.name))
    expect(vp8).toBeDefined()
    expect(vp8.supported).toBe(false)
  })

  test("AAC and Opus are both present and supported", () => {
    const d = loadData()
    const aac = d.codecs.find((c: any) => /aac/i.test(c.name))
    const opus = d.codecs.find((c: any) => /opus/i.test(c.name))
    expect(aac).toBeDefined()
    expect(aac.supported).toBe(true)
    expect(opus).toBeDefined()
    expect(opus.supported).toBe(true)
  })

  test("transcoding_note is a non-empty string", () => {
    const d = loadData()
    expect(typeof d.transcoding_note).toBe("string")
    expect(d.transcoding_note.length).toBeGreaterThan(20)
  })
})

import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadData(): any {
  return JSON.parse(readFileSync("protocol_comparison.json", "utf-8"))
}

describe("protocol_comparison.json", () => {
  test("file exists", () => {
    expect(existsSync("protocol_comparison.json")).toBe(true)
  })

  test("is valid JSON", () => {
    expect(() => loadData()).not.toThrow()
  })

  test("has required top-level keys", () => {
    const d = loadData()
    expect(d).toHaveProperty("protocols")
    expect(d).toHaveProperty("summary")
  })

  test("protocols is an array of at least 5 entries", () => {
    const d = loadData()
    expect(Array.isArray(d.protocols)).toBe(true)
    expect(d.protocols.length).toBeGreaterThanOrEqual(5)
  })

  test("each protocol has name, transport, role, latency fields", () => {
    const d = loadData()
    for (const p of d.protocols) {
      expect(typeof p.name).toBe("string")
      expect(typeof p.transport).toBe("string")
      expect(typeof p.role).toBe("string")
      expect(typeof p.latency).toBe("string")
    }
  })

  test("transport is TCP or UDP for every protocol", () => {
    const d = loadData()
    for (const p of d.protocols) {
      expect(["TCP", "UDP"]).toContain(p.transport)
    }
  })

  test("RTMP is TCP", () => {
    const d = loadData()
    const rtmp = d.protocols.find((p: any) => p.name.toUpperCase() === "RTMP")
    expect(rtmp).toBeDefined()
    expect(rtmp.transport).toBe("TCP")
  })

  test("WebRTC is UDP", () => {
    const d = loadData()
    const webrtc = d.protocols.find((p: any) => /webrtc/i.test(p.name))
    expect(webrtc).toBeDefined()
    expect(webrtc.transport).toBe("UDP")
  })

  test("SRT is UDP", () => {
    const d = loadData()
    const srt = d.protocols.find((p: any) => p.name.toUpperCase() === "SRT")
    expect(srt).toBeDefined()
    expect(srt.transport).toBe("UDP")
  })

  test("summary is a non-empty string of reasonable length", () => {
    const d = loadData()
    expect(typeof d.summary).toBe("string")
    expect(d.summary.length).toBeGreaterThan(20)
  })
})

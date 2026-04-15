import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadLifecycle(): any {
  return JSON.parse(readFileSync("rights_lifecycle.json", "utf-8"))
}

describe("rights_lifecycle.json", () => {
  test("file exists", () => {
    expect(existsSync("rights_lifecycle.json")).toBe(true)
  })

  test("is valid JSON with required top-level keys", () => {
    const r = loadLifecycle()
    expect(r).toHaveProperty("catalog")
    expect(r).toHaveProperty("summary")
    expect(r).toHaveProperty("renewal_alerts")
  })

  test("catalog has exactly 4 assets", () => {
    const r = loadLifecycle()
    expect(Array.isArray(r.catalog)).toBe(true)
    expect(r.catalog.length).toBe(4)
  })

  test("each asset has required fields with correct types", () => {
    const r = loadLifecycle()
    const validStatuses = ["active", "expiring_soon", "expired"]
    for (const asset of r.catalog) {
      expect(typeof asset.asset_id).toBe("string")
      expect(typeof asset.asset_type).toBe("string")
      expect(typeof asset.license_expires).toBe("string")
      expect(typeof asset.territory).toBe("string")
      expect(typeof asset.usage_constraints).toBe("string")
      expect(validStatuses).toContain(asset.status)
      expect(typeof asset.days_until_expiry).toBe("number")
    }
  })

  test("audio asset (aud-2023-11-30-podcast) has negative days_until_expiry and status expired", () => {
    const r = loadLifecycle()
    const audio = r.catalog.find((a: any) => a.asset_id === "aud-2023-11-30-podcast")
    expect(audio).toBeDefined()
    expect(audio.days_until_expiry).toBeLessThan(0)
    expect(audio.status).toBe("expired")
  })

  test("video asset (vid-2023-05-10-tutorial) expires ~29 days out and is expiring_soon", () => {
    const r = loadLifecycle()
    const video = r.catalog.find((a: any) => a.asset_id === "vid-2023-05-10-tutorial")
    expect(video).toBeDefined()
    // Allow ±5 day tolerance around 29 days (2025-05-10 - 2025-04-11 = 29 days)
    expect(video.days_until_expiry).toBeGreaterThanOrEqual(24)
    expect(video.days_until_expiry).toBeLessThanOrEqual(34)
    expect(video.status).toBe("expiring_soon")
  })

  test("image asset (img-2024-01-15-banner) has positive days and active status", () => {
    const r = loadLifecycle()
    const image = r.catalog.find((a: any) => a.asset_id === "img-2024-01-15-banner")
    expect(image).toBeDefined()
    expect(image.days_until_expiry).toBeGreaterThan(0)
    expect(image.status).toBe("active")
  })

  test("text asset (txt-2025-02-28-article) has positive days and active status", () => {
    const r = loadLifecycle()
    const text = r.catalog.find((a: any) => a.asset_id === "txt-2025-02-28-article")
    expect(text).toBeDefined()
    expect(text.days_until_expiry).toBeGreaterThan(0)
    expect(text.status).toBe("active")
  })

  test("summary total_assets is 4 and counts sum to 4", () => {
    const r = loadLifecycle()
    const s = r.summary
    expect(s.total_assets).toBe(4)
    expect(typeof s.active_count).toBe("number")
    expect(typeof s.expiring_soon_count).toBe("number")
    expect(typeof s.expired_count).toBe("number")
    expect(s.active_count + s.expiring_soon_count + s.expired_count).toBe(4)
  })

  test("summary counts reflect actual catalog statuses", () => {
    const r = loadLifecycle()
    const active = r.catalog.filter((a: any) => a.status === "active").length
    const expiring = r.catalog.filter((a: any) => a.status === "expiring_soon").length
    const expired = r.catalog.filter((a: any) => a.status === "expired").length
    expect(r.summary.active_count).toBe(active)
    expect(r.summary.expiring_soon_count).toBe(expiring)
    expect(r.summary.expired_count).toBe(expired)
  })

  test("renewal_alerts contains expired and expiring_soon asset IDs", () => {
    const r = loadLifecycle()
    expect(Array.isArray(r.renewal_alerts)).toBe(true)
    // Both audio (expired) and video (expiring_soon) should be in alerts
    expect(r.renewal_alerts).toContain("aud-2023-11-30-podcast")
    expect(r.renewal_alerts).toContain("vid-2023-05-10-tutorial")
  })
})

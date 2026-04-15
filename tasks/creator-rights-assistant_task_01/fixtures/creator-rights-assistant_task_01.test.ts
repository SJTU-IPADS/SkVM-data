import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadABC(): any {
  return JSON.parse(readFileSync("asset_birth_certificate.json", "utf-8"))
}

function loadSidecar(): string {
  return readFileSync("abc_sidecar.md", "utf-8")
}

describe("asset_birth_certificate.json", () => {
  test("file exists", () => {
    expect(existsSync("asset_birth_certificate.json")).toBe(true)
  })

  test("is valid JSON with required top-level keys", () => {
    const abc = loadABC()
    expect(abc).toHaveProperty("asset_id")
    expect(abc).toHaveProperty("origin")
    expect(abc).toHaveProperty("identity")
    expect(abc).toHaveProperty("provenance")
    expect(abc).toHaveProperty("licensing")
    expect(abc).toHaveProperty("attribution")
    expect(abc).toHaveProperty("integrity")
    expect(abc).toHaveProperty("disclaimer_acknowledged")
  })

  test("origin has creation_timestamp and asset_identifier", () => {
    const abc = loadABC()
    expect(typeof abc.origin.creation_timestamp).toBe("string")
    expect(abc.origin.creation_timestamp).toMatch(/2024-11-20/)
    expect(typeof abc.origin.asset_identifier).toBe("string")
    expect(abc.origin.asset_identifier.length).toBeGreaterThan(0)
  })

  test("identity has primary_author Jordan Lee", () => {
    const abc = loadABC()
    expect(typeof abc.identity.primary_author).toBe("string")
    expect(abc.identity.primary_author.toLowerCase()).toMatch(/jordan lee/)
  })

  test("provenance process_type is human-authored", () => {
    const abc = loadABC()
    expect(abc.provenance.process_type).toBe("human-authored")
    expect(typeof abc.provenance.provenance_notes).toBe("string")
  })

  test("licensing has required fields reflecting the provided terms", () => {
    const abc = loadABC()
    const lic = abc.licensing
    expect(typeof lic.duration).toBe("string")
    // Should mention 2-year or 2026 expiry
    expect(lic.duration.toLowerCase() + (lic.usage_constraints || "").toLowerCase()).toMatch(/2.year|2026|expires|expir/)
    expect(typeof lic.territory).toBe("string")
    expect(lic.territory.toLowerCase()).toMatch(/worldwide|global|all territories/)
    expect(typeof lic.usage_constraints).toBe("string")
  })

  test("attribution credit_string matches provided text", () => {
    const abc = loadABC()
    expect(typeof abc.attribution.credit_string).toBe("string")
    expect(abc.attribution.credit_string.toLowerCase()).toMatch(/jordan lee/)
  })

  test("attribution has platform_notes for instagram and shopify", () => {
    const abc = loadABC()
    const pn = abc.attribution.platform_notes
    expect(typeof pn.instagram).toBe("string")
    expect(pn.instagram.trim().length).toBeGreaterThan(5)
    expect(typeof pn.shopify).toBe("string")
    expect(pn.shopify.trim().length).toBeGreaterThan(5)
  })

  test("integrity content_hash matches the provided hash exactly", () => {
    const abc = loadABC()
    expect(abc.integrity.content_hash).toBe("sha256:a3f5c2d8e1b047690ac12345678fedcba987654321abc0")
    expect(typeof abc.integrity.version_notes).toBe("string")
    expect(abc.integrity.version_notes.toLowerCase()).toMatch(/v1|final/)
  })

  test("disclaimer_acknowledged is true", () => {
    const abc = loadABC()
    expect(abc.disclaimer_acknowledged).toBe(true)
  })
})

describe("abc_sidecar.md", () => {
  test("file exists", () => {
    expect(existsSync("abc_sidecar.md")).toBe(true)
  })

  test("sidecar contains key sections and creator name", () => {
    const text = loadSidecar().toLowerCase()
    expect(text).toMatch(/jordan lee/)
    expect(text).toMatch(/license|licensing/)
    expect(text).toMatch(/attribution/)
    expect(text).toMatch(/provenance/)
  })

  test("sidecar contains content hash", () => {
    const text = loadSidecar()
    expect(text).toMatch(/sha256:a3f5c2d8e1b047690ac12345678fedcba987654321abc0/)
  })
})

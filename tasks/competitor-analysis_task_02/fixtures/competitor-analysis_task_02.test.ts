import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadBattlecard(): any {
  return JSON.parse(readFileSync("battlecard.json", "utf-8"))
}

describe("battlecard.json", () => {
  test("file exists", () => {
    expect(existsSync("battlecard.json")).toBe(true)
  })

  test("valid JSON with required top-level fields", () => {
    const b = loadBattlecard()
    expect(b).toHaveProperty("our_product")
    expect(b).toHaveProperty("competitor")
    expect(b).toHaveProperty("price_comparison")
    expect(b).toHaveProperty("feature_comparison")
    expect(b).toHaveProperty("our_advantages")
    expect(b).toHaveProperty("their_advantages")
    expect(b).toHaveProperty("win_themes")
    expect(b).toHaveProperty("objection_handling")
    expect(b).toHaveProperty("nps_comparison")
  })

  test("product names are correct", () => {
    const b = loadBattlecard()
    expect(b.our_product).toBe("StreamlineHR")
    expect(b.competitor).toBe("WorkforceHub")
  })

  test("price_comparison has correct prices", () => {
    const b = loadBattlecard()
    expect(b.price_comparison).toHaveProperty("our_price_per_user")
    expect(b.price_comparison).toHaveProperty("competitor_price_per_user")
    expect(b.price_comparison).toHaveProperty("our_price_advantage_pct")
    expect(b.price_comparison.our_price_per_user).toBe(12)
    expect(b.price_comparison.competitor_price_per_user).toBe(18)
  })

  test("price advantage is approximately 33.3%", () => {
    const b = loadBattlecard()
    const pct = b.price_comparison.our_price_advantage_pct
    expect(typeof pct).toBe("number")
    expect(Math.abs(pct - 33.3)).toBeLessThan(0.5)
  })

  test("feature_comparison has three categories with items", () => {
    const b = loadBattlecard()
    expect(b.feature_comparison).toHaveProperty("we_have_they_dont")
    expect(b.feature_comparison).toHaveProperty("they_have_we_dont")
    expect(b.feature_comparison).toHaveProperty("both_have")
    expect(Array.isArray(b.feature_comparison.we_have_they_dont)).toBe(true)
    expect(Array.isArray(b.feature_comparison.they_have_we_dont)).toBe(true)
    expect(Array.isArray(b.feature_comparison.both_have)).toBe(true)
    expect(b.feature_comparison.we_have_they_dont.length).toBeGreaterThanOrEqual(1)
    expect(b.feature_comparison.they_have_we_dont.length).toBeGreaterThanOrEqual(1)
    expect(b.feature_comparison.both_have.length).toBeGreaterThanOrEqual(1)
  })

  test("Slack integration appears in our exclusive features", () => {
    const b = loadBattlecard()
    const weOnly = b.feature_comparison.we_have_they_dont.join(" ").toLowerCase()
    expect(weOnly).toContain("slack")
  })

  test("our_advantages has at least 3 entries", () => {
    const b = loadBattlecard()
    expect(Array.isArray(b.our_advantages)).toBe(true)
    expect(b.our_advantages.length).toBeGreaterThanOrEqual(3)
  })

  test("win_themes has at least 2 entries", () => {
    const b = loadBattlecard()
    expect(Array.isArray(b.win_themes)).toBe(true)
    expect(b.win_themes.length).toBeGreaterThanOrEqual(2)
  })

  test("objection_handling is array with objection and response fields", () => {
    const b = loadBattlecard()
    expect(Array.isArray(b.objection_handling)).toBe(true)
    expect(b.objection_handling.length).toBeGreaterThanOrEqual(1)
    for (const entry of b.objection_handling) {
      expect(entry).toHaveProperty("objection")
      expect(entry).toHaveProperty("response")
    }
  })

  test("nps_comparison has correct values and StreamlineHR as leader", () => {
    const b = loadBattlecard()
    expect(b.nps_comparison.ours).toBe(42)
    expect(b.nps_comparison.theirs).toBe(38)
    expect(b.nps_comparison.leader).toBe("StreamlineHR")
  })
})

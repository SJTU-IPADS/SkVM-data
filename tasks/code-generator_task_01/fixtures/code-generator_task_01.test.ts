import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"
import { execSync } from "child_process"

function loadSummary(): any {
  return JSON.parse(readFileSync("code_summary.json", "utf-8"))
}

describe("inventory.py", () => {
  test("file exists", () => {
    expect(existsSync("inventory.py")).toBe(true)
  })

  test("contains Inventory class definition", () => {
    const content = readFileSync("inventory.py", "utf-8")
    expect(content).toMatch(/class Inventory/)
  })

  test("contains all 6 required methods", () => {
    const content = readFileSync("inventory.py", "utf-8")
    expect(content).toMatch(/def __init__\s*\(/)
    expect(content).toMatch(/def add_item\s*\(/)
    expect(content).toMatch(/def remove_item\s*\(/)
    expect(content).toMatch(/def get_total_value\s*\(/)
    expect(content).toMatch(/def get_item_count\s*\(/)
    expect(content).toMatch(/def to_dict\s*\(/)
  })

  test("Inventory class is importable and add/get_total_value work correctly", () => {
    const result = execSync(
      `python3 -c "
from inventory import Inventory
inv = Inventory()
inv.add_item('Widget', 10, 2.50)
inv.add_item('Gadget', 5, 8.00)
total = inv.get_total_value()
assert total == 65.0, f'Expected 65.0, got {total}'
print('PASS')
"`,
      { encoding: "utf-8" }
    ).trim()
    expect(result).toBe("PASS")
  })

  test("remove_item returns False when quantity insufficient", () => {
    const result = execSync(
      `python3 -c "
from inventory import Inventory
inv = Inventory()
inv.add_item('Widget', 3, 1.0)
r = inv.remove_item('Widget', 10)
assert r == False, f'Expected False, got {r}'
count = inv.get_item_count()
assert count == 1, f'Expected item still present, count={count}'
print('PASS')
"`,
      { encoding: "utf-8" }
    ).trim()
    expect(result).toBe("PASS")
  })

  test("get_item_count returns correct count", () => {
    const result = execSync(
      `python3 -c "
from inventory import Inventory
inv = Inventory()
inv.add_item('A', 1, 1.0)
inv.add_item('B', 2, 2.0)
inv.add_item('C', 3, 3.0)
assert inv.get_item_count() == 3, f'Expected 3, got {inv.get_item_count()}'
print('PASS')
"`,
      { encoding: "utf-8" }
    ).trim()
    expect(result).toBe("PASS")
  })
})

describe("test_inventory.py", () => {
  test("file exists", () => {
    expect(existsSync("test_inventory.py")).toBe(true)
  })

  test("contains at least 6 test methods", () => {
    const content = readFileSync("test_inventory.py", "utf-8")
    const testMethods = content.match(/def test_\w+/g) || []
    expect(testMethods.length).toBeGreaterThanOrEqual(6)
  })

  test("all unit tests pass", () => {
    const result = execSync(
      "python3 -m unittest test_inventory.py -v 2>&1 || true",
      { encoding: "utf-8" }
    )
    expect(result).toMatch(/OK/)
    expect(result).not.toMatch(/FAILED/)
  })
})

describe("code_summary.json", () => {
  test("file exists", () => {
    expect(existsSync("code_summary.json")).toBe(true)
  })

  test("has correct field values", () => {
    const s = loadSummary()
    expect(s.class_name).toBe("Inventory")
    expect(s.language).toBe("python")
    expect(s.method_count).toBe(6)
    expect(s.test_count).toBeGreaterThanOrEqual(6)
    expect(s.all_tests_passed).toBe(true)
  })
})

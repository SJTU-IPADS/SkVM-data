import { describe, test, expect } from "bun:test"
import { existsSync, statSync } from "fs"
import { execSync } from "child_process"

function pdfToText(pdfPath: string): string {
  try {
    const result = execSync(
      `python3 << 'PYEOF'
import sys
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader
reader = PdfReader("${pdfPath}")
for page in reader.pages:
    text = page.extract_text()
    if text:
        print(text)
PYEOF`,
      { encoding: "utf-8", timeout: 30000 }
    )
    return result
  } catch {
    return ""
  }
}

function getPdfPageCount(pdfPath: string): number {
  try {
    const result = execSync(
      `python3 << 'PYEOF'
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader
reader = PdfReader("${pdfPath}")
print(len(reader.pages))
PYEOF`,
      { encoding: "utf-8", timeout: 30000 }
    )
    return parseInt(result.trim(), 10)
  } catch {
    return 0
  }
}

describe("edited-agenda.pdf", () => {
  test("edited-agenda.pdf exists", () => {
    expect(existsSync("edited-agenda.pdf")).toBe(true)
  })

  test("is a valid PDF with 1 page", () => {
    const pages = getPdfPageCount("edited-agenda.pdf")
    expect(pages).toBeGreaterThanOrEqual(1)
  })

  test("title changed to Monthly All-Hands Meeting", () => {
    const text = pdfToText("edited-agenda.pdf")
    const lower = text.toLowerCase()
    expect(lower).toContain("monthly")
    expect(lower).toContain("all-hands")
    // Old title should not be present
    expect(lower).not.toContain("weekly team meeting")
  })

  test("typo fixed - Engineering spelled correctly", () => {
    const text = pdfToText("edited-agenda.pdf")
    const lower = text.toLowerCase()
    // Should contain the correct spelling
    expect(lower).toContain("engineering")
    // Should not contain the misspelling
    expect(lower).not.toContain("enginering")
  })

  test("original agenda items preserved", () => {
    const text = pdfToText("edited-agenda.pdf")
    const lower = text.toLowerCase()
    // Key agenda items from the original should still be there
    expect(lower).toContain("sprint")
    expect(lower).toContain("code review")
    expect(lower).toContain("roadmap")
  })
})

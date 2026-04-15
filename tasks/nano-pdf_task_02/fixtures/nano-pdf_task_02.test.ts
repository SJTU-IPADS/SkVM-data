import { describe, test, expect } from "bun:test"
import { existsSync } from "fs"
import { execSync } from "child_process"

function pdfPageText(pdfPath: string, pageIndex: number): string {
  try {
    const result = execSync(
      `python3 << 'PYEOF'
import sys
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader
reader = PdfReader("${pdfPath}")
if ${pageIndex} < len(reader.pages):
    text = reader.pages[${pageIndex}].extract_text()
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

function pdfFullText(pdfPath: string): string {
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

describe("updated-catalog.pdf", () => {
  test("updated-catalog.pdf exists", () => {
    expect(existsSync("updated-catalog.pdf")).toBe(true)
  })

  test("PDF has at least 4 pages", () => {
    const pages = getPdfPageCount("updated-catalog.pdf")
    expect(pages).toBeGreaterThanOrEqual(4)
  })

  test("cover says Summer Collection instead of Spring", () => {
    const fullText = pdfFullText("updated-catalog.pdf")
    const lower = fullText.toLowerCase()
    // Should contain "summer collection" somewhere
    expect(lower).toContain("summer collection")
  })

  test("discount updated to 15% off through September 30", () => {
    const fullText = pdfFullText("updated-catalog.pdf")
    const lower = fullText.toLowerCase()
    // Should contain the new discount info
    expect(lower).toContain("15%")
    expect(lower).toContain("september")
    // Old discount should be gone
    expect(lower).not.toContain("10% off all indoor plants through march")
  })

  test("footer updated to Q3 2026", () => {
    const fullText = pdfFullText("updated-catalog.pdf")
    const lower = fullText.toLowerCase()
    // Should contain Q3 2026 reference
    expect(lower).toContain("q3 2026")
  })

  test("original product listings preserved", () => {
    const fullText = pdfFullText("updated-catalog.pdf")
    const lower = fullText.toLowerCase()
    // Key products from original should still be present
    expect(lower).toContain("monstera")
    expect(lower).toContain("fiddle leaf")
    expect(lower).toContain("snake plant")
    expect(lower).toContain("ceramic planter")
    expect(lower).toContain("bamboo plant stand")
    // Ordering info should be preserved
    expect(lower).toContain("how to order")
  })
})

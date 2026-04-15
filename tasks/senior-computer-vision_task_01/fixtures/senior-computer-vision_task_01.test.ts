import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadArchComparison(): any {
  return JSON.parse(readFileSync("arch_comparison.json", "utf-8"))
}

function loadQuantTradeoffs(): any {
  return JSON.parse(readFileSync("quantization_tradeoffs.json", "utf-8"))
}

const KNOWN_ARCHS = new Set(["YOLOv8n", "YOLOv8m", "Faster R-CNN R50", "RT-DETR-L"])

describe("arch_comparison.json", () => {
  test("file exists", () => {
    expect(existsSync("arch_comparison.json")).toBe(true)
  })

  test("has required top-level fields", () => {
    const d = loadArchComparison()
    expect(d).toHaveProperty("task")
    expect(d).toHaveProperty("constraint_fps")
    expect(d).toHaveProperty("constraint_gpu_memory_gb")
    expect(d).toHaveProperty("architectures")
    expect(d).toHaveProperty("recommended")
    expect(d).toHaveProperty("recommendation_reason")
  })

  test("contains exactly 4 architectures", () => {
    const d = loadArchComparison()
    expect(Array.isArray(d.architectures)).toBe(true)
    expect(d.architectures.length).toBe(4)
  })

  test("each architecture has required fields with correct types", () => {
    const d = loadArchComparison()
    for (const a of d.architectures) {
      expect(typeof a.name).toBe("string")
      expect(typeof a.inference_ms).toBe("number")
      expect(typeof a.map50).toBe("number")
      expect(typeof a.model_size_mb).toBe("number")
      expect(typeof a.fits_constraints).toBe("boolean")
      expect(typeof a.notes).toBe("string")
    }
  })

  test("inference_ms values are positive and plausible (> 0, < 500)", () => {
    const d = loadArchComparison()
    for (const a of d.architectures) {
      expect(a.inference_ms).toBeGreaterThan(0)
      expect(a.inference_ms).toBeLessThan(500)
    }
  })

  test("map50 values are between 0 and 1 (fractional) or 0 and 100", () => {
    const d = loadArchComparison()
    for (const a of d.architectures) {
      // Accept either fractional (0-1) or percentage (0-100)
      expect(a.map50).toBeGreaterThan(0)
      expect(a.map50).toBeLessThanOrEqual(100)
    }
  })

  test("fits_constraints is correct: true only if inference_ms < 33 AND model_size_mb < 2048", () => {
    const d = loadArchComparison()
    for (const a of d.architectures) {
      const shouldFit = a.inference_ms < 33 && a.model_size_mb < 2048
      expect(a.fits_constraints).toBe(shouldFit)
    }
  })

  test("recommended is a known architecture name from the architectures list", () => {
    const d = loadArchComparison()
    const names = d.architectures.map((a: any) => a.name)
    expect(names).toContain(d.recommended)
  })

  test("recommendation_reason is a non-empty string", () => {
    const d = loadArchComparison()
    expect(typeof d.recommendation_reason).toBe("string")
    expect(d.recommendation_reason.length).toBeGreaterThan(10)
  })
})

describe("quantization_tradeoffs.json", () => {
  test("file exists", () => {
    expect(existsSync("quantization_tradeoffs.json")).toBe(true)
  })

  test("is an array with exactly 3 precision entries", () => {
    const d = loadQuantTradeoffs()
    expect(Array.isArray(d)).toBe(true)
    expect(d.length).toBe(3)
  })

  test("each entry has precision and speed fields", () => {
    const d = loadQuantTradeoffs()
    for (const entry of d) {
      expect(typeof entry.precision).toBe("string")
      expect(typeof entry.relative_size_pct).toBe("number")
      expect(typeof entry.relative_speed_multiplier).toBe("number")
      expect(typeof entry.max_accuracy_drop_pct).toBe("number")
    }
  })

  test("covers FP32, FP16, and INT8 precisions", () => {
    const d = loadQuantTradeoffs()
    const precisions = d.map((e: any) => e.precision)
    expect(precisions).toContain("FP32")
    expect(precisions).toContain("FP16")
    expect(precisions).toContain("INT8")
  })

  test("FP32 has relative_size_pct of 100 (baseline)", () => {
    const d = loadQuantTradeoffs()
    const fp32 = d.find((e: any) => e.precision === "FP32")
    expect(fp32).toBeDefined()
    expect(fp32.relative_size_pct).toBe(100)
  })

  test("INT8 is smaller than FP16 which is smaller than FP32", () => {
    const d = loadQuantTradeoffs()
    const fp32 = d.find((e: any) => e.precision === "FP32")
    const fp16 = d.find((e: any) => e.precision === "FP16")
    const int8 = d.find((e: any) => e.precision === "INT8")
    expect(fp16.relative_size_pct).toBeLessThan(fp32.relative_size_pct)
    expect(int8.relative_size_pct).toBeLessThan(fp16.relative_size_pct)
  })
})

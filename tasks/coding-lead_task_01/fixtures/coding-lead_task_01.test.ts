import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadResults(): any {
  return JSON.parse(readFileSync("queue_test_results.json", "utf-8"))
}

describe("task_queue.py", () => {
  test("task_queue.py file exists", () => {
    expect(existsSync("task_queue.py")).toBe(true)
  })

  test("run_tests.py file exists", () => {
    expect(existsSync("run_tests.py")).toBe(true)
  })

  test("TaskQueue class is defined in task_queue.py", () => {
    const src = readFileSync("task_queue.py", "utf-8")
    expect(src).toContain("class TaskQueue")
  })

  test("all 8 required methods are present in task_queue.py", () => {
    const src = readFileSync("task_queue.py", "utf-8")
    expect(src).toContain("def enqueue")
    expect(src).toContain("def dequeue")
    expect(src).toContain("def peek")
    expect(src).toContain("def size")
    expect(src).toContain("def is_full")
    expect(src).toContain("def is_empty")
    expect(src).toContain("def clear")
  })
})

describe("queue_test_results.json", () => {
  test("file exists", () => {
    expect(existsSync("queue_test_results.json")).toBe(true)
  })

  test("valid JSON with all required fields", () => {
    const r = loadResults()
    expect(r).toHaveProperty("enqueue_1")
    expect(r).toHaveProperty("enqueue_2")
    expect(r).toHaveProperty("enqueue_3")
    expect(r).toHaveProperty("enqueue_4_full")
    expect(r).toHaveProperty("size_after_3_enqueues")
    expect(r).toHaveProperty("is_full")
    expect(r).toHaveProperty("peek_result")
    expect(r).toHaveProperty("dequeue_result")
    expect(r).toHaveProperty("size_after_dequeue")
    expect(r).toHaveProperty("is_empty_after_clear")
  })

  test("first three enqueues return true", () => {
    const r = loadResults()
    expect(r.enqueue_1).toBe(true)
    expect(r.enqueue_2).toBe(true)
    expect(r.enqueue_3).toBe(true)
  })

  test("fourth enqueue returns false when queue is full", () => {
    const r = loadResults()
    expect(r.enqueue_4_full).toBe(false)
  })

  test("size after 3 enqueues is 3", () => {
    const r = loadResults()
    expect(r.size_after_3_enqueues).toBe(3)
  })

  test("is_full returns true when queue is at capacity", () => {
    const r = loadResults()
    expect(r.is_full).toBe(true)
  })

  test("peek returns first enqueued task (FIFO)", () => {
    const r = loadResults()
    expect(r.peek_result).toEqual({ id: 1, name: "task_a" })
  })

  test("dequeue returns first enqueued task (FIFO)", () => {
    const r = loadResults()
    expect(r.dequeue_result).toEqual({ id: 1, name: "task_a" })
  })

  test("size decrements to 2 after one dequeue", () => {
    const r = loadResults()
    expect(r.size_after_dequeue).toBe(2)
  })

  test("is_empty returns true after clear", () => {
    const r = loadResults()
    expect(r.is_empty_after_clear).toBe(true)
  })
})

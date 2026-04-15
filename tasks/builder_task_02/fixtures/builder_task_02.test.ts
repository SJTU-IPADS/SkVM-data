import { describe, test, expect } from "bun:test"
import { existsSync, readFileSync } from "fs"

function loadCMake(): string {
  return readFileSync("CMakeLists.txt", "utf-8")
}

function loadDepGraph(): any {
  return JSON.parse(readFileSync("dependency_graph.json", "utf-8"))
}

describe("CMakeLists.txt", () => {
  test("file exists", () => {
    expect(existsSync("CMakeLists.txt")).toBe(true)
  })

  test("specifies cmake_minimum_required 3.20", () => {
    const cmake = loadCMake()
    expect(cmake).toMatch(/cmake_minimum_required\s*\(\s*VERSION\s+3\.20/i)
  })

  test("project name is DataProcessor with version 2.1.0", () => {
    const cmake = loadCMake()
    expect(cmake).toMatch(/project\s*\(\s*DataProcessor/i)
    expect(cmake).toMatch(/2\.1\.0/)
  })

  test("sets CXX standard to 17", () => {
    const cmake = loadCMake()
    expect(cmake).toMatch(/CMAKE_CXX_STANDARD\s+17|CXX_STANDARD\s+17/i)
  })

  test("add_executable includes all 3 source files", () => {
    const cmake = loadCMake()
    expect(cmake).toMatch(/add_executable\s*\(\s*data_processor/i)
    expect(cmake).toMatch(/src\/main\.cpp/i)
    expect(cmake).toMatch(/src\/processor\.cpp/i)
    expect(cmake).toMatch(/src\/io_handler\.cpp/i)
  })

  test("include_directories points to include/", () => {
    const cmake = loadCMake()
    expect(cmake).toMatch(/include_directories|target_include_directories/i)
    expect(cmake).toMatch(/include\//i)
  })

  test("defines ENABLE_LOGGING=1 compile definition", () => {
    const cmake = loadCMake()
    expect(cmake).toMatch(/ENABLE_LOGGING\s*=\s*1/i)
  })

  test("has install rule for data_processor", () => {
    const cmake = loadCMake()
    expect(cmake).toMatch(/install\s*\(/i)
    expect(cmake).toMatch(/data_processor/i)
    expect(cmake).toMatch(/bin/i)
  })
})

describe("dependency_graph.json", () => {
  test("file exists", () => {
    expect(existsSync("dependency_graph.json")).toBe(true)
  })

  test("is valid JSON with required top-level fields", () => {
    const d = loadDepGraph()
    expect(d).toHaveProperty("project")
    expect(d).toHaveProperty("version")
    expect(d).toHaveProperty("build_tool")
    expect(d).toHaveProperty("cpp_standard")
    expect(d).toHaveProperty("targets")
  })

  test("project is DataProcessor version 2.1.0 with CMake", () => {
    const d = loadDepGraph()
    expect(d.project).toBe("DataProcessor")
    expect(d.version).toBe("2.1.0")
    expect(d.build_tool).toBe("CMake")
    expect(d.cpp_standard).toBe(17)
  })

  test("targets array has one entry named data_processor of type executable", () => {
    const d = loadDepGraph()
    expect(Array.isArray(d.targets)).toBe(true)
    expect(d.targets.length).toBeGreaterThanOrEqual(1)
    const target = d.targets[0]
    expect(target.name).toBe("data_processor")
    expect(target.type).toBe("executable")
  })

  test("target sources list all 3 source files", () => {
    const d = loadDepGraph()
    const target = d.targets[0]
    expect(Array.isArray(target.sources)).toBe(true)
    const sourceStr = target.sources.join(",")
    expect(sourceStr).toContain("src/main.cpp")
    expect(sourceStr).toContain("src/processor.cpp")
    expect(sourceStr).toContain("src/io_handler.cpp")
  })

  test("target compile_definitions contains ENABLE_LOGGING=1", () => {
    const d = loadDepGraph()
    const target = d.targets[0]
    expect(Array.isArray(target.compile_definitions)).toBe(true)
    expect(target.compile_definitions).toContain("ENABLE_LOGGING=1")
  })
})

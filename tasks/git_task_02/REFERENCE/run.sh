#!/usr/bin/env bash
# Entry point for the reference solution.
# cwd must be the task workspace (where _setup.sh was run).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SCRIPT_DIR/solution.sh"

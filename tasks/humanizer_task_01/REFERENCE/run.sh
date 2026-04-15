#!/usr/bin/env bash
# Reference runner for humanizer_task_01.
# Run from the workspace directory (cwd = workspace root with draft.txt).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/solution.py"

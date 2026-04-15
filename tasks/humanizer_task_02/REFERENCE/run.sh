#!/usr/bin/env bash
# Reference runner for humanizer_task_02.
# Run from the workspace directory (cwd = workspace root with article.md).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/solution.py"

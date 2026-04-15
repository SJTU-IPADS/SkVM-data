#!/usr/bin/env bash
# Reference solution runner for word-docx_task_02
# Expects cwd to be the workspace root (where draft.docx lives).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/solution.py"

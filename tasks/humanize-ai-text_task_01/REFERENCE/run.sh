#!/usr/bin/env bash
# Reference runner for humanize-ai-text_task_01.
# Run from workspace containing input.txt (copied from fixtures/).
set -euo pipefail
if [ ! -f input.txt ] && [ -f fixtures/input.txt ]; then
  cp fixtures/input.txt .
fi
python3 "$(dirname "$0")/solution.py"

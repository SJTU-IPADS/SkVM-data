#!/usr/bin/env bash
# Reference runner for frontend-slides_task_02.
# Usage: run from a workspace containing talk_outline.json (from fixtures/).
set -euo pipefail
if [ ! -f talk_outline.json ] && [ -f fixtures/talk_outline.json ]; then
  cp fixtures/talk_outline.json .
fi
python3 "$(dirname "$0")/solution.py"

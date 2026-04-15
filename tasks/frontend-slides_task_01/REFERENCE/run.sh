#!/usr/bin/env bash
# Reference runner for frontend-slides_task_01.
# Usage: run from a workspace directory that contains deck_spec.json (copied from fixtures/).
set -euo pipefail
if [ ! -f deck_spec.json ] && [ -f fixtures/deck_spec.json ]; then
  cp fixtures/deck_spec.json .
fi
python3 "$(dirname "$0")/solution.py"

#!/usr/bin/env bash
# Reference runner for schema-markup-generator_task_02.
# Run from a workspace containing page_brief.json (copied from fixtures/).
set -euo pipefail
if [ ! -f page_brief.json ] && [ -f fixtures/page_brief.json ]; then
  cp fixtures/page_brief.json .
fi
python3 "$(dirname "$0")/solution.py"

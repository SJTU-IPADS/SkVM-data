#!/usr/bin/env bash
# Reference runner for schema-markup-generator_task_01.
# Run from a workspace containing product_brief.json (copied from fixtures/).
set -euo pipefail
if [ ! -f product_brief.json ] && [ -f fixtures/product_brief.json ]; then
  cp fixtures/product_brief.json .
fi
python3 "$(dirname "$0")/solution.py"

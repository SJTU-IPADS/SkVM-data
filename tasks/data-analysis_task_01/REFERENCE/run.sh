#!/usr/bin/env bash
# Reference runner for data-analysis_task_03.
# Usage (from a workspace containing orders.csv from fixtures/):
#   bash REFERENCE/run.sh
# Or from the task dir, copy the fixture in first:
#   cp fixtures/orders.csv . && bash REFERENCE/run.sh
set -euo pipefail
if [ ! -f orders.csv ] && [ -f fixtures/orders.csv ]; then
  cp fixtures/orders.csv .
fi
python3 "$(dirname "$0")/solution.py"

#!/usr/bin/env bash
# Reference runner for document-pdf_task_01.
# Usage (from a workspace containing report_spec.json from fixtures/):
#   bash REFERENCE/run.sh
# Or from the task dir:
#   cp fixtures/report_spec.json . && bash REFERENCE/run.sh
set -euo pipefail
if [ ! -f report_spec.json ] && [ -f fixtures/report_spec.json ]; then
  cp fixtures/report_spec.json .
fi
python3 "$(dirname "$0")/solution.py"

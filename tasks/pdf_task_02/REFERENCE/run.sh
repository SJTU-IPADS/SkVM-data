#!/usr/bin/env bash
# Reference runner for pdf_task_02.
# Usage (from a workspace containing budget_report.pdf from fixtures/):
#   bash REFERENCE/run.sh
set -euo pipefail
if [ ! -f budget_report.pdf ] && [ -f fixtures/budget_report.pdf ]; then
  cp fixtures/budget_report.pdf .
fi
python3 "$(dirname "$0")/solution.py"

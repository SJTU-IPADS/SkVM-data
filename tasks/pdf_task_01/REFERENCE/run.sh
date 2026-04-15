#!/usr/bin/env bash
# Reference runner for pdf_task_01.
# Usage (from a workspace containing invoice_analysis.pdf from fixtures/):
#   bash REFERENCE/run.sh
set -euo pipefail
if [ ! -f invoice_analysis.pdf ] && [ -f fixtures/invoice_analysis.pdf ]; then
  cp fixtures/invoice_analysis.pdf .
fi
python3 "$(dirname "$0")/solution.py"

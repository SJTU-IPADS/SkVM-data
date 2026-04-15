#!/usr/bin/env bash
# Reference runner for document-pdf_task_02.
# Usage (from a workspace containing ledger.pdf from fixtures/):
#   bash REFERENCE/run.sh
set -euo pipefail
if [ ! -f ledger.pdf ] && [ -f fixtures/ledger.pdf ]; then
  cp fixtures/ledger.pdf .
fi
python3 "$(dirname "$0")/solution.py"

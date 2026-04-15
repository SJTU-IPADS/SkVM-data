#!/usr/bin/env bash
# Reference runner for excel-xlsx_task_02.
# Usage: run from a workspace that contains sales.xlsx (bench copies fixtures/ for you).
set -euo pipefail
if [ ! -f sales.xlsx ] && [ -f fixtures/sales.xlsx ]; then
  cp fixtures/sales.xlsx .
fi
python3 "$(dirname "$0")/solution.py"

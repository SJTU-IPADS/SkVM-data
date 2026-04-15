#!/usr/bin/env bash
# Reference runner for excel-xlsx_task_01.
# Usage: run from a workspace that contains inventory.xlsx (bench copies fixtures/ for you).
set -euo pipefail
if [ ! -f inventory.xlsx ] && [ -f fixtures/inventory.xlsx ]; then
  cp fixtures/inventory.xlsx .
fi
python3 "$(dirname "$0")/solution.py"

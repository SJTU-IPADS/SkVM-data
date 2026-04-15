#!/usr/bin/env bash
# Reference runner for cantian-bazi_task_02.
# Usage (cwd = workspace with skill accessible):
#   bash REFERENCE/run.sh
set -euo pipefail
python3 "$(dirname "$0")/solution.py"

#!/usr/bin/env bash
# Reference runner for risk-management-specialist_task_02
# cwd must be the workspace (where fmea_inventory.csv lives)
set -euo pipefail
python3 "$(dirname "$0")/solution.py"

#!/usr/bin/env bash
# Reference runner for risk-management-specialist_task_01
# cwd must be the workspace (where hazard_inventory.csv lives)
set -euo pipefail
python3 "$(dirname "$0")/solution.py"

#!/usr/bin/env bash
# Reference runner for cantian-bazi_task_01.
# Usage (cwd = workspace that contains the skill at ../../skills/cantian-bazi relative to task):
#   bash REFERENCE/run.sh
# The workspace must have access to the cantian-bazi skill scripts.
# When run via the bench harness the skill root is available at the path recorded in task.json.
set -euo pipefail
python3 "$(dirname "$0")/solution.py"

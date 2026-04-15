#!/usr/bin/env bash
# Reference runner for ui-design-system_task_01.
# Run from workspace that already has brand-brief.md from fixtures/.
set -euo pipefail
if [ ! -f brand-brief.md ] && [ -f fixtures/brand-brief.md ]; then
  cp fixtures/brand-brief.md .
fi
python3 "$(dirname "$0")/solution.py"

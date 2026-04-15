#!/usr/bin/env bash
# Reference runner for ui-design-system_task_02.
# Run from workspace that already has design-spec.md from fixtures/.
set -euo pipefail
if [ ! -f design-spec.md ] && [ -f fixtures/design-spec.md ]; then
  cp fixtures/design-spec.md .
fi
python3 "$(dirname "$0")/solution.py"

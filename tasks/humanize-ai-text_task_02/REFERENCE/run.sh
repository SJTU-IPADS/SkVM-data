#!/usr/bin/env bash
# Reference runner for humanize-ai-text_task_02.
# Run from workspace containing article.md (copied from fixtures/).
set -euo pipefail
if [ ! -f article.md ] && [ -f fixtures/article.md ]; then
  cp fixtures/article.md .
fi
python3 "$(dirname "$0")/solution.py"

#!/usr/bin/env bash
set -euo pipefail
if [ ! -f spec.json ] && [ -f fixtures/spec.json ]; then
  cp fixtures/spec.json .
fi
python3 "$(dirname "$0")/solution.py"

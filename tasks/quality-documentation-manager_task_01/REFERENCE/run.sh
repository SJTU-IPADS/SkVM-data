#!/usr/bin/env bash
set -euo pipefail
# Run the reference solution from the workspace directory.
# The workspace already has the fixture files copied into it.
python3 "$(dirname "$0")/solution.py"

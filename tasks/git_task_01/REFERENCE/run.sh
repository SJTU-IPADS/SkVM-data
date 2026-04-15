#!/usr/bin/env bash
# Reference runner for git_task_03. Assumes cwd is the workspace after
# _setup.sh has populated it.
set -euo pipefail
bash "$(dirname "$0")/solution.sh"

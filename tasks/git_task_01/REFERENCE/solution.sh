#!/usr/bin/env bash
# Reference solution for git_task_03.
#
# Strategy: soft-reset the feature branch onto main so every change collapses
# into the index, drop .env.local from both index and working tree (which
# also eliminates it from all history because the old commits are
# unreachable after the reset + recommit), then land a single clean
# conventional commit.
set -euo pipefail

export GIT_AUTHOR_NAME="Reference Solution"
export GIT_AUTHOR_EMAIL="ref@example.com"
export GIT_COMMITTER_NAME="Reference Solution"
export GIT_COMMITTER_EMAIL="ref@example.com"
export GIT_AUTHOR_DATE="2025-01-04T10:00:00+0000"
export GIT_COMMITTER_DATE="2025-01-04T10:00:00+0000"

git switch feature/user-api

# Flatten all 8 messy commits into the index, keep working tree.
git reset --soft main

# Remove the accidentally-committed secret from both index and working tree.
# After the soft reset + recommit below, the old commits that contained it
# become unreachable and will no longer appear in `git log -- .env.local`.
if git ls-files --error-unmatch .env.local > /dev/null 2>&1; then
  git rm --cached -f .env.local
fi
rm -f .env.local

git commit -qm "feat: add getUser endpoint with input validation"

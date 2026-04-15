#!/usr/bin/env bash
# Reference solution for git_task_02.
#
# Steps:
# 1. Use git bisect to locate the commit that broke calculate_discount.
#    The first commit (oldest) is known-good; HEAD of main is known-bad.
# 2. Write bisect-result.txt with the bad commit SHA and subject.
# 3. Call git bisect reset to exit the bisect session cleanly (avoids detached HEAD).
# 4. Recover the deleted experiment/cache branch using the experiment-cache-tip tag.
# 5. Return to main.
set -euo pipefail

REPO="$(pwd)"

# -----------------------------------------------------------------------
# Step 1 + 2: Run bisect and capture the bad commit
# -----------------------------------------------------------------------
FIRST_SHA=$(git log main --format="%H" --reverse | head -1)

# Capture all bisect output, including the "is the first bad commit" line
BISECT_OUTPUT=$(
    git bisect start 2>&1
    git bisect bad main 2>&1
    git bisect good "$FIRST_SHA" 2>&1
    git bisect run python3 -c "
from lib import calculate_discount
import sys
try:
    result = calculate_discount(100, 10)
    sys.exit(0 if result == 90.0 else 1)
except Exception:
    sys.exit(1)
" 2>&1
)

# Extract the bad commit SHA from bisect output
BAD_SHA=$(echo "$BISECT_OUTPUT" | grep " is the first bad commit" | awk '{print $1}')

# Get the subject of the bad commit (still accessible before reset)
BAD_SUBJECT=$(git log -1 --format="%s" "$BAD_SHA")

# Step 3: Reset bisect — returns HEAD to main and clears bisect state
git bisect reset

# Write the required output file
cat > bisect-result.txt << RESULTEOF
bad-commit: $BAD_SHA
subject: $BAD_SUBJECT
RESULTEOF

# -----------------------------------------------------------------------
# Step 4: Recover the deleted experiment/cache branch from the tag
# -----------------------------------------------------------------------
CACHE_SHA=$(git rev-parse experiment-cache-tip)
git switch -c experiment/cache "$CACHE_SHA"
git switch -q experiment/cache

# Step 5: Return to main
git switch main
git switch -q main

echo "Done."
echo ""
echo "bisect-result.txt:"
cat bisect-result.txt
echo ""
echo "Branches:"
git branch

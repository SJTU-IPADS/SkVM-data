#!/usr/bin/env bash
# Set up a messy feature branch for git_task_03.
#
# Creates a local repo with:
#   - `main` branch (3 clean commits on a small Node-ish project)
#   - `feature/user-api` branch (8 messy commits including WIP / oops / typo
#     messages AND a commit that introduces .env.local containing secrets)
#
# The fixture uses fixed GIT_*_DATE env vars so commit SHAs are deterministic
# across runs and across hosts (no author-timezone drift).
#
# grade.py reads `.grade_state/` to discover what the baseline state was so
# the agent cannot trivially cheat by inspecting the post-setup repo.
set -euo pipefail

export GIT_AUTHOR_NAME="Bench Fixture"
export GIT_AUTHOR_EMAIL="fixture@example.com"
export GIT_COMMITTER_NAME="Bench Fixture"
export GIT_COMMITTER_EMAIL="fixture@example.com"
export GIT_AUTHOR_DATE="2025-01-02T10:00:00+0000"
export GIT_COMMITTER_DATE="2025-01-02T10:00:00+0000"

REPO="$(pwd)"

# Clean slate — if the agent workspace already has files, the fixture may
# conflict, but bench's prepareWorkDir runs this on a fresh mktemp dir.
git init -q
git config user.name "Bench Fixture"
git config user.email "fixture@example.com"
git config commit.gpgsign false
git config tag.gpgsign false
git config init.defaultBranch main
git symbolic-ref HEAD refs/heads/main

# ------------------------------ main branch --------------------------------

echo '{"name":"user-api","version":"0.1.0","type":"module"}' > package.json
cat > README.md <<'EOF'
# user-api

A tiny Node module for exposing user records.
EOF
mkdir -p src
cat > src/index.js <<'EOF'
import { getUser } from "./user.js";

console.log(getUser(1));
EOF
git add package.json README.md src/index.js
git commit -qm "chore: initial project scaffold"

GIT_AUTHOR_DATE="2025-01-02T11:00:00+0000" \
GIT_COMMITTER_DATE="2025-01-02T11:00:00+0000" \
  git commit -q --allow-empty -m "docs: note that user.js is pending"

cat > src/lib.js <<'EOF'
export function formatName(first, last) {
  return `${first} ${last}`;
}
EOF
git add src/lib.js
GIT_AUTHOR_DATE="2025-01-02T12:00:00+0000" \
GIT_COMMITTER_DATE="2025-01-02T12:00:00+0000" \
  git commit -qm "feat: add name formatter helper"

# ---------------------------- feature branch -------------------------------

git switch -c feature/user-api 2>/dev/null

# Commit 1: wip stub
cat > src/user.js <<'EOF'
export function getUser(id) {
  // TODO
  return null;
}
EOF
git add src/user.js
GIT_AUTHOR_DATE="2025-01-03T09:00:00+0000" \
GIT_COMMITTER_DATE="2025-01-03T09:00:00+0000" \
  git commit -qm "wip: starting on endpoint"

# Commit 2: a working draft with a stray debug log
cat > src/user.js <<'EOF'
export function getUser(id) {
  console.log("DEBUG getUser", id);
  return { id, role: "member" };
}
EOF
git add src/user.js
GIT_AUTHOR_DATE="2025-01-03T10:00:00+0000" \
GIT_COMMITTER_DATE="2025-01-03T10:00:00+0000" \
  git commit -qm "feat: add user endpoint draft"

# Commit 3: fixup removing the debug
cat > src/user.js <<'EOF'
export function getUser(id) {
  return { id, role: "member" };
}
EOF
git add src/user.js
GIT_AUTHOR_DATE="2025-01-03T11:00:00+0000" \
GIT_COMMITTER_DATE="2025-01-03T11:00:00+0000" \
  git commit -qm "fixup! feat: add user endpoint draft"

# Commit 4: oops, forgot null handling
cat > src/user.js <<'EOF'
export function getUser(id) {
  if (id == null) throw new Error("id required");
  return { id, role: "member" };
}
EOF
git add src/user.js
GIT_AUTHOR_DATE="2025-01-03T12:00:00+0000" \
GIT_COMMITTER_DATE="2025-01-03T12:00:00+0000" \
  git commit -qm "oops, forgot to handle null id"

# Commit 5: accidentally committed secrets (MUST be purged from history)
cat > .env.local <<'EOF'
API_SECRET=sk_test_abc123def456
DB_PASSWORD=hunter2
STRIPE_KEY=sk_live_shouldnotbehere
EOF
git add .env.local
GIT_AUTHOR_DATE="2025-01-03T13:00:00+0000" \
GIT_COMMITTER_DATE="2025-01-03T13:00:00+0000" \
  git commit -qm "wip: local config"

# Commit 6: real validation feature
cat > src/user.js <<'EOF'
function validateId(id) {
  if (id == null) throw new Error("id required");
  if (typeof id !== "number") throw new TypeError("id must be a number");
  if (id < 0) throw new RangeError("id must be non-negative");
  return id;
}

export function getUser(id) {
  validateId(id);
  return { id, role: "member" };
}
EOF
git add src/user.js
GIT_AUTHOR_DATE="2025-01-03T14:00:00+0000" \
GIT_COMMITTER_DATE="2025-01-03T14:00:00+0000" \
  git commit -qm "feat: add validation for getUser input"

# Commit 7: typo fix
cat > src/user.js <<'EOF'
function validateId(id) {
  if (id == null) throw new Error("id is required");
  if (typeof id !== "number") throw new TypeError("id must be a number");
  if (id < 0) throw new RangeError("id must be non-negative");
  return id;
}

export function getUser(id) {
  validateId(id);
  return { id, role: "member" };
}
EOF
git add src/user.js
GIT_AUTHOR_DATE="2025-01-03T15:00:00+0000" \
GIT_COMMITTER_DATE="2025-01-03T15:00:00+0000" \
  git commit -qm "typo"

# Commit 8: final "looks good" empty-ish commit with a non-imperative message
GIT_AUTHOR_DATE="2025-01-03T16:00:00+0000" \
GIT_COMMITTER_DATE="2025-01-03T16:00:00+0000" \
  git commit -q --allow-empty -m "added more stuff"

# --------------- record baseline state for grade.py -------------------------
mkdir -p .grade_state
git rev-parse main > .grade_state/main_sha
git log main --format="%s" > .grade_state/main_subjects
git log feature/user-api --not main --format="%s" > .grade_state/feature_subjects_before
git show feature/user-api:src/user.js > .grade_state/expected_user_js_substrings
# grade.py only reads this file to confirm the agent's final HEAD includes the
# same validation logic — we just snapshot the "good" version. .grade_state/
# is git-ignored so it doesn't pollute the repo but still sits in the
# workspace for grade.py to read.
cat > .gitignore <<'EOF'
.grade_state/
EOF
# Already tracked files have been committed; ignore doesn't affect them.
# Stay on feature branch — the agent starts where the work is.
git status -s > .grade_state/status_after_setup || true

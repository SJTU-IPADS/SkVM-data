#!/usr/bin/env bash
# _setup.sh for git_task_02
#
# Creates a local repo with:
#   - main branch: 10 commits on a Python pricing library
#   - A regression introduced in one commit (calculate_discount divides by 10 instead of 100)
#   - A tag 'experiment-cache-tip' pointing to the tip of the deleted experiment/cache branch
#
# grade.py reads .grade_state/ to discover the correct regression SHA and cache tip SHA.
#
# Note: uses `git switch -c foo` then `git switch -q foo` separately —
# `git switch -cq foo` is broken on git 2.50.
set -euo pipefail

export GIT_AUTHOR_NAME="Bench Fixture"
export GIT_AUTHOR_EMAIL="fixture@example.com"
export GIT_COMMITTER_NAME="Bench Fixture"
export GIT_COMMITTER_EMAIL="fixture@example.com"

REPO="$(pwd)"

git init -q
git config user.name "Bench Fixture"
git config user.email "fixture@example.com"
git config commit.gpgsign false
git config tag.gpgsign false
git config init.defaultBranch main
git symbolic-ref HEAD refs/heads/main

# ---- Commit 1: initial library (KNOWN GOOD) ----
cat > lib.py << 'PYEOF'
"""Pricing utilities."""

def calculate_discount(price: float, pct: int) -> float:
    """Return price after applying pct% discount."""
    return round(price * (1 - pct / 100), 2)

def apply_tax(price: float, rate: float) -> float:
    """Return price with tax applied."""
    return round(price * (1 + rate), 2)
PYEOF

cat > test_lib.py << 'PYEOF'
"""Quick regression check -- run: python3 test_lib.py"""
from lib import calculate_discount, apply_tax

assert calculate_discount(100, 10) == 90.0, f"got {calculate_discount(100,10)}"
assert calculate_discount(200, 25) == 150.0, f"got {calculate_discount(200,25)}"
assert apply_tax(100, 0.1) == 110.0, f"got {apply_tax(100, 0.1)}"
print("all tests passed")
PYEOF

export GIT_AUTHOR_DATE="2025-03-01T09:00:00+0000"
export GIT_COMMITTER_DATE="2025-03-01T09:00:00+0000"
git add lib.py test_lib.py
git commit -qm "feat: add calculate_discount and apply_tax"

# ---- Commit 2: add README ----
cat > README.md << 'MDEOF'
# pricing-utils

A small Python pricing library.

## Usage
```python
from lib import calculate_discount, apply_tax
```
MDEOF

export GIT_AUTHOR_DATE="2025-03-01T10:00:00+0000"
export GIT_COMMITTER_DATE="2025-03-01T10:00:00+0000"
git add README.md
git commit -qm "docs: add README"

# ---- Commit 3: add format_currency ----
cat >> lib.py << 'PYEOF'

def format_currency(amount: float, symbol: str = "$") -> str:
    """Format amount as currency string."""
    return f"{symbol}{amount:.2f}"
PYEOF
export GIT_AUTHOR_DATE="2025-03-01T11:00:00+0000"
export GIT_COMMITTER_DATE="2025-03-01T11:00:00+0000"
git add lib.py
git commit -qm "feat: add format_currency helper"

# ---- Commit 4: add net_price (experiment/cache branches off here) ----
cat > lib.py << 'PYEOF'
"""Pricing utilities."""

def calculate_discount(price: float, pct: int) -> float:
    """Return price after applying pct% discount."""
    return round(price * (1 - pct / 100), 2)

def apply_tax(price: float, rate: float) -> float:
    """Return price with tax applied (rate as decimal, e.g. 0.1 for 10%)."""
    return round(price * (1 + rate), 2)

def format_currency(amount: float, symbol: str = "$") -> str:
    """Format amount as currency string."""
    return f"{symbol}{amount:.2f}"

def net_price(price: float, discount_pct: int, tax_rate: float) -> float:
    """Apply discount then tax and return final price."""
    discounted = calculate_discount(price, discount_pct)
    return apply_tax(discounted, tax_rate)
PYEOF
export GIT_AUTHOR_DATE="2025-03-01T12:00:00+0000"
export GIT_COMMITTER_DATE="2025-03-01T12:00:00+0000"
git add lib.py
git commit -qm "feat: add net_price combining discount and tax"

# ---- Create experiment/cache branch (it will be deleted before the task begins) ----
git switch -c experiment/cache
git switch -q experiment/cache
export GIT_AUTHOR_DATE="2025-03-01T12:30:00+0000"
export GIT_COMMITTER_DATE="2025-03-01T12:30:00+0000"
cat > cache.py << 'PYEOF'
"""Simple memoization cache for pricing calculations."""
_cache: dict = {}

def cached_net_price(price: float, discount_pct: int, tax_rate: float) -> float:
    from lib import net_price
    key = (price, discount_pct, tax_rate)
    if key not in _cache:
        _cache[key] = net_price(price, discount_pct, tax_rate)
    return _cache[key]
PYEOF
git add cache.py
git commit -qm "feat: add memoization cache for net_price"
CACHE_TIP_SHA=$(git rev-parse HEAD)

# Tag the tip so the agent can find it
git tag experiment-cache-tip

# Return to main
git switch main
git switch -q main

# ---- Commit 5 (on main): THE REGRESSION ----
# divides by 10 instead of 100 — causing massive "discounts"
cat > lib.py << 'PYEOF'
"""Pricing utilities."""

def calculate_discount(price: float, pct: int) -> float:
    """Return price after applying pct% discount."""
    # BUG: divides by 10 instead of 100
    return round(price * (1 - pct / 10), 2)

def apply_tax(price: float, rate: float) -> float:
    """Return price with tax applied (rate as decimal, e.g. 0.1 for 10%)."""
    return round(price * (1 + rate), 2)

def format_currency(amount: float, symbol: str = "$") -> str:
    """Format amount as currency string."""
    return f"{symbol}{amount:.2f}"

def net_price(price: float, discount_pct: int, tax_rate: float) -> float:
    """Apply discount then tax and return final price."""
    discounted = calculate_discount(price, discount_pct)
    return apply_tax(discounted, tax_rate)
PYEOF
export GIT_AUTHOR_DATE="2025-03-02T09:00:00+0000"
export GIT_COMMITTER_DATE="2025-03-02T09:00:00+0000"
git add lib.py
git commit -qm "perf: optimize discount calculation loop"
REGRESSION_SHA=$(git rev-parse HEAD)

# ---- Commit 6: unrelated — add logging ----
cat > logging_utils.py << 'PYEOF'
"""Simple logging for pricing events."""
import datetime

def log_transaction(price: float, final: float) -> None:
    ts = datetime.datetime.now().isoformat()
    print(f"[{ts}] price={price:.2f} final={final:.2f}")
PYEOF
export GIT_AUTHOR_DATE="2025-03-02T10:00:00+0000"
export GIT_COMMITTER_DATE="2025-03-02T10:00:00+0000"
git add logging_utils.py
git commit -qm "feat: add transaction logging utility"

# ---- Commit 7: unrelated — add config ----
cat > config.py << 'PYEOF'
"""Runtime configuration."""
DEFAULT_CURRENCY = "$"
DEFAULT_TAX_RATE = 0.08
MAX_DISCOUNT_PCT = 90
PYEOF
export GIT_AUTHOR_DATE="2025-03-02T11:00:00+0000"
export GIT_COMMITTER_DATE="2025-03-02T11:00:00+0000"
git add config.py
git commit -qm "chore: add runtime config module"

# ---- Commit 8: placeholder ----
export GIT_AUTHOR_DATE="2025-03-02T12:00:00+0000"
export GIT_COMMITTER_DATE="2025-03-02T12:00:00+0000"
git commit -q --allow-empty -m "ci: add placeholder for future CI config"

# ---- Commit 9: more logging (HEAD, still broken) ----
export GIT_AUTHOR_DATE="2025-03-02T13:00:00+0000"
export GIT_COMMITTER_DATE="2025-03-02T13:00:00+0000"
cat >> logging_utils.py << 'PYEOF'

def log_discount(original: float, discounted: float) -> None:
    pct_off = (1 - discounted / original) * 100
    print(f"discount applied: {pct_off:.1f}% off")
PYEOF
git add logging_utils.py
git commit -qm "feat: add discount logging"

# ---- Delete experiment/cache — simulates "lost" branch ----
git branch -D experiment/cache

# ---- Add .gitignore so .grade_state/ is not visible to the agent ----
cat > .gitignore << 'GITEOF'
.grade_state/
GITEOF
git add .gitignore
export GIT_AUTHOR_DATE="2025-03-02T14:00:00+0000"
export GIT_COMMITTER_DATE="2025-03-02T14:00:00+0000"
git commit -qm "chore: add gitignore"

# ---- Save baseline state for grade.py ----
mkdir -p .grade_state
# Record main's final SHA (after the gitignore commit)
git rev-parse main > .grade_state/main_sha_before
echo "$REGRESSION_SHA" > .grade_state/regression_sha
echo "$CACHE_TIP_SHA" > .grade_state/cache_tip_sha

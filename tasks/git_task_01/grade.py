"""
Grade function for git_task_03.

Returns a list of criterion records per docs/skvm/grade-py-protocol.md.
Checks are direct git inspections — no bun test subprocess, no JUnit.

The fixture _setup.sh records baseline state under .grade_state/ so grade.py
can compare the agent's post-cleanup branch against what the original repo
looked like.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


CONVENTIONAL_RE = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|chore|build|ci|revert)(\([^)]+\))?!?:\s.+$")
WIP_RE = re.compile(r"\b(wip|fixup|squash|oops|typo|temp|tmp|checkpoint|misc)\b", re.IGNORECASE)
NON_IMPERATIVE_PREFIXES = ("added ", "fixed ", "updated ", "changed ", "removed ", "deleted ", "adding ", "fixing ", "updating ", "changing ", "removing ")
REQUIRED_USER_JS_SUBSTRINGS = ("validateId", "non-negative")


def _run(cmd: list[str], cwd: str) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return 1, "", f"{type(e).__name__}: {e}"
    return p.returncode, p.stdout, p.stderr


def _feature_subjects(cwd: str) -> list[str] | None:
    code, out, _ = _run(["git", "log", "feature/user-api", "--not", "main", "--format=%s"], cwd)
    if code != 0:
        return None
    return [line for line in out.strip().splitlines() if line]


def _check_main_unchanged(ctx: dict):
    cwd = ctx["cwd"]
    state = ctx["state_dir"]
    sha_file = state / "main_sha"
    if not sha_file.exists():
        return 0.0, ".grade_state/main_sha missing (fixture not set up)"
    expected = sha_file.read_text().strip()
    code, out, err = _run(["git", "rev-parse", "main"], cwd)
    if code != 0:
        return 0.0, f"git rev-parse main failed: {err.strip()[:120]}"
    got = out.strip()
    if got != expected:
        return 0.0, f"main branch was rewritten: expected {expected[:12]}, got {got[:12]}"
    return 1.0, None


def _check_feature_branch_exists(ctx: dict):
    cwd = ctx["cwd"]
    code, _out, _err = _run(["git", "rev-parse", "--verify", "feature/user-api"], cwd)
    if code != 0:
        return 0.0, "feature/user-api branch does not exist"
    return 1.0, None


def _check_no_secret_in_history(ctx: dict):
    cwd = ctx["cwd"]
    code, out, err = _run(
        ["git", "log", "feature/user-api", "--format=%H", "--", ".env.local"],
        cwd,
    )
    if code != 0:
        return 0.0, f"git log failed: {err.strip()[:120]}"
    commits = [c for c in out.strip().splitlines() if c]
    if commits:
        return 0.0, (
            f".env.local still present in {len(commits)} commit(s) on feature/user-api — "
            f"history was not purged (sample: {commits[0][:12]})"
        )
    return 1.0, None


def _check_head_has_validation(ctx: dict):
    cwd = ctx["cwd"]
    code, out, err = _run(["git", "show", "feature/user-api:src/user.js"], cwd)
    if code != 0:
        return 0.0, f"feature/user-api:src/user.js not readable: {err.strip()[:120]}"
    missing = [s for s in REQUIRED_USER_JS_SUBSTRINGS if s not in out]
    if missing:
        return 0.0, f"feature HEAD src/user.js missing required markers: {missing}"
    return 1.0, None


def _check_head_no_env_local(ctx: dict):
    cwd = ctx["cwd"]
    code, out, _err = _run(["git", "ls-tree", "-r", "feature/user-api", "--name-only"], cwd)
    if code != 0:
        return 0.0, "git ls-tree feature/user-api failed"
    paths = out.splitlines()
    if ".env.local" in paths:
        return 0.0, ".env.local is still tracked in feature/user-api HEAD tree"
    return 1.0, None


def _check_commit_count_reduced(ctx: dict):
    subjects = _feature_subjects(ctx["cwd"])
    if subjects is None:
        return 0.0, "could not list feature commits"
    n = len(subjects)
    if n < 1:
        return 0.0, f"feature/user-api has {n} commits over main (expected 1..5)"
    if n > 5:
        return 0.0, f"feature/user-api has {n} commits over main — expected cleanup down from 8 to at most 5"
    return 1.0, None


def _check_conventional_commits(ctx: dict):
    subjects = _feature_subjects(ctx["cwd"])
    if subjects is None:
        return 0.0, "could not list feature commits"
    if not subjects:
        return 0.0, "no commits on feature/user-api"
    bad = [s for s in subjects if not CONVENTIONAL_RE.match(s)]
    if bad:
        return 0.0, f"{len(bad)}/{len(subjects)} commits do not match conventional format; first: {bad[0]!r}"
    return 1.0, None


def _check_no_wip_messages(ctx: dict):
    subjects = _feature_subjects(ctx["cwd"])
    if subjects is None:
        return 0.0, "could not list feature commits"
    bad = [s for s in subjects if WIP_RE.search(s)]
    if bad:
        return 0.0, f"{len(bad)} commit(s) still contain wip/fixup/oops/typo wording; first: {bad[0]!r}"
    return 1.0, None


def _check_subject_under_72(ctx: dict):
    subjects = _feature_subjects(ctx["cwd"])
    if subjects is None:
        return 0.0, "could not list feature commits"
    bad = [(len(s), s) for s in subjects if len(s) > 72]
    if bad:
        return 0.0, f"{len(bad)} commit subject(s) exceed 72 chars; first: {bad[0][0]} chars — {bad[0][1]!r}"
    return 1.0, None


def _check_imperative_mood(ctx: dict):
    subjects = _feature_subjects(ctx["cwd"])
    if subjects is None:
        return 0.0, "could not list feature commits"
    bad = []
    for s in subjects:
        # Conventional prefix like "feat: " — strip before checking the body mood.
        body_match = re.match(r"^[a-z]+(\([^)]+\))?!?:\s*(.*)$", s)
        body = body_match.group(2) if body_match else s
        if body.lower().startswith(NON_IMPERATIVE_PREFIXES):
            bad.append(s)
    if bad:
        return 0.0, (
            f"{len(bad)} commit subject(s) use past-tense / gerund (non-imperative); "
            f"first: {bad[0]!r}"
        )
    return 1.0, None


def _check_no_conflict_markers(ctx: dict):
    cwd = ctx["cwd"]
    code, out, _err = _run(["git", "ls-tree", "-r", "feature/user-api", "--name-only"], cwd)
    if code != 0:
        return 0.0, "git ls-tree failed"
    paths = [p for p in out.splitlines() if p]
    markers = ("<<<<<<<", "=======", ">>>>>>>")
    bad = []
    for p in paths:
        show_code, content, _ = _run(["git", "show", f"feature/user-api:{p}"], cwd)
        if show_code != 0:
            continue
        if any(m in content for m in markers):
            bad.append(p)
    if bad:
        return 0.0, f"conflict markers found in {bad}"
    return 1.0, None


CRITERIA = [
    {
        "id": "main-unchanged",
        "weight": 0.10,
        "description": "The `main` branch SHA is unchanged from the fixture baseline — the agent must not rewrite history on the shared main branch, per SKILL.md core rule 'Never force push to shared branches'.",
        "check": _check_main_unchanged,
    },
    {
        "id": "feature-branch-exists",
        "weight": 0.05,
        "description": "The `feature/user-api` branch still exists after cleanup.",
        "check": _check_feature_branch_exists,
    },
    {
        "id": "no-secret-in-history",
        "weight": 0.18,
        "description": "`.env.local` appears in no commit on feature/user-api — the secrets file must be purged from history (not merely removed in a new commit), so a future `git log -- .env.local` returns empty.",
        "check": _check_no_secret_in_history,
    },
    {
        "id": "head-tree-has-validation",
        "weight": 0.10,
        "description": "The HEAD of feature/user-api still contains src/user.js with the `validateId` helper and the 'non-negative' error message — cleanup must preserve the final feature work.",
        "check": _check_head_has_validation,
    },
    {
        "id": "head-tree-no-env-local",
        "weight": 0.05,
        "description": "`.env.local` does not exist in the feature/user-api HEAD tree (working-tree and index clean, not just historically purged).",
        "check": _check_head_no_env_local,
    },
    {
        "id": "commit-count-reduced",
        "weight": 0.10,
        "description": "The feature/user-api branch has between 1 and 5 commits over main (cleaned up from the original 8 messy commits via squash/drop).",
        "check": _check_commit_count_reduced,
    },
    {
        "id": "conventional-commits",
        "weight": 0.15,
        "description": "Every commit on feature/user-api (not on main) has a subject matching the conventional commit format `type(scope?)!?: description` with a recognised type (feat/fix/docs/style/refactor/perf/test/chore/build/ci/revert), per SKILL.md commit-message rules.",
        "check": _check_conventional_commits,
    },
    {
        "id": "no-wip-messages",
        "weight": 0.10,
        "description": "No commit subject on feature/user-api contains WIP / fixup / oops / typo / squash / temp wording — the cleanup must have rewritten those messages, not preserved them.",
        "check": _check_no_wip_messages,
    },
    {
        "id": "subject-under-72",
        "weight": 0.07,
        "description": "Every commit subject on feature/user-api is at most 72 characters, per the SKILL.md commit-message rule.",
        "check": _check_subject_under_72,
    },
    {
        "id": "imperative-mood",
        "weight": 0.05,
        "description": "No commit subject starts with past-tense or gerund verbs (added/fixed/adding/fixing/updating/…); subjects must use imperative mood per SKILL.md.",
        "check": _check_imperative_mood,
    },
    {
        "id": "no-conflict-markers",
        "weight": 0.05,
        "description": "No file in feature/user-api HEAD contains leftover merge-conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).",
        "check": _check_no_conflict_markers,
    },
]

_w_sum = sum(c["weight"] for c in CRITERIA)
assert abs(_w_sum - 1.0) < 1e-3, f"CRITERIA weights sum to {_w_sum}, expected 1.0"


def grade(transcript, workspace_path):
    ctx = {
        "cwd": workspace_path,
        "state_dir": Path(workspace_path) / ".grade_state",
    }
    records = []
    # If this workspace isn't a git repo at all, everything fails loudly.
    code, _out, _err = _run(["git", "rev-parse", "--git-dir"], workspace_path)
    is_git_repo = code == 0

    for spec in CRITERIA:
        if not is_git_repo:
            records.append({
                "id": spec["id"],
                "score": 0.0,
                "weight": spec["weight"],
                "description": spec["description"],
                "details": "workspace is not a git repository",
            })
            continue
        score, details = spec["check"](ctx)
        record = {
            "id": spec["id"],
            "score": float(score),
            "weight": float(spec["weight"]),
            "description": spec["description"],
        }
        if details is not None and score < 1.0:
            record["details"] = details
        records.append(record)
    return records

"""
Grade function for git_task_02.

Returns a list of criterion records per docs/skvm/grade-py-protocol.md.
Checks are direct git inspections — no bun test subprocess, no JUnit.

The fixture _setup.sh records baseline state under .grade_state/ so grade.py
can compare the agent's post-investigation state against the known-correct values.

Task: use git bisect to find a regression commit, write bisect-result.txt in a
pinned format, reset bisect cleanly, and recover a deleted branch from a tag.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path


def _run(cmd: list[str], cwd: str) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return 1, "", f"{type(e).__name__}: {e}"
    return p.returncode, p.stdout, p.stderr


def _check_bisect_result_exists(ctx: dict):
    path = Path(ctx["cwd"]) / "bisect-result.txt"
    if not path.exists():
        return 0.0, "bisect-result.txt does not exist at workspace root"
    return 1.0, None


def _check_bisect_result_format(ctx: dict):
    path = Path(ctx["cwd"]) / "bisect-result.txt"
    if not path.exists():
        return 0.0, "bisect-result.txt missing — cannot check format"
    text = path.read_text().strip()
    lines = text.splitlines()
    if len(lines) < 2:
        return 0.0, f"bisect-result.txt must have at least 2 lines (got {len(lines)}): {text[:120]!r}"
    # Line 1: "bad-commit: <40-hex-sha>"
    if not re.match(r"^bad-commit:\s+[0-9a-f]{40}$", lines[0]):
        return 0.0, f"Line 1 must match 'bad-commit: <40-hex-sha>', got: {lines[0]!r}"
    # Line 2: "subject: <text>"
    if not re.match(r"^subject:\s+\S", lines[1]):
        return 0.0, f"Line 2 must match 'subject: <text>', got: {lines[1]!r}"
    return 1.0, None


def _check_bisect_correct_sha(ctx: dict):
    path = Path(ctx["cwd"]) / "bisect-result.txt"
    state = ctx["state_dir"]
    if not path.exists():
        return 0.0, "bisect-result.txt missing"
    regression_sha_file = state / "regression_sha"
    if not regression_sha_file.exists():
        return 0.0, ".grade_state/regression_sha missing (fixture not run)"
    expected_sha = regression_sha_file.read_text().strip()
    text = path.read_text().strip()
    lines = text.splitlines()
    if not lines:
        return 0.0, "bisect-result.txt is empty"
    match = re.match(r"^bad-commit:\s+([0-9a-f]{40})$", lines[0])
    if not match:
        return 0.0, f"Could not parse SHA from line 1: {lines[0]!r}"
    got_sha = match.group(1)
    if got_sha != expected_sha:
        return 0.0, (
            f"Wrong commit identified: expected {expected_sha[:12]} "
            f"('perf: optimize discount calculation loop'), got {got_sha[:12]}"
        )
    return 1.0, None


def _check_bisect_subject_matches(ctx: dict):
    """The subject line in bisect-result.txt must match the regression commit's subject."""
    path = Path(ctx["cwd"]) / "bisect-result.txt"
    state = ctx["state_dir"]
    if not path.exists():
        return 0.0, "bisect-result.txt missing"
    regression_sha_file = state / "regression_sha"
    if not regression_sha_file.exists():
        return 0.0, ".grade_state/regression_sha missing"
    regression_sha = regression_sha_file.read_text().strip()
    code, out, err = _run(["git", "log", "-1", "--format=%s", regression_sha], ctx["cwd"])
    if code != 0:
        return 0.0, f"Could not read regression commit subject: {err.strip()[:80]}"
    expected_subject = out.strip()
    text = path.read_text().strip()
    lines = text.splitlines()
    if len(lines) < 2:
        return 0.0, "bisect-result.txt has fewer than 2 lines"
    match = re.match(r"^subject:\s+(.+)$", lines[1])
    if not match:
        return 0.0, f"Line 2 does not start with 'subject: ': {lines[1]!r}"
    got_subject = match.group(1).strip()
    if got_subject != expected_subject:
        return 0.0, f"Subject mismatch: expected {expected_subject!r}, got {got_subject!r}"
    return 1.0, None


def _check_no_bisect_in_progress(ctx: dict):
    """No bisect session must be in progress — .git/BISECT_HEAD and .git/BISECT_LOG must be absent."""
    cwd = ctx["cwd"]
    bisect_head = Path(cwd) / ".git" / "BISECT_HEAD"
    if bisect_head.exists():
        return 0.0, (
            ".git/BISECT_HEAD still exists — bisect session is still active; "
            "call 'git bisect reset' to exit the session and return HEAD to main"
        )
    bisect_log = Path(cwd) / ".git" / "BISECT_LOG"
    if bisect_log.exists():
        return 0.0, (
            ".git/BISECT_LOG still exists — bisect session is still active; "
            "call 'git bisect reset'"
        )
    return 1.0, None


def _check_head_on_main_not_detached(ctx: dict):
    """After bisect reset, HEAD must be on branch main (not detached)."""
    cwd = ctx["cwd"]
    code, out, err = _run(["git", "symbolic-ref", "HEAD"], cwd)
    if code != 0:
        return 0.0, (
            "HEAD is detached — 'git bisect reset' was not called or the agent "
            "left HEAD in detached state; run 'git switch main' to fix"
        )
    ref = out.strip()
    if ref != "refs/heads/main":
        return 0.0, f"HEAD is on {ref!r}, expected refs/heads/main — switch back to main after bisect"
    return 1.0, None


def _check_main_sha_unchanged(ctx: dict):
    """main branch SHA must equal the fixture baseline — nothing should have rewritten it."""
    cwd = ctx["cwd"]
    state = ctx["state_dir"]
    sha_file = state / "main_sha_before"
    if not sha_file.exists():
        return 0.0, ".grade_state/main_sha_before missing (fixture not run)"
    expected = sha_file.read_text().strip()
    code, out, err = _run(["git", "rev-parse", "main"], cwd)
    if code != 0:
        return 0.0, f"git rev-parse main failed: {err.strip()[:80]}"
    got = out.strip()
    if got != expected:
        return 0.0, f"main was rewritten: expected {expected[:12]}, got {got[:12]}"
    return 1.0, None


def _check_experiment_cache_exists(ctx: dict):
    """The experiment/cache branch must exist — it was deleted and needs to be recovered."""
    cwd = ctx["cwd"]
    code, out, err = _run(["git", "rev-parse", "--verify", "experiment/cache"], cwd)
    if code != 0:
        return 0.0, (
            "experiment/cache branch does not exist — recover it using "
            "'git switch -c experiment/cache experiment-cache-tip' or reflog"
        )
    return 1.0, None


def _check_experiment_cache_correct_tip(ctx: dict):
    """experiment/cache must point to the exact SHA that was its tip before deletion."""
    cwd = ctx["cwd"]
    state = ctx["state_dir"]
    sha_file = state / "cache_tip_sha"
    if not sha_file.exists():
        return 0.0, ".grade_state/cache_tip_sha missing"
    expected_sha = sha_file.read_text().strip()
    code, out, err = _run(["git", "rev-parse", "experiment/cache"], cwd)
    if code != 0:
        return 0.0, f"experiment/cache branch does not exist: {err.strip()[:80]}"
    got_sha = out.strip()
    if got_sha != expected_sha:
        return 0.0, (
            f"experiment/cache points to {got_sha[:12]}, expected {expected_sha[:12]} "
            f"(the original tip before deletion — use the experiment-cache-tip tag)"
        )
    return 1.0, None


def _check_cache_py_in_experiment_branch(ctx: dict):
    """experiment/cache HEAD must contain cache.py with the memoization function."""
    cwd = ctx["cwd"]
    code, out, err = _run(["git", "show", "experiment/cache:cache.py"], cwd)
    if code != 0:
        return 0.0, f"experiment/cache:cache.py not readable: {err.strip()[:80]}"
    if "cached_net_price" not in out:
        return 0.0, "experiment/cache:cache.py does not contain 'cached_net_price' — wrong commit was recovered"
    return 1.0, None


CRITERIA = [
    {
        "id": "bisect-result-exists",
        "weight": 0.08,
        "description": "bisect-result.txt exists at the workspace root — the agent must create this file to record the bisect finding before exiting the bisect session.",
        "check": _check_bisect_result_exists,
    },
    {
        "id": "bisect-result-format",
        "weight": 0.10,
        "description": "bisect-result.txt contains exactly two lines in the required format: line 1 is 'bad-commit: <40-hex-sha>' and line 2 is 'subject: <commit subject text>' — both keys and the SHA format are pinned.",
        "check": _check_bisect_result_format,
    },
    {
        "id": "bisect-correct-sha",
        "weight": 0.22,
        "description": "The SHA in bisect-result.txt identifies the exact regression commit ('perf: optimize discount calculation loop') that changed the divisor from 100 to 10 — verifies that git bisect converged on the correct commit.",
        "check": _check_bisect_correct_sha,
    },
    {
        "id": "bisect-subject-matches",
        "weight": 0.08,
        "description": "The subject field in bisect-result.txt matches the commit message of the identified bad commit exactly — confirms the agent recorded the correct metadata alongside the SHA.",
        "check": _check_bisect_subject_matches,
    },
    {
        "id": "no-bisect-in-progress",
        "weight": 0.08,
        "description": "No active bisect session remains: .git/BISECT_HEAD and .git/BISECT_LOG are both absent, meaning 'git bisect reset' was called to cleanly exit the bisect session after recording the result.",
        "check": _check_no_bisect_in_progress,
    },
    {
        "id": "head-on-main-not-detached",
        "weight": 0.10,
        "description": "HEAD is attached to the main branch (symbolic-ref HEAD == refs/heads/main), not in detached HEAD state — the SKILL.md warns 'Detached HEAD: use git switch - to return to previous branch', and bisect leaves HEAD detached until reset is called.",
        "check": _check_head_on_main_not_detached,
    },
    {
        "id": "main-sha-unchanged",
        "weight": 0.07,
        "description": "The main branch tip SHA equals the fixture baseline recorded before the task started — bisect and branch recovery must not rewrite or advance the shared main branch.",
        "check": _check_main_sha_unchanged,
    },
    {
        "id": "experiment-cache-exists",
        "weight": 0.12,
        "description": "The experiment/cache branch exists after recovery — it was deleted before the task began and must be restored, most directly via 'git switch -c experiment/cache experiment-cache-tip'.",
        "check": _check_experiment_cache_exists,
    },
    {
        "id": "experiment-cache-correct-tip",
        "weight": 0.10,
        "description": "experiment/cache points to the exact SHA referenced by the experiment-cache-tip tag — recovery must restore the branch pointer to the original commit, not an ancestor or sibling.",
        "check": _check_experiment_cache_correct_tip,
    },
    {
        "id": "cache-py-present-in-branch",
        "weight": 0.05,
        "description": "experiment/cache HEAD tree contains cache.py with the 'cached_net_price' memoization function — confirms the correct commit was recovered, not just a nearby ancestor.",
        "check": _check_cache_py_in_experiment_branch,
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

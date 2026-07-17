"""Lightweight git integration used to auto-tag tasks and sessions.

This deliberately shells out to the `git` binary rather than depending on
a third-party library, keeping FlowCLI's dependency footprint small.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


def _run_git(args: list[str], cwd: Optional[Path] = None) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    if result.returncode != 0:
        return None
    output = result.stdout.strip()
    return output or None


def is_git_repo(cwd: Optional[Path] = None) -> bool:
    return _run_git(["rev-parse", "--is-inside-work-tree"], cwd) == "true"


def current_branch(cwd: Optional[Path] = None) -> Optional[str]:
    if not is_git_repo(cwd):
        return None
    return _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)


def repo_name(cwd: Optional[Path] = None) -> Optional[str]:
    """Infer a project name from the git repo's top-level directory."""
    if not is_git_repo(cwd):
        return None
    top_level = _run_git(["rev-parse", "--show-toplevel"], cwd)
    if not top_level:
        return None
    return Path(top_level).name


def last_commit_summary(cwd: Optional[Path] = None) -> Optional[str]:
    if not is_git_repo(cwd):
        return None
    return _run_git(["log", "-1", "--pretty=%h %s"], cwd)

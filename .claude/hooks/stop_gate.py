#!/usr/bin/env python3
"""Stop hook: a loop builder cannot end its turn until `pr_gate.py` passes on its change.

This is the agent loop's check stage. It applies only to a loop builder (`LOOP_ROLE=builder`),
never to an interactive session or a reviewer, and only when the checkout differs from the
base. It runs the same command CI's required check runs, against the same base:

    <gate interpreter> scripts/ai/pr_gate.py --base ${LOOP_BASE:-origin/main}

Outcomes, kept apart on purpose, because a setup failure must never read as either a pass or
a code failure:
- gate exit 0: the stop is allowed.
- gate exit 1: the stop is blocked. The tail of the gate output and REVIEW.md's defect
  classes go back to the builder. After 5 blocked stops the builder may end anyway, so a
  person can look; the loop's own final gate run is the backstop.
- gate interpreter unusable, gate exit 2 (tool or usage error), or a timeout: blocked once
  with a message naming it as a setup problem, then allowed. These don't count toward the
  5-stop budget.

Each outcome adds one line to `checks.log` in the run folder (`$LOOP_RUN_DIR`, default
`<main checkout>/.loop`); each block's full message also goes to `blocked.log`.

Stdlib only, Python 3.9-safe. Exit 0 = allow the stop · exit 2 = block, reason on stderr.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

BUDGET = 5
GATE_TIMEOUT = 280  # under the 300 s hook timeout in settings.json, so this hook reports it


def git(cwd: Path, *args: str) -> Optional[str]:
    try:
        out = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                             timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout if out.returncode == 0 else None


def defect_classes(root: Path) -> str:
    try:
        review = (root / "REVIEW.md").read_text(encoding="utf-8")
    except OSError:
        return ""
    match = re.search(r"^## The defect classes.*?(?=^## )", review, re.S | re.M)
    return match.group(0).strip() if match else ""


def main() -> int:
    if os.environ.get("LOOP_ROLE") != "builder":
        return 0
    try:
        event = json.load(sys.stdin)
    except ValueError:
        event = {}
    start = Path(event.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    top = git(start, "rev-parse", "--show-toplevel")
    common = git(start, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if not top or not common:
        return 0
    root, main_root = Path(top.strip()), Path(common.strip()).parent
    if (main_root / ".loop" / "STOP").exists():
        return 0  # the kill switch wants the agent to stop, not to keep fixing

    run_dir = Path(os.environ.get("LOOP_RUN_DIR") or main_root / ".loop")
    run_dir.mkdir(parents=True, exist_ok=True)
    checks, blocked_log = run_dir / "checks.log", run_dir / "blocked.log"
    base = os.environ.get("LOOP_BASE") or "origin/main"

    def log(line: str) -> None:
        with checks.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def block(message: str) -> int:
        with blocked_log.open("a", encoding="utf-8") as fh:
            fh.write(message + "\n\n")
        print(message, file=sys.stderr)
        return 2

    def setup_block(reason: str) -> int:
        marker = run_dir / ".gate-setup-blocked"
        if marker.exists():
            return 0
        marker.touch()
        log(f"setup ({reason.splitlines()[0]})")
        return block(f"The gate could not run, so this is a setup problem, not a code failure: "
                     f"{reason}\nMake no more changes for it. Say in your answer that the gate "
                     f"did not run and why, then stop.")

    unchanged = git(root, "diff", "--quiet", base, "--") is not None
    if unchanged and not (git(root, "status", "--porcelain") or "").strip():
        return 0
    prior = checks.read_text(encoding="utf-8").splitlines() if checks.exists() else []
    if sum(1 for line in prior if line.startswith("blocked")) >= BUDGET:
        return 0

    sys.path.insert(0, str(root / "scripts" / "ai"))
    try:
        import gate_python  # noqa: PLC0415  (the checkout's own copy)
    except ImportError:
        return setup_block("scripts/ai/gate_python.py is missing from this checkout")
    python, problems = gate_python.problems(root)
    if problems:
        return setup_block("; ".join(problems) + ". See scripts/ai/gate_python.py")

    try:
        run = subprocess.run([str(python), "scripts/ai/pr_gate.py", "--base", base], cwd=root,
                             capture_output=True, text=True, timeout=GATE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return setup_block(f"pr_gate.py took longer than {GATE_TIMEOUT}s")
    output = run.stdout + run.stderr
    summary = next((line for line in reversed(output.splitlines())
                    if re.match(r"^\d+ checks:", line)), "no summary line")
    if run.returncode == 0:
        log(f"pass ({summary})")
        return 0
    if run.returncode != 1:
        return setup_block(f"pr_gate.py exited {run.returncode}: "
                           + "\n".join(output.strip().splitlines()[-5:]))
    log(f"blocked ({summary})")
    tail = "\n".join(output.rstrip().splitlines()[-40:])
    return block(f"pr_gate.py --base {base} failed, so this isn't done. Fix the cause, then "
                 f"finish again.\n\n{tail}\n\nDefect classes this repo produces (REVIEW.md):\n"
                 f"{defect_classes(root)}")


if __name__ == "__main__":
    sys.exit(main())

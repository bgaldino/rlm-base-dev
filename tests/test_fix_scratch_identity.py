#!/usr/bin/env python3
"""Unit tests for tasks.rlm_fix_scratch_identity.FixScratchOrgIdentity.

Self-contained — no pytest required (matches this repo's lightweight test
convention). Run from the repo root with base Python (CumulusCI is not needed;
the task module degrades to stdlib-only when CumulusCI is absent):

    python tests/test_fix_scratch_identity.py

Exits 0 when all checks pass, 1 otherwise. Covers every branch of the repair
logic: the isScratch flip/no-op decisions, secret + permission handling, the
raise-on-unreadable behavior, and the _run_task summary (clean / repaired /
errors / partial).
"""
import json
import logging
import os
import pathlib
import sys
import tempfile
from types import SimpleNamespace

# Make `tasks` importable regardless of cwd.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from tasks.rlm_fix_scratch_identity import (  # noqa: E402
    FixScratchOrgIdentity,
    TaskOptionsError,
)

RESULTS = []


def check(name, condition):
    RESULTS.append((name, bool(condition)))
    print(f"  [{'PASS' if condition else 'FAIL'}] {name}")


class CapturingHandler(logging.Handler):
    """Collects emitted log messages for summary assertions."""

    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def make_task(options=None, org_config=None):
    """Build a task instance without running CumulusCI's BaseTask.__init__."""
    task = FixScratchOrgIdentity.__new__(FixScratchOrgIdentity)
    handler = CapturingHandler()
    logger = logging.getLogger(f"test.{id(task)}")
    logger.handlers = [handler]
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    task.logger = logger
    task.options = options or {}
    task.org_config = org_config
    task._captured = handler.messages
    return task


def write_auth(directory, data, mode=0o600, name="u.json"):
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    os.chmod(path, mode)
    return pathlib.Path(path)


# ----------------------------------------------------------------------
# _repair_file: flip / no-op decisions
# ----------------------------------------------------------------------

def test_repair_decisions():
    task = make_task()
    cases = {
        "broken EE scratch flips": (
            {"isScratch": False, "devHubUsername": "dh", "accessToken": "SECRET"}, True),
        "missing isScratch flips": (
            {"devHubUsername": "dh"}, True),
        "already true is no-op": (
            {"isScratch": True, "devHubUsername": "dh"}, False),
        "no devHubUsername left alone": (
            {"isScratch": False}, False),
        "devhub left alone": (
            {"isScratch": False, "devHubUsername": "dh", "isDevHub": True}, False),
        "sandbox left alone": (
            {"isScratch": False, "devHubUsername": "dh", "isSandbox": True}, False),
    }
    for name, (data, expect_change) in cases.items():
        with tempfile.TemporaryDirectory() as d:
            path = write_auth(d, dict(data))
            changed = task._repair_file(path)
            after = json.loads(path.read_text())
            ok = changed == expect_change
            if expect_change:
                ok = ok and after.get("isScratch") is True
            else:
                ok = ok and after.get("isScratch") == data.get("isScratch")
            # secrets must never be dropped
            ok = ok and after.get("accessToken") == data.get("accessToken")
            check(name, ok)


# ----------------------------------------------------------------------
# _repair_file: raises on unreadable / non-JSON / non-object
# ----------------------------------------------------------------------

def test_repair_raises_on_bad_files():
    task = make_task()
    bad = {
        "non-JSON raises": "not json at all",
        "non-object raises": "[1, 2, 3]",
        "undecodable raises": "\udcff",  # not valid UTF-8 when written below
    }
    for name, content in bad.items():
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "u.json")
            with open(path, "wb") as fh:
                fh.write(content.encode("utf-8", errors="surrogateescape"))
            try:
                task._repair_file(pathlib.Path(path))
                check(name, False)
            except RuntimeError:
                check(name, True)


# ----------------------------------------------------------------------
# _atomic_write: permissions forced to 0600
# ----------------------------------------------------------------------

def test_permissions_forced_0600():
    task = make_task()
    for in_mode in (0o700, 0o644, 0o600, 0o666):
        with tempfile.TemporaryDirectory() as d:
            path = write_auth(d, {"isScratch": False, "devHubUsername": "dh"}, mode=in_mode)
            task._repair_file(path)
            final = oct(os.stat(path).st_mode & 0o777)
            check(f"{oct(in_mode)} -> {final} (expect 0o600)", final == "0o600")


# ----------------------------------------------------------------------
# _find_auth_files: locates ~/.sfdx/<username>.json
# ----------------------------------------------------------------------

def test_find_auth_files():
    task = make_task()
    original_home = os.environ.get("HOME")
    with tempfile.TemporaryDirectory() as home:
        os.environ["HOME"] = home
        try:
            sfdx = os.path.join(home, ".sfdx")
            os.makedirs(sfdx)
            target = write_auth(sfdx, {"isScratch": True}, name="alice@example.com.json")
            found = task._find_auth_files("alice@example.com")
            check("finds ~/.sfdx/<user>.json", [str(p) for p in found] == [str(target)])
            check("missing user -> empty", task._find_auth_files("nobody@example.com") == [])
        finally:
            if original_home is not None:
                os.environ["HOME"] = original_home
            else:
                os.environ.pop("HOME", None)


# ----------------------------------------------------------------------
# _run_task: summary branches
# ----------------------------------------------------------------------

def _run_with_files(files, options=None):
    task = make_task(options=options, org_config=SimpleNamespace(scratch=True, username="u"))
    task._find_auth_files = lambda username: files
    task._run_task()
    return task._captured


def test_run_summary_branches():
    # all clean -> "already correct"
    with tempfile.TemporaryDirectory() as d:
        good = write_auth(d, {"isScratch": True, "devHubUsername": "dh"})
        msgs = _run_with_files([good])
        check("summary: already correct", any("already correct" in m for m in msgs))

    # patched only -> "repaired"
    with tempfile.TemporaryDirectory() as d:
        broken = write_auth(d, {"isScratch": False, "devHubUsername": "dh"})
        msgs = _run_with_files([broken])
        check("summary: repaired", any("identity repaired" in m for m in msgs))

    # errors only -> "NOT verified"
    with tempfile.TemporaryDirectory() as d:
        bad = pathlib.Path(os.path.join(d, "bad.json"))
        bad.write_text("not json")
        msgs = _run_with_files([bad])
        check("summary: NOT verified", any("NOT verified" in m for m in msgs))

    # patched + errors -> "PARTIALLY repaired"
    with tempfile.TemporaryDirectory() as d:
        good = write_auth(d, {"isScratch": False, "devHubUsername": "dh"}, name="g.json")
        bad = pathlib.Path(os.path.join(d, "b.json"))
        bad.write_text("not json")
        msgs = _run_with_files([good, bad])
        check("summary: partial", any("PARTIALLY repaired" in m for m in msgs))


def test_run_gating_and_failure_modes():
    # non-scratch org -> skip
    task = make_task(org_config=SimpleNamespace(scratch=False, username="u"))
    task._run_task()
    check("non-scratch org skipped", any("skipping" in m for m in task._captured))

    # raise_on_failure raises when a file can't be parsed
    with tempfile.TemporaryDirectory() as d:
        bad = pathlib.Path(os.path.join(d, "bad.json"))
        bad.write_text("not json")
        task = make_task(
            options={"raise_on_failure": True},
            org_config=SimpleNamespace(scratch=True, username="u"),
        )
        task._find_auth_files = lambda username: [bad]
        try:
            task._run_task()
            check("raise_on_failure raises", False)
            check("raise_on_failure chains cause", False)
        except TaskOptionsError as exc:
            check("raise_on_failure raises", True)
            # The originating error must be chained (raise ... from exc).
            check("raise_on_failure chains cause", exc.__cause__ is not None)


def test_dedicated_exception_type():
    # The CumulusCI-absent fallback must be a distinct type, not bare Exception,
    # so `except TaskOptionsError` catches only intended failures.
    check("TaskOptionsError is not bare Exception", TaskOptionsError is not Exception)
    check("TaskOptionsError subclasses Exception", issubclass(TaskOptionsError, Exception))


def test_atomic_write_cleanup_on_chmod_failure():
    # If os.fchmod raises before os.fdopen takes ownership of the descriptor,
    # _atomic_write must still re-raise and leave no stray temp file behind.
    if not hasattr(os, "fchmod"):
        check("atomic_write cleanup on fchmod failure (skipped: no fchmod)", True)
        return
    original_fchmod = os.fchmod

    def boom(*args, **kwargs):
        raise OSError("simulated fchmod failure")

    with tempfile.TemporaryDirectory() as d:
        path = write_auth(d, {"isScratch": False, "devHubUsername": "dh"})
        os.fchmod = boom
        try:
            raised = False
            try:
                FixScratchOrgIdentity._atomic_write(path, {"isScratch": True})
            except OSError:
                raised = True
            leftover = [f for f in os.listdir(d) if f.startswith(".rlm_auth_")]
            check("atomic_write re-raises on fchmod failure", raised)
            check("atomic_write leaves no temp file", leftover == [])
        finally:
            os.fchmod = original_fchmod


def test_atomic_write_without_fchmod():
    # Simulate a platform without os.fchmod (e.g. Windows): the os.chmod path
    # must still restrict perms to 0600 (before writing) and write correctly.
    task = make_task()
    had_fchmod = hasattr(os, "fchmod")
    saved = os.fchmod if had_fchmod else None
    if had_fchmod:
        delattr(os, "fchmod")
    try:
        with tempfile.TemporaryDirectory() as d:
            path = write_auth(d, {"isScratch": False, "devHubUsername": "dh"}, mode=0o644)
            task._repair_file(path)
            final = oct(os.stat(path).st_mode & 0o777)
            data = json.loads(path.read_text())
            check("no-fchmod path -> 0o600", final == "0o600")
            check("no-fchmod path writes isScratch=true", data.get("isScratch") is True)
    finally:
        if had_fchmod:
            os.fchmod = saved


def main():
    test_repair_decisions()
    test_repair_raises_on_bad_files()
    test_permissions_forced_0600()
    test_find_auth_files()
    test_run_summary_branches()
    test_run_gating_and_failure_modes()
    test_dedicated_exception_type()
    test_atomic_write_cleanup_on_chmod_failure()
    test_atomic_write_without_fchmod()

    passed = sum(1 for _, ok in RESULTS if ok)
    total = len(RESULTS)
    print(f"\n{passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

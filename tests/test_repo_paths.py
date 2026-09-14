#!/usr/bin/env python3
"""Direct unit tests for the shared git-tracking helpers and the diff_schemas
object-name parsing fix consolidated by todo pack 167.

`scripts/repo_paths.py` is the one copy of "which of these candidate paths does
git track?", previously duplicated in `check_plan_readme_consistency.py` and
`scripts/erd/schema_diff/diff_schemas.py`. `tests/test_check_plan_readme_discovery.py`
exercises it through the README gate's thin wrappers; this suite pins the module
directly (so a regression is attributable to the module, not a caller) and pins
the two behaviors pack 167 CHANGED in `diff_schemas.py`:

  1. `_extract_object_name` now delegates query parsing to the subquery-aware,
     case-insensitive `sfdmu_export.extract_object_name`. The old inline
     `query.split("FROM ")[1]` misread a SELECT-clause subquery's inner `FROM`
     and could not match a lowercase `from` — both fixed, both pinned below.
  2. `_list_tracked_export_jsons` now calls `repo_paths.tracked_paths` but keeps
     its softer failure mode (return None on git failure, don't raise).

Builds a hermetic git repo in a tempdir (same pattern as
test_check_plan_readme_discovery.py), never touching this checkout's git state.

Run: `python tests/test_repo_paths.py` (offline, no org; spawns git in a
throwaway tempdir, no network).
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import repo_paths as rp  # noqa: E402

GIT_ENV = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
GIT_ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
               GIT_CONFIG_NOSYSTEM="1")

_failures: list[str] = []


def check(label: str, ok: bool) -> None:
    if not ok:
        _failures.append(label)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")


def git(cwd, *args):
    proc = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                          text=True, env=GIT_ENV)
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {cwd}:\n{proc.stderr}")
    return proc.stdout.strip()


def _load_diff_schemas():
    path = REPO / "scripts" / "erd" / "schema_diff" / "diff_schemas.py"
    spec = importlib.util.spec_from_file_location("diff_schemas_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- repo_paths.repo_relpath -------------------------------------------------
print("=" * 100)
print("-- repo_paths.repo_relpath")
with tempfile.TemporaryDirectory() as td:
    root = os.path.realpath(td)
    inside = os.path.join(root, "datasets", "sfdmu", "x", "export.json")
    check("a path under repo_root becomes a clean relative path",
          rp.repo_relpath(inside, root) == "datasets/sfdmu/x/export.json")
    check("repo_root itself maps to '.'",
          rp.repo_relpath(root, root) == ".")
    # Case-only-differing prefix is treated as the same dir (macOS APFS), NOT a
    # '../'-prefixed escape that would later make git ls-files exit 128.
    check("a case-only-differing repo_root prefix is the SAME dir (no '..' escape)",
          rp.repo_relpath(root.upper() + "/datasets/x", root) == "datasets/x")
    # A genuinely outside path still yields a '..'-prefixed relpath (the guard the
    # README gate keys on to skip cleanly).
    outside = os.path.join(os.path.dirname(root), "sibling", "export.json")
    check("a genuinely outside path still yields a '..'-prefixed relpath",
          rp.repo_relpath(outside, root).startswith(".."))


# --- repo_paths.tracked_paths ------------------------------------------------
print("-- repo_paths.tracked_paths")
with tempfile.TemporaryDirectory() as td:
    root = os.path.realpath(td)
    tracked_dir = pathlib.Path(root) / "datasets" / "sfdmu" / "kept"
    tracked_dir.mkdir(parents=True)
    tracked_json = tracked_dir / "export.json"
    tracked_json.write_text(json.dumps({"objectSets": []}))

    scratch_dir = pathlib.Path(root) / "datasets" / "sfdmu" / "scratch"
    scratch_dir.mkdir(parents=True)
    scratch_json = scratch_dir / "export.json"
    scratch_json.write_text(json.dumps({"objectSets": []}))

    (pathlib.Path(root) / ".gitignore").write_text("datasets/sfdmu/scratch/**\n")
    git(root, "init", "--quiet", "-b", "base")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "test")
    git(root, "config", "commit.gpgsign", "false")
    git(root, "config", "core.hooksPath", os.devnull)
    git(root, "add", ".gitignore", "datasets/sfdmu/kept/export.json")
    git(root, "commit", "--quiet", "-m", "seed")

    got = rp.tracked_paths([str(tracked_json), str(scratch_json)], root)
    check("a git-tracked candidate is returned",
          str(tracked_json) in got)
    check("a gitignored candidate is filtered out",
          str(scratch_json) not in got)
    check("returns the CALLER's own path strings (not git's reconstruction)",
          got == {str(tracked_json)})
    check("empty input short-circuits to empty set (no git call)",
          rp.tracked_paths([], root) == set())

# check=True hard-fails outside a checkout — a gate must not read empty stdout as
# "nothing tracked". The README gate lets this propagate; diff_schemas wraps it.
print("-- repo_paths.tracked_paths raises outside a git checkout (check=True)")
with tempfile.TemporaryDirectory() as td:
    root = os.path.realpath(td)
    cand = os.path.join(root, "export.json")
    open(cand, "w").close()
    raised = False
    try:
        rp.tracked_paths([cand], root)
    except subprocess.CalledProcessError:
        raised = True
    check("git failure raises rather than returning empty (silent pass-by-absence)",
          raised)


# --- diff_schemas._extract_object_name (pack 167 parsing fix) ----------------
print("-- diff_schemas._extract_object_name delegates to the subquery-aware parser")
ds = _load_diff_schemas()
check("explicit objectName wins over query",
      ds._extract_object_name({"objectName": "Account", "query": "SELECT Id FROM Contact"}) == "Account")
check("simple query is parsed",
      ds._extract_object_name({"query": "SELECT Id, Name FROM Product2"}) == "Product2")
# The old split("FROM ") read the subquery's inner FROM; the shared parser strips
# parenthesized groups first and returns the OUTER object.
check("SELECT-clause subquery's inner FROM is NOT mistaken for the object",
      ds._extract_object_name(
          {"query": "SELECT Id, (SELECT Id FROM Contacts) FROM Account"}) == "Account")
# The old `if "FROM " in query` was case-sensitive; the shared parser matches
# the FROM keyword case-insensitively.
check("a lowercase 'from' keyword is matched",
      ds._extract_object_name({"query": "select id from Asset"}) == "Asset")
check("no objectName and no parseable query yields ''",
      ds._extract_object_name({}) == "")


print("=" * 100)
if _failures:
    for label in _failures:
        print(f"FAILED: {label}")
    print(f"\n{'-' * 20}\n{len(_failures)} FAILED")
    sys.exit(1)
print("All checks passed")
sys.exit(0)

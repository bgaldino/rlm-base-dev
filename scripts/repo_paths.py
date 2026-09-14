"""Shared "is this path git-tracked?" helpers.

One implementation of the question "which of these candidate paths does git
track?", used by both the SFDMU plan-README gate
(`scripts/ai/check_plan_readme_consistency.py`) and the ERD schema-diff impact
report (`scripts/erd/schema_diff/diff_schemas.py`). Both need it for the same
reason: a report/gate that should reflect a *fresh clone* must exclude
gitignored local/scratch plan dirs (`datasets/sfdmu/extractions/`,
`.../reconcile/`, `test/qb-dro.bak/`, …) that happen to carry an `export.json`.

Todo pack 167 consolidated the two copies here. `repo_root` is an explicit
parameter (not a module global) so callers keep their own root — and so the
README gate's tests, which monkeypatch that script's `REPO_ROOT` to a temp git
repo, still redirect this helper.

Deliberately NOT merged with `bump_api_version.py`'s `tracked_files()` (a
cached, whole-repo, repo-relative frozenset): that answers a different question
(a full-repo inventory, not "which of THESE few candidates are tracked") — the
same "unrelated concern domains / not worth the coupling" reasoning the README
gate already applied to it. Kept out of the pure-parsing `sfdmu_export.py` on
purpose too: that module is dependency-free (`re` only); this one shells out to
git.

Failure mode is the CALLER's to choose, at the call site: `tracked_paths` lets a
git failure raise (`check=True`, uncaught). The README gate lets it propagate —
a gate must never silently look like "nothing tracked". `diff_schemas.py` wraps
the call and degrades to an `rglob` walk + warning, because an impact report is
analysis, not a merge gate. Same helper, two policies, each explicit.
"""
from __future__ import annotations

import os
import subprocess


def repo_relpath(p: str, repo_root: str) -> str:
    """Like `os.path.relpath(p, repo_root)`, but treats a `repo_root` prefix that
    differs from `p` only in case as the SAME directory — so a path admitted as
    "inside the repo" on a case-insensitive filesystem (macOS APFS) does not turn
    into a bogus, deeply-'../'-prefixed relpath that then makes `git ls-files`
    exit 128 ("outside repository") and, via `tracked_paths`' `check=True`, crash
    instead of cleanly reporting bad input (round 15 of PR #406's review, pack
    147: live-reproduced)."""
    p = os.fspath(p)
    repo_root = os.fspath(repo_root)
    root_len = len(repo_root)
    if p[:root_len].lower() == repo_root.lower() and p[root_len:root_len + 1] in ("", os.sep):
        return p[root_len:].lstrip(os.sep) or "."
    return os.path.relpath(p, repo_root)


def tracked_paths(paths: list[str], repo_root: str) -> set[str]:
    """Absolute paths of `paths` that git tracks under `repo_root` — one batched
    `git ls-files` call for all candidates, instead of one
    `git ls-files --error-unmatch` subprocess per candidate (~30+ processes on
    this repo's tree). Returns which of the GIVEN candidates are tracked, not a
    full-repo inventory.

    check=True: a git failure (e.g. run outside a checkout) must not silently
    yield empty stdout, which a gate would misread as "nothing tracked" and
    pass-by-absence. Callers that prefer to degrade rather than crash wrap this
    and catch `CalledProcessError`/`FileNotFoundError` themselves.

    -z: git's default core.quotepath=true C-quotes/octal-escapes non-ASCII bytes
    in plain `ls-files` output (a tracked `café/export.json` echoes as
    `caf\\303\\251/export.json`), which would never match the relpath below and
    misclassify a genuinely tracked path as untracked. -z disables quoting and
    NUL-delimits instead.

    Compares as BYTES (no `text=`): `-z` makes git emit raw filename bytes, so
    decoding them with `text=True` under the process locale would raise
    `UnicodeDecodeError` on a path with non-decodable bytes — an exception NEITHER
    caller expects (the README gate would crash; `diff_schemas`' soft-failure
    wrapper only catches `CalledProcessError`/`FileNotFoundError`, so the intended
    rglob fallback is bypassed). We keep git's output as bytes and `os.fsencode`
    each candidate relpath to compare, which round-trips any byte sequence and
    can't raise. (`repo_relpath` -> `os.path.relpath` already tolerates such names
    on input.)

    Matches EXACT-case, and returns the CALLER's own path (not git's stdout
    string) for each match. Case-folding the comparison — which this helper's
    ancestor did — is wrong: on case-sensitive Linux (where CI runs) `foo/` and
    `FOO/` are distinct directories, so folding would report an untracked local
    `FOO/export.json` as tracked whenever a real `foo/export.json` is, a false
    positive that misclassifies a scratch dir as a shipped plan. It also bought
    nothing on macOS: `git ls-files` does NOT match a mis-cased pathspec there
    (verified — a query for `FOO/export.json` against a tracked `foo/export.json`
    returns empty, not the index casing), so there is no folded match for the
    fold to recover. This is the same "never fold a path identity that maps to a
    real file git/SFDMU read exact-case" lesson as todo pack 163."""
    if not paths:
        return set()
    paths = [os.fspath(p) for p in paths]
    # Normalize to forward slashes: `repo_relpath` -> `os.path.relpath` emits the
    # platform separator (`\` on Windows), but `git ls-files` always prints index
    # paths with `/`. Comparing the two directly would never match on Windows and
    # silently drop every tracked candidate (a gate then reads "nothing tracked").
    # git accepts `/` in a pathspec on all platforms, so we normalize once and use
    # the result for both the query and the comparison. Replacing `\`->`/`
    # unconditionally (not via `os.sep`) is a no-op on POSIX for the repo-relative
    # `export.json` paths this helper is given — none contain a literal backslash —
    # and, unlike `os.sep`, is exercised by the tests regardless of host platform.
    rels = [repo_relpath(p, repo_root).replace("\\", "/") for p in paths]
    r = subprocess.run(["git", "ls-files", "-z", "--"] + rels, cwd=repo_root,
                        capture_output=True, check=True)
    tracked = {chunk for chunk in r.stdout.split(b"\0") if chunk}
    return {p for p, rel in zip(paths, rels) if os.fsencode(rel) in tracked}

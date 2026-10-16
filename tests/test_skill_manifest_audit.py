#!/usr/bin/env python
"""Offline checks for the local-only path handling in `skill_manifest.py --check`.

The audit's claim is that every path-shaped value in the Foundations section resolves in
the working tree. `.agents/artifacts/` breaks that claim by design: it is a separate
PRIVATE repo, gitignored by the main one, and the analysis-artifacts rule requires
generated working documents to live there — so tracked files legitimately cite paths
inside it. The audit demanded those paths resolve, which made `--check` fail on every
fresh clone and in CI while passing on the one workstation holding the clone. Found by
review on PR #383, when the gate proposed to make `skill_manifest.py --check` gating.

The fix must hold two properties at once, and only the pair is correct:

  1. Absent private tree  -> the reference is REPORTED as unaudited, and the run passes.
     A silent skip would be the unfalsifiable check this module's own docstrings warn
     about; a failure would break CI for a path CI cannot have.
  2. Present private tree -> the reference is audited normally, so a typo still fails.
     Downgrading it everywhere would have traded a false failure for a blind spot.

Run: python tests/test_skill_manifest_audit.py   (needs PyYAML; no org, no network)
"""

import io
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                "scripts", "ai"))

import skill_manifest  # noqa: E402

PASSED = 0
FAILED = []


def check(label, condition, detail=""):
    global PASSED
    if condition:
        PASSED += 1
        print(f"  [PASS] {label}")
    else:
        FAILED.append(label)
        print(f"  [FAIL] {label}" + (f"\n         {detail}" if detail else ""))


class _Resolved:
    """Stands in for RepoLocation: the audit reads only `.path`."""

    def __init__(self, path):
        self.path = path


def audit(root, cited, *, create_private):
    """Run the audit over a throwaway tree citing one local-only path."""
    tracked = Path(root, "docs", "real.md")
    tracked.parent.mkdir(parents=True, exist_ok=True)
    tracked.write_text("tracked\n")
    if create_private:
        target = Path(root, cited)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("private\n")
    section = {
        "_resolved": _Resolved(root),
        # A real path alongside the local-only one, so a pass cannot come from an
        # empty walk.
        "grounding": {"tracked": "docs/real.md", "private": cited},
        "skills": [],
    }
    buf = io.StringIO()
    with redirect_stdout(buf):
        ok = skill_manifest._audit_foundations({"foundations": section})
    return ok, buf.getvalue()


CITED = ".agents/artifacts/integration-staging/pmos-integration.md"

print(__doc__.splitlines()[0])
print("=" * 100)

with TemporaryDirectory() as root:
    ok, out = audit(root, CITED, create_private=False)
    check("an absent private tree does not fail the audit", ok is True, out)
    check("the unaudited reference is named, not swallowed", CITED in out, out)
    check("the reason is given as absence, not drift",
          "not audited" in out and "absent" in out, out)
    check("the summary stops claiming that ALL paths resolve",
          "all auditable paths resolve" in out, out)
    check("a real path in the same walk is still resolved", "[OK" in out, out)

with TemporaryDirectory() as root:
    ok, out = audit(root, CITED, create_private=True)
    check("a present private tree is audited, and a correct path passes", ok is True, out)
    check("nothing is reported as unaudited when the tree is there",
          "not audited" not in out, out)
    check("the summary reverts to the unqualified claim",
          "all paths resolve" in out and "auditable" not in out, out)

with TemporaryDirectory() as root:
    # The discriminating case: the tree exists but the cited file inside it does not.
    Path(root, ".agents", "artifacts").mkdir(parents=True)
    ok, out = audit(root, CITED, create_private=False)
    check("a typo inside a PRESENT private tree still fails", ok is False, out)
    check("the failure names the missing path", CITED in out, out)
    check("it is reported as a problem, not as unaudited",
          "[ERROR]" in out and "not audited" not in out, out)

with TemporaryDirectory() as root:
    # A path merely *resembling* the private prefix must not inherit the exemption.
    lookalike = ".agents/artifacts-notes/decoy.md"
    Path(root, ".agents", "artifacts").mkdir(parents=True)
    ok, out = audit(root, lookalike, create_private=False)
    check("a sibling directory with a similar name is not exempt", ok is False, out)

check("the exempt prefix is anchored with a separator",
      skill_manifest.LOCAL_ONLY_PREFIXES == (".agents/artifacts/",),
      skill_manifest.LOCAL_ONLY_PREFIXES)

print("\n" + "=" * 100)
if FAILED:
    print(f"{len(FAILED)} FAILED: {', '.join(FAILED)}")
    sys.exit(1)
EXPECTED = 13
if PASSED != EXPECTED:
    print(f"{PASSED} checks passed but {EXPECTED} were expected — update EXPECTED "
          "deliberately when adding or removing a check")
    sys.exit(1)
print(f"{PASSED}/{EXPECTED} checks passed")

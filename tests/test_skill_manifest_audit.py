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

The second half covers clone discovery, which decides WHICH tree the audit reads. From a
git worktree whose origin used an SSH host alias (`git@github.com-<alias>:owner/repo`),
`--check` failed: no hint named the worktree, so the sibling hint found the main checkout,
and the alias host made its remote compare as a provably different repo (issue #593).
Fixing only the comparison would have been worse than the failure — the audit would then
pass against the main checkout, another branch. So the pair again:

  3. The repo containing the manifest wins its own section, ahead of every hint, and the
     self test cannot take a Foundations checkout for PMOS (it has both skill surfaces).
  4. An alias host with the same owner/repo is unverifiable, not rejected — while a
     different owner/repo is still rejected, which is what the rejection exists for.

Run: python tests/test_skill_manifest_audit.py   (needs PyYAML and git; no org, no network)
"""

import io
import os
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                "scripts", "ai"))

import skill_manifest  # noqa: E402

# Run as if outside any git hook, as tests/test_pr_gate.py does: an exported GIT_DIR would
# aim the throwaway clones' `git init`/`remote add`, and every remote the resolver reads, at
# this repository instead.
for _var in [v for v in os.environ
             if v in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                      "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_PREFIX",
                      "GIT_NAMESPACE", "GIT_CONFIG", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT")
             or v.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))]:
    os.environ.pop(_var)

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

# ─── Clone discovery ─────────────────────────────────────────────────────────

URL = "https://github.com/bgaldino/rlm-base-dev"
ALIAS = "git@github.com-work:bgaldino/rlm-base-dev.git"
FOREIGN = "git@github.com:someone-else/rlm-base-dev.git"

check("an SSH-alias host with the same owner/repo cannot be compared, not a mismatch",
      skill_manifest._urls_equivalent(ALIAS, URL) is None,
      skill_manifest._urls_equivalent(ALIAS, URL))
check("a different owner/repo is still a provable mismatch",
      skill_manifest._urls_equivalent(FOREIGN, URL) is False,
      skill_manifest._urls_equivalent(FOREIGN, URL))
check("the same host and owner/repo still match",
      skill_manifest._urls_equivalent("git@github.com:bgaldino/rlm-base-dev.git", URL) is True)
check("the ssh:// form of an alias is unverifiable too",
      skill_manifest._urls_equivalent("ssh://git@github.com-work/bgaldino/rlm-base-dev.git", URL)
      is None)
# An https host is never an SSH alias, so another forge with the same owner/repo — a mirror,
# or an unrelated repo that happens to share the name — is still a mismatch.
check("two https hosts with the same owner/repo are still a mismatch",
      skill_manifest._urls_equivalent("https://git.example.com/bgaldino/rlm-base-dev", URL)
      is False)
check("an ssh:// alias with a user other than git is unverifiable too",
      skill_manifest._urls_equivalent("ssh://alice@github.com-work/bgaldino/rlm-base-dev", URL)
      is None)
check("https userinfo names an account, not a different host",
      skill_manifest._urls_equivalent("https://someone@github.com/bgaldino/rlm-base-dev", URL)
      is True)


def clone(parent, name, *, remote, surfaces):
    """A directory shaped like a checkout: the manifest, skill surfaces, an origin remote."""
    root = Path(parent, name)
    Path(root, ".claude").mkdir(parents=True)
    Path(root, skill_manifest.MANIFEST_FILENAME).write_text("manifest_version: 2\n")
    for surface in surfaces:
        Path(root, surface).mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "remote", "add", "origin", remote], check=True)
    return root.resolve()


def section(name, url, hints, marker):
    return {"name": name, "role": "test", "repo_url": url,
            "local_path_hints": hints, "clone_markers": [marker]}


FOUNDATIONS_SURFACES = (".cursor/skills", ".claude/skills")
FOUNDATIONS = section("rlm-base-dev", URL, ["../rlm-base-dev"], ".cursor/skills")
PMOS_URL = "https://git.example.com/bgaldino/pmos-revenue-cloud"

with TemporaryDirectory() as parent:
    main = clone(parent, "rlm-base-dev", remote=ALIAS, surfaces=FOUNDATIONS_SURFACES)
    wt = clone(parent, "rlm-base-dev-wt", remote=ALIAS, surfaces=FOUNDATIONS_SURFACES)
    found = skill_manifest._discover_repo(FOUNDATIONS, manifest_root=wt)
    check("a worktree resolves its own section to itself, not the sibling checkout",
          found.path == wt, found.path)
    check("and is verified as self rather than by remote",
          found.identity == "verified-self", found.identity)

    # An env-var hint (here: absolute, listed first) naming the main checkout still loses.
    found = skill_manifest._discover_repo(
        section("rlm-base-dev", URL, [str(main), "../rlm-base-dev"], ".cursor/skills"),
        manifest_root=wt)
    check("self wins its section ahead of an earlier absolute hint",
          found.path == wt, found.path)

    found = skill_manifest._discover_repo(FOUNDATIONS, manifest_root=main)
    check("the main checkout still resolves to itself", found.path == main, found.path)
    check("a hint naming self is not tried twice",
          [p.resolve() for p in found.candidates_tried].count(main) == 1,
          found.candidates_tried)

    # From a repo that is NOT this section (the PMOS side finding Foundations), an alias
    # remote on the hinted clone is accepted as unverified instead of rejected...
    pmos = clone(parent, "pmos-revenue-cloud", remote=PMOS_URL, surfaces=(".claude/skills",))
    found = skill_manifest._discover_repo(FOUNDATIONS, manifest_root=pmos)
    check("an alias-remote clone found by hint is accepted, not rejected",
          found.path == main and found.identity == "unverified" and not found.rejected,
          (found.path, found.identity, found.rejected))

    # ...but a clone of a different owner/repo at the same hint is still rejected.
    stale = clone(parent, "stale", remote=FOREIGN, surfaces=FOUNDATIONS_SURFACES)
    found = skill_manifest._discover_repo(
        section("rlm-base-dev", URL, ["../stale"], ".cursor/skills"), manifest_root=pmos)
    check("a foreign owner/repo at a hint path is still rejected",
          found.path is None and [p for p, _ in found.rejected] == [stale],
          (found.path, found.rejected))

    # A Foundations checkout also has .claude/skills, PMOS's surface. Taken as self for
    # the PMOS section, every Foundations checkout would answer for PMOS. Its remote is a
    # local mirror, which cannot be compared, so only the surface test can say no.
    mirrored = clone(parent, "rlm-base-dev-mirrored", remote=str(Path(parent, "mirror")),
                     surfaces=FOUNDATIONS_SURFACES)
    found = skill_manifest._discover_repo(
        section("pmos-revenue-cloud", PMOS_URL, [], ".claude/skills"), manifest_root=mirrored)
    check("a Foundations checkout is not taken for PMOS as self",
          found.identity != "verified-self", (found.path, found.identity))

    # CONTRIBUTING.md has contributors clone their fork: another owner, the same repo.
    fork = clone(parent, "rlm-base-dev-fork", remote="https://github.com/alice/rlm-base-dev",
                 surfaces=FOUNDATIONS_SURFACES)
    found = skill_manifest._discover_repo(FOUNDATIONS, manifest_root=fork)
    check("a contributor's fork resolves its own section to itself",
          found.path == fork and found.identity == "verified-self" and not found.rejected,
          (found.path, found.identity, found.rejected))

    # The surface test is structural. Were PMOS to grow .cursor/skills, it would pass for
    # Foundations; its remote is what still says otherwise.
    grown = clone(parent, "pmos-grown", remote=PMOS_URL, surfaces=FOUNDATIONS_SURFACES)
    found = skill_manifest._discover_repo(
        section("rlm-base-dev", URL, [], ".cursor/skills"), manifest_root=grown)
    check("a self root whose remote names another repo is rejected, not verified-self",
          found.path is None and [p for p, _ in found.rejected] == [grown],
          (found.path, found.identity, found.rejected))

print("\n" + "=" * 100)
if FAILED:
    print(f"{len(FAILED)} FAILED: {', '.join(FAILED)}")
    sys.exit(1)
EXPECTED = 30
if PASSED != EXPECTED:
    print(f"{PASSED} checks passed but {EXPECTED} were expected — update EXPECTED "
          "deliberately when adding or removing a check")
    sys.exit(1)
print(f"{PASSED}/{EXPECTED} checks passed")

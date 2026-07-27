#!/usr/bin/env python
"""One command that must pass before a push. Todo 080, Deliverable 1.

WHY THIS EXISTS. PR #317 took nine Copilot rounds, and rounds 4-9 were almost
entirely unswept instances of classes already found in rounds 1-3 - several of
them earlier fixes left half delivered. Every one of those rounds was a credit
spent on a defect that was knowable locally. The tooling to prevent it already
existed and simply was not run, which is why making it "required" in prose does
not hold: AGENTS.md is read every session and the skills were still skipped. It
has to be a gate that FAILS.

    python scripts/ai/pre_push_audit.py                # audit this branch
    python scripts/ai/pre_push_audit.py --pr 317       # also require 0 unresolved threads
    python scripts/ai/pre_push_audit.py --since main   # explicit diff base
    python scripts/ai/pre_push_audit.py --list         # what would run, and why

FIVE TIERS
  A  compose the pass/fail gates that already exist - shell out, never reimplement
  B  the AGENTS.md DO NOT list                  ) declared in gate_rules.yml
  C  the .cursor/rules/*.mdc rules              )
  D  the doc-consistency change-surface map     )
  E  the defect-class registry (defect_classes.yml via defect_scan.py)

THREE RULES INHERITED FROM THE TODO PACK, each because it was violated before:

  * A SKIP MUST NEVER READ AS A PASS. Every check reports pass / fail /
    unavailable / not-applicable. "Unavailable" - could not execute - exits 2,
    which is louder than a failure, because an unknown result is worse than a
    known bad one. `test_docgen_helpers.py` exits 1 purely because pytest is not
    installed; an exit code alone cannot tell that apart from a real failure, so
    this script reads stderr and classifies it.
  * SCOPE IS NEVER SILENTLY TRUNCATED. If a check is bounded (changed files
    only, a pinned baseline), it says so in its own output line.
  * REVIEW PROMPTS CANNOT BE IGNORED. A rule that is not greppable without
    flooding false positives is still enforced - it blocks until acknowledged
    with --ack <id>. It never silently passes.

EXIT CODES
    0  everything that was in scope executed and passed
    1  at least one check failed
    2  at least one check could not execute, or a review prompt is unacknowledged
"""

import argparse
import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _gate_interpreter import ensure_pyyaml  # noqa: E402

ensure_pyyaml(__file__)
import yaml  # noqa: E402

RULES_FILE = REPO_ROOT / "scripts" / "ai" / "gate_rules.yml"

# validate_sfdmu_v5_datasets.py exits 1 on a CLEAN tree: two plans fail by
# design. Pinning the failing plans BY NAME rather than by count is deliberate -
# a count baseline silently absorbs "one fixed, one newly broken".
SFDMU_BASELINE_FAILURES = {"mfg/en-US/mfg-multicurrency", "procedure-plans"}

PASS, FAIL, UNAVAILABLE, NA, PROMPT = "PASS", "FAIL", "UNAVAILABLE", "n/a", "PROMPT"

_ICON = {PASS: "  ok    ", FAIL: "  FAIL  ", UNAVAILABLE: "  UNAVAIL", NA: "  --    ",
         PROMPT: "  PROMPT"}


class Result:
    def __init__(self, tier, name, status, detail="", remediation="", scope_note=""):
        self.tier, self.name, self.status = tier, name, status
        self.detail, self.remediation, self.scope_note = detail, remediation, scope_note


def run(cmd, cwd=REPO_ROOT, timeout=600):
    """Run a command, returning (returncode, combined_output). -1 = not found."""
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except FileNotFoundError:
        return -1, f"executable not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return -2, f"timed out after {timeout}s: {' '.join(cmd)}"


def git(*args):
    code, out = run(["git", *args])
    return out.strip() if code == 0 else ""


def _could_not_run(out):
    """Distinguish 'the check failed' from 'the check never ran'."""
    # SyntaxError/IndentationError mean the file could not even be PARSED, so it
    # never ran - reporting that as a failed check would attribute a crash to
    # the code under audit. Found the hard way: an f-string containing a
    # backslash is a SyntaxError before Python 3.12, and macOS /usr/bin/python3
    # is 3.9 yet ships PyYAML, so it got selected and then died.
    return bool(re.search(r"ModuleNotFoundError|ImportError:|No module named|"
                          r"SyntaxError|IndentationError|"
                          r"command not found|executable not found|timed out after", out))


def _tier_d_coverage():
    """The declared Tier D coverage, or None. Read rather than hardcoded so the
    number cannot drift from the registry that states it."""
    try:
        reg = yaml.safe_load(RULES_FILE.read_text(encoding="utf-8"))
        return reg.get("tier_d_coverage")
    except Exception:
        return None


def _pytest_testpaths():
    """The pytest surfaces, read from pyproject.toml so this cannot drift.

    Falls back to discovery if the file is unreadable - but never to "none",
    because silently finding zero pytest suites is how 34 test files went
    unrun while the gate reported success.
    """
    cfg = REPO_ROOT / "pyproject.toml"
    try:
        import tomllib
        data = tomllib.loads(cfg.read_text(encoding="utf-8"))
        paths = (data.get("tool", {}).get("pytest", {})
                 .get("ini_options", {}).get("testpaths", []))
        found = [p for p in paths if (REPO_ROOT / p).is_dir()]
        if found:
            return found
    except Exception:
        pass
    return sorted(str(p.relative_to(REPO_ROOT))
                  for p in (REPO_ROOT / "tests").iterdir()
                  if p.is_dir() and any(p.glob("test_*.py")))


# ───────────────────────────── diff scoping ──────────────────────────────────

class Diff:
    """What this change touched. Compared against the merge base, and including
    the working tree - a pre-push gate that only looked at HEAD would miss
    uncommitted work when run by hand."""

    def __init__(self, since):
        self.base = git("merge-base", since, "HEAD") or since
        self.since = since
        # Untracked files count as added. `git diff` cannot see them, so a brand
        # new file - exactly the shape of a stray analysis artifact - would slip
        # past a diff-only gate until someone staged it.
        untracked = [f for f in git("ls-files", "--others",
                                    "--exclude-standard").splitlines() if f]
        self.changed = sorted(set(
            [f for f in git("diff", "--name-only", self.base).splitlines() if f]
            + untracked))
        self.added = sorted(set(
            [f for f in git("diff", "--name-only", "--diff-filter=A",
                            self.base).splitlines() if f] + untracked))
        self.untracked = untracked
        self.branch = git("rev-parse", "--abbrev-ref", "HEAD")

    def match(self, globs, pool=None):
        pool = self.changed if pool is None else pool
        hits = []
        for g in globs or []:
            rx = _glob_re(g)
            hits += [f for f in pool if rx.match(f)]
        return sorted(set(hits))


def _glob_re(pattern):
    """fnmatch treats * as crossing / , which makes 'force-app/**/profiles/*'
    match too much. Translate ** and * separately."""
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?"); i += 3
        elif pattern.startswith("**", i):
            out.append(".*"); i += 2
        elif pattern[i] == "*":
            out.append("[^/]*"); i += 1
        elif pattern[i] == "?":
            out.append("[^/]"); i += 1
        else:
            out.append(re.escape(pattern[i])); i += 1
    return re.compile("^" + "".join(out) + "$")


def repo_files(globs, exclude=()):
    tracked = git("ls-files").splitlines()
    hits = []
    for g in globs or []:
        rx = _glob_re(g)
        hits += [f for f in tracked if rx.match(f)]
    for g in exclude or ():
        rx = _glob_re(g)
        hits = [f for f in hits if not rx.match(f)]
    return sorted(set(hits))


# ─────────────────────────────── Tier A ──────────────────────────────────────

def tier_a(diff, args):
    py = sys.executable
    out_results = []
    add = out_results.append

    def simple(name, cmd, remediation, scope_note=""):
        code, out = run(cmd)
        if code == 0:
            return Result("A", name, PASS, scope_note=scope_note)
        if code < 0 or _could_not_run(out):
            return Result("A", name, UNAVAILABLE, out.strip().splitlines()[-1][:160]
                          if out.strip() else "", remediation, scope_note)
        tail = [l for l in out.strip().splitlines() if l.strip()][-1:] or [""]
        return Result("A", name, FAIL, tail[0][:160], remediation, scope_note)

    add(simple("analyze_agent_tooling check",
               [py, "scripts/ai/analyze_agent_tooling.py", "check"],
               "Run it directly to see which of its checks failed."))

    add(simple("skill_manifest --check",
               [py, "scripts/ai/skill_manifest.py", "--check"],
               "The cross-repo skill manifest cannot resolve. See "
               ".cursor/skills/pmos-integration/SKILL.md."))

    add(simple("plan README consistency",
               [py, "scripts/ai/check_plan_readme_consistency.py"],
               "Update the plan README so its object table and record counts match "
               "export.json + the CSVs.",
               scope_note="repo-wide, all plans"))

    # generate_cci_reference must be a NO-OP on a clean tree. Running it and then
    # diffing is the only honest check: a stale reference file and a never-run
    # generator look identical if you only check the exit code.
    gen_targets = [".cursor/skills/cci-orchestration/tasks-reference.md",
                   ".cursor/skills/cci-orchestration/flows-reference.md",
                   ".cursor/skills/cci-orchestration/feature-flags.md"]
    before = git("status", "--porcelain", *gen_targets)
    code, out = run([py, "scripts/ai/generate_cci_reference.py"])
    if code != 0 or _could_not_run(out):
        add(Result("A", "generated CCI reference", UNAVAILABLE,
                   out.strip().splitlines()[-1][:160] if out.strip() else "",
                   "generate_cci_reference.py did not run. This is the trap the pack "
                   "names: an empty diff after a script that never ran reads as a pass."))
    else:
        after = git("status", "--porcelain", *gen_targets)
        if after != before:
            add(Result("A", "generated CCI reference", FAIL,
                       "regenerating changed the committed reference files",
                       "Commit the regenerated files: "
                       "python scripts/ai/generate_cci_reference.py"))
        else:
            add(Result("A", "generated CCI reference", PASS,
                       scope_note="ran the generator, diffed its 3 outputs"))

    # SFDMU validator: exits 1 on a CLEAN tree. Compare the FAILING PLAN NAMES
    # against the pinned baseline instead of trusting the exit code.
    if diff.match(["datasets/**"]) or args.all_checks:
        code, out = run([py, "scripts/validate_sfdmu_v5_datasets.py"])
        if code < 0 or _could_not_run(out):
            add(Result("A", "SFDMU v5 datasets", UNAVAILABLE, out.strip()[-160:],
                       "Could not run scripts/validate_sfdmu_v5_datasets.py."))
        else:
            failing = set(re.findall(r"^### \S+ FAIL (\S+)", out, re.M))
            new = failing - SFDMU_BASELINE_FAILURES
            fixed = SFDMU_BASELINE_FAILURES - failing
            note = (f"baseline pins {len(SFDMU_BASELINE_FAILURES)} known-failing plans "
                    f"by name: {', '.join(sorted(SFDMU_BASELINE_FAILURES))}")
            if new:
                add(Result("A", "SFDMU v5 datasets", FAIL,
                           f"NEW failing plan(s): {', '.join(sorted(new))}",
                           "Run python scripts/validate_sfdmu_v5_datasets.py and fix, or "
                           "justify and add to SFDMU_BASELINE_FAILURES with a reason.",
                           note))
            else:
                detail = ("baseline plan(s) now PASSING: " + ", ".join(sorted(fixed)) +
                          " - tighten SFDMU_BASELINE_FAILURES") if fixed else ""
                add(Result("A", "SFDMU v5 datasets", PASS, detail, "", note))
    else:
        add(Result("A", "SFDMU v5 datasets", NA, "no datasets/ change in this diff"))

    # Expression Set JSON, only what changed.
    es = [f for f in diff.match(["datasets/**/*.json", "**/expression_set*/**/*.json"])
          if Path(REPO_ROOT / f).exists()]
    if es:
        bad = []
        for f in es:
            code, out = run([py, "scripts/ai/validate_expression_set.py", f])
            if code == 1:
                bad.append(f)
        add(Result("A", "expression-set schema", FAIL if bad else PASS,
                   ", ".join(bad[:4]),
                   "python scripts/ai/validate_expression_set.py <file>",
                   f"{len(es)} changed JSON file(s) considered"))
    else:
        add(Result("A", "expression-set schema", NA, "no candidate JSON changed"))

    # THREE test surfaces, not one. Running only the top-level glob covers 13 of
    # 47 files and reports "13 suite(s)" as though that were the whole surface -
    # exactly the silent scope truncation the todo pack forbids.
    #   tests/*.py          self-contained, run DIRECTLY. pyproject.toml is
    #                       explicit that these must NOT be pytest-collected:
    #                       they aggregate via check() and gate on main()'s exit
    #                       code, so under pytest their test_* functions would
    #                       false-pass because the checks never raise.
    #   pyproject testpaths real pytest suites (build_harness, txn_data_harness).
    direct = sorted(p.name for p in (REPO_ROOT / "tests").glob("*.py"))
    failed, unavailable = [], []
    for t in direct:
        code, out = run([py, f"tests/{t}"], timeout=300)
        if code == 0:
            continue
        (unavailable if (code < 0 or _could_not_run(out)) else failed).append(t)

    paths = _pytest_testpaths()
    n_pytest = sum(len(list((REPO_ROOT / p).rglob("test_*.py"))) for p in paths)
    if paths:
        code, out = run([py, "-m", "pytest", "-q", *paths], timeout=900)
        if code != 0:
            if code < 0 or _could_not_run(out) or "No module named pytest" in out:
                unavailable.append(f"pytest [{', '.join(paths)}]")
            else:
                failed.append(f"pytest [{', '.join(paths)}]")

    note = (f"{len(direct)} direct + {n_pytest} pytest file(s) across "
            f"{1 + len(paths)} surface(s)")
    if failed:
        add(Result("A", "offline test suites", FAIL, ", ".join(failed),
                   "Run the suite directly to see the assertion.", note))
    elif unavailable:
        add(Result("A", "offline test suites", UNAVAILABLE, ", ".join(unavailable),
                   "A dependency is missing, so these did not run at all - which is "
                   "NOT a pass. Prepare the project venv: "
                   "python -m venv .venv && source .venv/bin/activate && "
                   "pip install -r requirements-dev.txt", note))
    else:
        add(Result("A", "offline test suites", PASS, "", "", note))

    # Prettier on Apex - enforced as of this branch (todo 080 Tier A decision).
    apex = diff.match(["**/*.cls", "**/*.trigger", "**/*.apex"])
    apex = [f for f in apex if (REPO_ROOT / f).exists()]
    if apex:
        code, out = run(["npx", "--no-install", "prettier", "--check", *apex])
        if code < 0 or "not found" in out.lower():
            add(Result("A", "prettier (Apex)", UNAVAILABLE, out.strip()[-120:],
                       "npx/prettier unavailable. npm install."))
        else:
            add(Result("A", "prettier (Apex)", PASS if code == 0 else FAIL,
                       "" if code == 0 else "run: npm run prettier:apex",
                       "npm run prettier:apex", f"{len(apex)} changed Apex file(s)"))
    else:
        add(Result("A", "prettier (Apex)", NA, "no Apex changed"))

    # eslint, scoped to CHANGED LWC js. Repo-wide is red today (issue #205), so a
    # repo-wide gate would be permanently failing and would get disabled.
    lwc = [f for f in diff.match(["**/lwc/**/*.js"]) if (REPO_ROOT / f).exists()]
    if lwc:
        code, out = run(["npx", "--no-install", "eslint", "--max-warnings", "0", *lwc])
        if code < 0:
            add(Result("A", "eslint (changed LWC)", UNAVAILABLE, out.strip()[-120:],
                       "npx/eslint unavailable. npm install."))
        else:
            last = [l for l in out.strip().splitlines() if l.strip()][-1:] or [""]
            add(Result("A", "eslint (changed LWC)", PASS if code == 0 else FAIL,
                       "" if code == 0 else last[0][:160],
                       "Fix all problems INCLUDING warnings - an unused eslint-disable "
                       "is itself a finding.",
                       f"{len(lwc)} changed LWC file(s); repo-wide is knowingly red "
                       f"(issue #205)"))
    else:
        add(Result("A", "eslint (changed LWC)", NA, "no LWC js changed"))

    # PR review threads - only meaningful with a PR number.
    if args.pr:
        code, out = run([py, "scripts/ai/pr_review.py", "verify", str(args.pr)])
        if code < 0 or _could_not_run(out):
            add(Result("A", f"PR #{args.pr} threads", UNAVAILABLE, out.strip()[-160:],
                       "Needs the gh CLI, authenticated."))
        else:
            add(Result("A", f"PR #{args.pr} threads", PASS if code == 0 else FAIL,
                       "" if code == 0 else "unresolved review threads remain",
                       "Every round ends at 0 unresolved: "
                       f"python scripts/ai/pr_review.py status {args.pr}"))
    else:
        add(Result("A", "PR review threads", NA, "no --pr given"))

    return out_results


# ────────────────────────── Tiers B / C / D ──────────────────────────────────

def _scan_files(files, patterns, ignore_comments, allow):
    findings = []
    compiled = [re.compile(p) for p in patterns]
    for f in files:
        path = REPO_ROOT / f
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if ignore_comments and re.match(r"\s*(?://|\*|/\*|<!--|#)", line):
                continue
            for rx in compiled:
                m = rx.search(line)
                if m and f"{f}::{m.group(0).strip()}" not in allow:
                    findings.append(f"{f}:{lineno}")
                    break
    return findings


def tier_bcd(diff, acked):
    if not RULES_FILE.exists():
        return [Result("B", "gate_rules.yml", UNAVAILABLE, f"missing {RULES_FILE}")]
    try:
        registry = yaml.safe_load(RULES_FILE.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [Result("B", "gate_rules.yml", UNAVAILABLE, f"invalid YAML: {exc}")]

    results = []
    for rule in registry.get("rules") or []:
        rid = rule.get("id", "<unnamed>")
        tier = rule.get("tier", "?")
        scope = rule.get("scope")
        rem = " ".join((rule.get("remediation") or "").split())
        allow = {f"{e['file']}::{e['match']}" for e in (rule.get("allow_list") or [])
                 if "file" in e and "match" in e}
        allow_files = {e["file"] for e in (rule.get("allow_list") or [])
                       if "file" in e and "match" not in e}

        def done(status, detail="", note=""):
            results.append(Result(tier, rid, status, detail, rem, note))

        if scope == "branch":
            forbidden = rule.get("forbid_branches") or []
            if diff.branch in forbidden:
                done(FAIL, f"HEAD is on '{diff.branch}'")
            else:
                done(PASS, "", f"on '{diff.branch}'")
            continue

        if rule.get("detection") == "review-prompt":
            pool = diff.added if rule.get("only_added") else diff.changed
            hits = diff.match(rule.get("paths"), pool=pool)
            hits = [h for h in hits if not any(_glob_re(g).match(h)
                                              for g in rule.get("exclude_paths") or [])]
            # A prompt that fires on files it has no evidence about gets --ack'd
            # reflexively. Narrow to files that actually contain the thing.
            cfilter = rule.get("content_filter")
            if cfilter and hits:
                rxs = [re.compile(p) for p in cfilter]
                hits = [h for h in hits
                        if (REPO_ROOT / h).exists()
                        and any(rx.search((REPO_ROOT / h).read_text(
                            encoding="utf-8", errors="replace")) for rx in rxs)]
            scope_desc = "newly added only" if rule.get("only_added") else "changed"
            if cfilter:
                scope_desc += f", containing /{cfilter[0]}/"
            if not hits:
                done(NA, f"nothing in scope ({scope_desc})")
            elif rid in acked:
                done(PASS, f"acknowledged (--ack {rid})",
                     f"{len(hits)} file(s) in scope ({scope_desc})")
            else:
                done(PROMPT, f"{len(hits)} file(s) need a human decision: "
                             + ", ".join(hits[:3]) + (" ..." if len(hits) > 3 else ""),
                     scope_desc)
            continue

        if scope == "changed-path":
            hits = [h for h in diff.match(rule.get("paths")) if h not in allow_files]
            done(FAIL if hits else PASS,
                 ", ".join(hits[:5]) + (f" (+{len(hits)-5})" if len(hits) > 5 else ""))

        elif scope == "added-path":
            hits = [h for h in diff.match(rule.get("paths"), pool=diff.added)
                    if h not in allow_files]
            done(FAIL if hits else PASS,
                 ", ".join(hits[:5]), "newly ADDED files only")

        elif scope in ("changed-content", "repo-content"):
            if scope == "changed-content":
                files = diff.match(rule.get("paths"))
                files = [f for f in files if not any(_glob_re(g).match(f)
                         for g in rule.get("exclude_paths") or [])]
                note = f"{len(files)} changed file(s) in scope"
            else:
                files = repo_files(rule.get("paths"), rule.get("exclude_paths"))
                note = f"{len(files)} file(s), repo-wide"
            pats = rule.get("patterns") or []
            if not pats:
                done(UNAVAILABLE, "mechanical rule with no patterns")
                continue
            try:
                hits = _scan_files(files, pats, rule.get("ignore_comment_lines"), allow)
            except re.error as exc:
                done(UNAVAILABLE, f"bad regex: {exc}")
                continue
            done(FAIL if hits else PASS,
                 ", ".join(hits[:5]) + (f" (+{len(hits)-5})" if len(hits) > 5 else ""),
                 note)

        elif scope == "exact-value":
            files = repo_files(rule.get("paths"))
            need = rule.get("require") or ""
            missing = [f for f in files
                       if need not in (REPO_ROOT / f).read_text(encoding="utf-8",
                                                                errors="replace")]
            done(FAIL if missing else PASS, ", ".join(missing),
                 f"{len(files)} file(s) must contain the placeholder")

        elif scope == "paired-change":
            # only_added narrows the trigger to NEW files. Several map rows are
            # about registering a new thing ("new docs/guides/*.md -> README
            # Primary Guides"); firing them on every edit to an existing file
            # would be noise, and a noisy rule gets ignored or deleted.
            pool = diff.added if rule.get("only_added") else diff.changed
            trigger = diff.match(rule.get("when_changed"), pool=pool)
            trigger = [t for t in trigger
                       if not any(_glob_re(g).match(t)
                                  for g in rule.get("exclude_paths") or [])]
            if not trigger:
                done(NA, "no trigger" +
                     (" (new files only)" if rule.get("only_added") else ""))
            elif not repo_files(rule.get("require_changed")):
                # A companion glob matching nothing TRACKED is a registry bug,
                # not a code defect: the rule could never be satisfied, so it
                # would fail forever and get --ack'd or deleted. Surfacing it as
                # could-not-execute points at the right thing - a renamed or
                # moved doc - instead of blaming the change under audit.
                done(UNAVAILABLE,
                     f"require_changed matches no tracked file: "
                     f"{rule.get('require_changed')}",
                     "registry path is stale - the companion doc moved or was renamed")
            else:
                partner = diff.match(rule.get("require_changed"))
                done(PASS if partner else FAIL,
                     "" if partner else
                     f"{len(trigger)} file(s) changed but no companion did",
                     f"triggered by {trigger[0]}"
                     + (f" (+{len(trigger)-1})" if len(trigger) > 1 else ""))
        else:
            done(UNAVAILABLE, f"unknown scope {scope!r}")

    return results


# ─────────────────────────────── Tier E ──────────────────────────────────────

def tier_e():
    code, out = run([sys.executable, "scripts/ai/defect_scan.py", "--quiet"])
    if code == 2 or _could_not_run(out):
        return [Result("E", "defect-class registry", UNAVAILABLE,
                       out.strip().splitlines()[-1][:160] if out.strip() else "",
                       "defect_scan.py could not run - see its own output.")]
    if code == 1:
        names = re.findall(r"^\s*FAIL\s+(\S+)", out, re.M)
        return [Result("E", "defect-class registry", FAIL, ", ".join(names),
                       "python scripts/ai/defect_scan.py  (shows file:line per class)",
                       "whole repo surface, not just the diff")]
    summary = re.search(r"classes: .*", out)
    return [Result("E", "defect-class registry", PASS, "",
                   "", summary.group(0) if summary else "")]


# ─────────────────────────────── report ──────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", default="main", help="diff base (default: main)")
    ap.add_argument("--pr", type=int, help="also require 0 unresolved threads on this PR")
    ap.add_argument("--tier", help="comma-separated subset, e.g. B,C")
    ap.add_argument("--ack", action="append", default=[], metavar="RULE_ID",
                    help="acknowledge a review-prompt rule (repeatable)")
    ap.add_argument("--all-checks", action="store_true",
                    help="run scope-gated checks even when the diff does not touch them")
    ap.add_argument("--list", action="store_true", help="list rules and exit")
    args = ap.parse_args()

    if args.list:
        reg = yaml.safe_load(RULES_FILE.read_text(encoding="utf-8"))
        for r in reg.get("rules") or []:
            print(f"  {r.get('tier')}  {r.get('id'):45s} {r.get('detection'):14s} "
                  f"{r.get('severity','')}")
        return 0

    wanted = {t.strip().upper() for t in args.tier.split(",")} if args.tier else None
    diff = Diff(args.since)

    print(f"pre-push audit — branch '{diff.branch}', {len(diff.changed)} file(s) changed "
          f"vs {args.since} ({diff.base[:9]})")
    if not diff.changed:
        print("  note: no differences from the base — most diff-scoped checks are n/a")
    print()

    results = []
    if not wanted or "A" in wanted:
        results += tier_a(diff, args)
    if not wanted or wanted & {"B", "C", "D"}:
        results += [r for r in tier_bcd(diff, set(args.ack))
                    if not wanted or r.tier in wanted]
    if not wanted or "E" in wanted:
        results += tier_e()

    cov = _tier_d_coverage()
    last_tier = None
    for r in results:
        if r.tier != last_tier:
            print(f"── Tier {r.tier} " + "─" * 58)
            # Announce partial coverage AT the tier, not in a footnote. A tier
            # that quietly mechanises a fraction of its stated scope reads as
            # complete, which is how an unimplemented row let three
            # undocumented scripts through.
            if r.tier == "D" and cov:
                n_prompt = len(cov.get("covered_as_prompt") or [])
                print(f"   ⚠ PARTIAL: {cov['covered_rows']} of {cov['total_rows']} "
                      f"change-surface map rows enforced"
                      + (f" ({n_prompt} as blocking prompts, not greppable)"
                         if n_prompt else "")
                      + f"; {len(cov.get('uncovered') or [])} still unenforced "
                      f"(see gate_rules.yml → tier_d_coverage)")
            last_tier = r.tier
        line = f"{_ICON[r.status]} {r.name}"
        if r.scope_note:
            line += f"   [{r.scope_note}]"
        print(line)
        if r.detail:
            print(f"            {r.detail}")
        if r.status in (FAIL, UNAVAILABLE, PROMPT) and r.remediation:
            print(f"            fix: {r.remediation}")

    failed = [r for r in results if r.status == FAIL]
    unavail = [r for r in results if r.status == UNAVAILABLE]
    prompts = [r for r in results if r.status == PROMPT]
    ran = [r for r in results if r.status in (PASS, FAIL)]

    print()
    print(f"{len(ran)} check(s) executed · {len(failed)} failed · "
          f"{len(unavail)} could not run · {len(prompts)} awaiting acknowledgement · "
          f"{len([r for r in results if r.status == NA])} not applicable")

    if unavail:
        print("\nCHECKS THAT DID NOT RUN ARE NOT PASSES:")
        for r in unavail:
            print(f"  - {r.name}: {r.detail}")
    if prompts:
        print("\nREVIEW PROMPTS — confirm each, then re-run with the flag shown:")
        for r in prompts:
            print(f"  - {r.name}\n      --ack {r.name}")
    if failed:
        print(f"\n{len(failed)} FAILING: " + ", ".join(r.name for r in failed))

    if unavail or prompts:
        return 2
    if failed:
        return 1
    print("\nclean — safe to push.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

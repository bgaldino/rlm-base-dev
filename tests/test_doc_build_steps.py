"""Audit `N.M | <flow>` build-step numbers in docs against cumulusci.yml.

These numbers are hand-maintained and have no generator, so they drift silently
every time a step is inserted into or removed from `prepare_rlm_org` or one of
its subflows. #264-55 is what that costs: eight rows in
`docs/references/revenue-cloud-permissions.md` had gone off by one on the parent
number, and the `prepare_agents` permission-set row was *additionally* wrong on
the substep because a step had been removed from that subflow. Two independent
reviewers flagged the substep; nobody noticed the parents; and the first fix
attempt refuted a correct finding because it was audited against a stale
checkout. All of that is mechanically checkable, which is what this does.

What a row must satisfy, given a cell of the form `| N.M |` on a line that also
names a subflow of `prepare_rlm_org`:

  N  is that subflow's step number *in* `prepare_rlm_org`
  M  is a step that exists in that subflow

Scope note: the scan is repo-wide over `*.md` rather than pinned to the one file
that currently has such rows, so a new doc adopting the convention is covered
without editing this test. It is deliberately conservative about what counts as
a row -- the cell must be exactly `N.M` (so `| 5.8.0 |` and `| 68.0 |` do not
match) *and* the line must name a known flow -- because a false positive here
trains people to ignore the check.

Run:  <cci-venv-python> tests/test_doc_build_steps.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# A table cell holding exactly `N.M`, nothing else.
_STEP_CELL = re.compile(r"\|\s*(\d+)\.(\d+)\s*\|")

# Directories whose markdown is not ours to audit.
_SKIP_PARTS = {".git", "node_modules", ".venv", ".harness", ".agents"}

_passed = _total = 0
_failures = []


def check(label, cond, detail=""):
    global _passed, _total
    _total += 1
    if cond:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label}  {detail}")
        _failures.append((label, detail))


def _load_flows():
    import yaml  # lazy: keeps import-time stdlib-only

    with open(os.path.join(REPO, "cumulusci.yml"), encoding="utf-8") as fh:
        return yaml.safe_load(fh)["flows"]


def _steps(flows, flow_name):
    """Step numbers declared by a flow, as ints."""
    raw = (flows.get(flow_name) or {}).get("steps") or {}
    out = set()
    for key in raw:
        try:
            out.add(int(key))
        except (TypeError, ValueError):
            continue
    return out


def _subflow_positions(flows, parent="prepare_rlm_org"):
    """Map subflow name -> its step number in the parent flow.

    A step whose `flow` is the string "None" is a *disabled* step -- CumulusCI's
    way of skipping an inherited step -- so it is not a position anyone can cite.
    """
    positions = {}
    for key, step in ((k, v) for k, v in (flows[parent].get("steps") or {}).items()):
        if not isinstance(step, dict):
            continue
        name = step.get("flow")
        if not name or name == "None":
            continue
        try:
            positions[name] = int(key)
        except (TypeError, ValueError):
            continue
    return positions


def _markdown_files():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in _SKIP_PARTS]
        for name in files:
            if name.endswith(".md"):
                yield os.path.join(root, name)


def audit(flows):
    """Yield (relpath, lineno, flow, doc_parent, doc_sub, problem) for bad rows."""
    positions = _subflow_positions(flows)
    substeps = {name: _steps(flows, name) for name in positions}
    rows = 0
    for path in _markdown_files():
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        rel = os.path.relpath(path, REPO)
        for lineno, line in enumerate(lines, 1):
            m = _STEP_CELL.search(line)
            if not m:
                continue
            named = [f for f in positions if f in line]
            if not named:
                continue
            # Longest match wins: `prepare_core` is a substring of nothing here,
            # but `prepare_pricing_data` vs `prepare_pricing_discovery` shows the
            # shape, and a shorter accidental match would blame the wrong flow.
            flow = max(named, key=len)
            rows += 1
            parent, sub = int(m.group(1)), int(m.group(2))
            if parent != positions[flow]:
                yield (rel, lineno, flow, parent, sub,
                       f"parent should be {positions[flow]}, doc says {parent}")
            elif sub not in substeps[flow]:
                have = sorted(substeps[flow])
                yield (rel, lineno, flow, parent, sub,
                       f"{flow} has no step {sub} (has {have[0]}..{have[-1]})")
    audit.rows_seen = rows


def main():
    print("Doc build-step numbers vs cumulusci.yml")
    print("=" * 116)
    try:
        flows = _load_flows()
    except ImportError:
        print("  [SKIP] PyYAML unavailable — cannot parse cumulusci.yml")
        return 0

    problems = list(audit(flows))
    seen = getattr(audit, "rows_seen", 0)

    # A silent zero is the failure mode that matters most: if the regex or the
    # flow-name join ever stops matching, an empty problem list looks like
    # success. Assert the scan found rows to audit at all.
    check("scan_found_rows_to_audit", seen > 0,
          "no `N.M | <flow>` rows matched anywhere — the scan itself is broken, "
          "which would report clean no matter how wrong the docs were")

    check("no_step_number_mismatches", not problems,
          f"{len(problems)} bad row(s) out of {seen}")
    for rel, lineno, flow, parent, sub, problem in problems:
        print(f"         {rel}:{lineno}  [{flow}] doc={parent}.{sub} — {problem}")

    print("=" * 116)
    print(f"{_passed}/{_total} checks passed  ({seen} step rows audited)")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())

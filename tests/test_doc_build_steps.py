"""Audit `N.M(.Z)` build-step citations in docs against the real resolved flow.

These citations are hand-maintained with no generator, so they drift silently
every time a step is inserted into or removed from `prepare_rlm_org` or one of
its subflows. #264-55 is what that costs: eight rows in
`docs/references/revenue-cloud-permissions.md` had gone off by one, and the
`prepare_agents` row was *additionally* wrong on its substep. Two reviewers
flagged the substep; nobody caught the parents.

**Existence is not enough, and the first version of this check learned that the
hard way.** Asserting only that substep `M` is *some* declared step passes every
insertion, because this repo renumbers rather than leaving gaps: inserting
`fix_scratch_org_identity` at `prepare_core` step 1 shifted everything after it,
yet `1.3`, `1.6`, `1.9`, `1.10` and `1.12` all still pointed at *existing*
steps — just the wrong ones. So a row must name the step it means, and the check
verifies the citation resolves to exactly that:

    | 1.4 | `prepare_core` > `assign_permission_set_licenses` | … |
      └ coordinate                └ the path it must resolve to

Two directions are checked, because drift and omission are different failures:

1. **Every cited coordinate resolves to the path the row names.** Catches
   renumbering, a wrong substep, and a row pointing at a different task.
2. **Every permission-assigning step in the flow is cited.** Catches the
   opposite failure: `prepare_payments`, `prepare_billing`, `prepare_prm_pricing`,
   `prepare_inapp` and one `prepare_personas` assignment were **missing entirely**
   from a table whose own preamble claims to list them all, so five permission
   sets were being granted by the build with no entry in the permissions
   reference. Scoped to the file that makes that claim (found by its heading),
   not repo-wide.

**Two notations, because the docs use two.** The coordinate form above is only
40 citations repo-wide. The other form -- `` `prepare_agents` step 10 `` -- is
~290, including a second table *in the same permissions file* whose step cell is
not the first column, and the whole of the generated flag reference. Auditing
only the first notation leaves that surface uncovered while reporting the file
clean, so both are checked:

    `prepare_quantumbit` step 4       flow + step, either order
    step 28 of `prepare_rlm_org`      reversed

For that form the assertion is necessarily weaker: the text names a step number
but not the task, so only existence can be checked. That is a real limit, not a
theoretical one -- "assigned early in `prepare_core` (steps 2, 7, 8, 10)" was
wrong (the PSL assignments are 1.4 and 1.9.1-1.9.4) and every one of those four
numbers *exists*, so this check could not prove it. It was found by reading, and
fixed by rewriting the sentence into a form that names the flow whose steps they
are. **Prefer the coordinate form in new writing**, and when prose must cite a
step, name the innermost flow so at least the range is pinned.

Ground truth is **CumulusCI's own flow resolution**, not a hand-parse of
`cumulusci.yml`. That is what makes the coordinates trustworthy: CCI resolves
subflow nesting, `flow: None` disabling, inherited steps, and fractional step
keys (`1.1`), and its `step_num` (`1/9/1`) maps 1:1 onto the doc's `1.9.1`.
Re-implementing any of that here would just be a second, wronger parser.

Run:  <cci-venv-python> tests/test_doc_build_steps.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

ROOT_FLOW = "prepare_rlm_org"

# The table that claims to list every permission assignment, identified by the
# heading that makes the claim rather than by path, so moving the file does not
# silently disable direction 2.
COMPLETENESS_HEADING = "## Assignment Order in `prepare_rlm_org`"

# Steps that grant something. `recalculate_permission_set_groups` and `deploy_pre`
# are cited by the table for context but are not grants, so they are allowed
# without being required.
GRANTING_PREFIX = "assign_permission_set"

# `| N.M |` or `| N.M.Z |` as the FIRST cell of a table row. Anchored at the row
# start so pipe-containing prose and mid-row numbers are not read as citations.
# `[1-9]\d*` after each dot is load-bearing rather than cosmetic: CumulusCI step
# numbers are 1-based, so a `.0` is never a step, and without it an API-version
# cell like `| 68.0 |` parses as step 68 substep 0 and gets reported as a missing
# step. (An earlier version of this file claimed `| 68.0 |` could not match. It
# could — 4,000+ lines repo-wide match the bare number shape, and the only thing
# keeping them out was the flow-name requirement below.)
_ROW = re.compile(r"^\s*\|\s*(\d+)\.([1-9]\d*)(?:\.([1-9]\d*))?\s*\|(.*)$")
_BACKTICKED = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")
_FENCE = re.compile(r"^\s*(?:```|~~~)")

# The prose / second-table form. Three shapes that mean two different things, and
# conflating them would invent failures:
#
#   `prepare_agents` step 10      -> step 10 *inside* prepare_agents
#   step 2 of `prepare_ux`        -> same, reversed
#   `prepare_large_stx` at step 27 -> prepare_large_stx *is* step 27 of the root
#
# The flow name must be backticked and adjacent, which is what keeps ordinary
# "step 3" prose from being read as a citation.
_INSIDE = re.compile(r"`([a-z][a-z0-9_]*)`\s+step\s+(\d+)(?![\d.])")
# Plural: "`prepare_core` (steps 2, 7, 8, 10)". Worth matching rather than
# rewriting away, because a list of four numbers is four chances to drift and it
# is the shape a reader is least likely to re-derive by hand.
_INSIDE_PLURAL = re.compile(r"`([a-z][a-z0-9_]*)`\s*\(steps?\s+([\d,\s]+?)\)")
_INSIDE_OF = re.compile(r"\bstep\s+(\d+)(?![\d.])\s+of\s+`([a-z][a-z0-9_]*)`")
_AT_ROOT = re.compile(r"`([a-z][a-z0-9_]*)`[^|`\n]{0,12}?\bat\s+step\s+(\d+)(?![\d.])")

_SKIP_PARTS = {".git", "node_modules", ".venv", ".harness", ".agents", "__pycache__"}

_passed = _total = 0


def check(label, cond, detail=""):
    global _passed, _total
    _total += 1
    if cond:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label}  {detail}")


def resolve_flow():
    """Return {dotted step number: path} for the fully resolved root flow.

    Raises so a broken toolchain is never mistaken for a clean audit.
    """
    from cumulusci.cli.runtime import CliRuntime  # lazy: import time stays light

    runtime = CliRuntime(load_keychain=False)
    coordinator = runtime.get_flow(ROOT_FLOW)
    return {
        str(step.step_num).replace("/", "."): (step.path, step.task_name)
        for step in coordinator.steps
    }


def index_flows(steps):
    """Return (steps inside each flow, which flow sits at each root step number).

    Derived from the resolved coordinates rather than re-read from YAML: a step at
    `1.9.1` with path `prepare_core.assign_feature_psls.<task>` says root step 1 is
    `prepare_core`, `prepare_core` has a step 9 which is `assign_feature_psls`, and
    that has a step 1. Nested flows are flattened by the coordinator, so this is
    the only place their own step numbering can be recovered.
    """
    inside, root_at = {}, {}
    for coord, (path, _task) in steps.items():
        cs, ps = coord.split("."), path.split(".")
        owners = [ROOT_FLOW] + ps[:-1]
        for depth, owner in enumerate(owners):
            if depth < len(cs):
                inside.setdefault(owner, set()).add(int(cs[depth]))
        if len(ps) > 1:
            root_at[int(cs[0])] = ps[0]
    return inside, root_at


def audit_named_steps(inside, root_at):
    """Audit the `<flow> step N` citation form. Returns (problems, count)."""
    problems, seen = [], 0
    for path in _markdown_files():
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        rel = os.path.relpath(path, REPO)
        for lineno, line in enumerate(text.splitlines(), 1):
            claims = [(f, int(n), "inside") for f, n in _INSIDE.findall(line)]
            claims += [(f, int(n), "inside") for n, f in _INSIDE_OF.findall(line)]
            claims += [(f, int(n), "root") for f, n in _AT_ROOT.findall(line)]
            for flow, numbers in _INSIDE_PLURAL.findall(line):
                claims += [(flow, int(n), "inside")
                           for n in numbers.replace(" ", "").split(",") if n]
            for flow, num, kind in claims:
                # An unknown name is usually a task, a standalone flow that is not
                # part of this root flow, or prose about something else entirely --
                # not a defect, and guessing would flood the output.
                if kind == "inside":
                    if flow not in inside:
                        continue
                    seen += 1
                    if num not in inside[flow]:
                        have = sorted(inside[flow])
                        problems.append((rel, lineno, f"`{flow}` step {num}",
                                         f"{flow} has no step {num} "
                                         f"(has {have[0]}..{have[-1]})"))
                else:
                    if flow not in inside and flow not in root_at.values():
                        continue
                    seen += 1
                    actual = root_at.get(num)
                    if actual != flow:
                        where = f"step {num} is `{actual}`" if actual else \
                                f"{ROOT_FLOW} has no step {num}"
                        problems.append((rel, lineno, f"`{flow}` at step {num}",
                                         f"{where}"))
    return problems, seen


def _markdown_files():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in _SKIP_PARTS]
        for name in sorted(files):
            if name.endswith(".md"):
                yield os.path.join(root, name)


def _rows(text):
    """Yield (lineno, coordinate, chain) for citation rows outside code/comments.

    A fenced block or an HTML comment can hold an illustrative or retired row;
    auditing those produces failures nobody can act on, which is how a check
    teaches people to ignore it.
    """
    in_fence = in_comment = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if in_comment:
            in_comment = "-->" not in line
            continue
        if line.lstrip().startswith("<!--"):
            in_comment = "-->" not in line
            continue
        m = _ROW.match(line)
        if not m:
            continue
        parent, sub, nested, rest = m.groups()
        coord = ".".join(p for p in (parent, sub, nested) if p)
        cell = rest.split("|")[0]
        yield lineno, coord, _BACKTICKED.findall(cell)


def audit(steps):
    """Return (problems, audited, completeness) for every citation in the repo."""
    subflows = {path.split(".")[0] for path, _ in steps.values()}
    problems, audited = [], 0
    cited_by_file = {}

    for path in _markdown_files():
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        rel = os.path.relpath(path, REPO)
        for lineno, coord, chain in _rows(text):
            # Only rows naming a subflow of the root flow are ours to audit; this
            # is what keeps unrelated tables with their own `N.M` numbering out.
            if not chain or chain[0] not in subflows:
                continue
            audited += 1
            cited_by_file.setdefault(rel, set()).add(coord)
            declared = ".".join(chain)
            if coord not in steps:
                problems.append((rel, lineno, coord, f"no step {coord} in {ROOT_FLOW}"))
                continue
            actual, _task = steps[coord]
            if declared != actual:
                problems.append((rel, lineno, coord,
                                 f"resolves to `{actual}`, row names `{declared}`"))

    granting = {c for c, (_p, task) in steps.items() if task.startswith(GRANTING_PREFIX)}
    completeness = None
    for path in _markdown_files():
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError):
            continue
        if COMPLETENESS_HEADING in text:
            rel = os.path.relpath(path, REPO)
            completeness = (rel, sorted(granting - cited_by_file.get(rel, set()),
                                        key=lambda c: [int(p) for p in c.split(".")]))
            break
    return problems, audited, completeness


def main():
    print(f"Doc build-step citations vs the resolved {ROOT_FLOW} flow")
    print("=" * 116)
    try:
        steps = resolve_flow()
    except Exception as exc:  # noqa: BLE001 — any failure here invalidates the audit
        print(f"  [FAIL] flow resolution: {type(exc).__name__}: {exc}")
        print("         needs CumulusCI on the interpreter running this test — "
              "run it with the CCI venv python, not a bare python3")
        return 1

    problems, audited, completeness = audit(steps)
    inside, root_at = index_flows(steps)
    named_problems, named = audit_named_steps(inside, root_at)

    check("flow_resolved", len(steps) > 0, "resolved flow is empty")

    # A silent zero is the failure mode that matters most here: if row matching
    # ever breaks, an empty problem list looks exactly like success.
    check("found_citations_to_audit", audited > 0,
          "no citation rows matched anywhere — the scan itself is broken, and would "
          "report clean no matter how wrong the docs were")
    check("found_named_step_citations", named > 0,
          "no `<flow> step N` citations matched — that notation outnumbers the "
          "coordinate form ~7:1, so a silent zero here hides most of the surface")

    check("every_citation_resolves_to_the_step_it_names", not problems,
          f"{len(problems)} bad citation(s) of {audited}")
    for rel, lineno, coord, problem in problems:
        print(f"         {rel}:{lineno}  {coord} — {problem}")

    check("every_named_step_exists", not named_problems,
          f"{len(named_problems)} bad citation(s) of {named}")
    for rel, lineno, cite, problem in named_problems:
        print(f"         {rel}:{lineno}  {cite} — {problem}")

    if completeness is None:
        check("completeness_table_found", False,
              f"no file contains {COMPLETENESS_HEADING!r} — direction 2 is not running")
    else:
        rel, missing = completeness
        check("every_granting_step_is_documented", not missing,
              f"{len(missing)} granting step(s) missing from {rel}")
        for coord in missing:
            print(f"         {rel}  missing {coord} — {steps[coord][0]}")

    print("=" * 116)
    print(f"{_passed}/{_total} checks passed  ({audited} coordinate + {named} named "
          f"citations audited, {len(steps)} resolved steps)")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())

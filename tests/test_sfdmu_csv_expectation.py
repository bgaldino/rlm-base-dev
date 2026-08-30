#!/usr/bin/env python3
"""Does `validate_sfdmu_v5_datasets.py` expect a root CSV exactly where one is owed?

The root-CSV check used to fire unconditionally, which made the validator permanently red on
two shapes that correctly have no file at the plan root (`#264-51` / pack 123):

  * `operation: Readonly` — the records are queried from the *target org*, so there is no
    source file to read. The wrong fix is an empty CSV; the right one is not to ask.
  * a per-pass override — the file lives at `objectset_source/object-set-N/<Object>.csv` and
    is validated there. The root path is an *alternative* location, not an extra requirement.

A permanently-red validator is worse than none: it trains readers to ignore the only
automated check this repo has over its data plans, which is how the seven
`mfg-multicurrency` findings survived. So narrowing it is the point — but narrowing a check
is also how a check quietly stops working, and the two gates are only correct while each
stays conditional on its own reason. These cases pin that: an Upsert object with no CSV
*anywhere* must still fail Critical, including when some *other* object has a per-pass file.

Run: `python tests/test_sfdmu_csv_expectation.py` (offline, no org).
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import re
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
VALIDATOR = REPO / "scripts" / "validate_sfdmu_v5_datasets.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("sfdmu_validator", VALIDATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = load_validator()

UPSERT = {"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert", "externalId": "Name"}
READONLY = {"query": "SELECT Id, Name FROM Gadget__c", "operation": "Readonly", "externalId": "Name"}
HEADER = "Id,Name\n1,a\n"


def _write_plan(td, plan_body, root_files=None, per_pass_files=None):
    """Materialize a synthetic plan directory: export.json, root CSVs, and per-pass overrides.

    Every fixture-building helper in this file wrote this same scaffold independently — mkdir,
    write export.json, write `root_files`, write `per_pass_files` under
    `objectset_source/object-set-N/` — which is how three of them (`fix_mode_writes`,
    `fix_mode_proposals`, `verbose_log_lines`) drifted to byte-identical bodies with nothing left
    to distinguish them but the code that runs after the write. `plan_body` is taken as the exact
    already-built `export.json` dict, not built here: callers disagree on that part (`issues()`
    wraps a list of passes in `objectSets`, `raw_issues()` takes the container verbatim to reach
    malformed-container shapes), which is exactly the part that must stay their own.
    """
    plan = pathlib.Path(td) / "plan"
    plan.mkdir()
    (plan / "export.json").write_text(json.dumps(plan_body))
    for name, body in (root_files or {}).items():
        (plan / name).write_text(body)
    for pass_number, files in (per_pass_files or {}).items():
        d = plan / "objectset_source" / f"object-set-{pass_number}"
        d.mkdir(parents=True, exist_ok=True)
        for name, body in files.items():
            (d / name).write_text(body)
    return plan


def issues(passes, root_files=None, per_pass_files=None, severity=None, use_separated_csv_files=None):
    """Validate a synthetic plan and return its issue strings, optionally filtered by severity.

    `passes` is a list of objectSets, each a list of object configs, so a case can put the same
    object in more than one pass — the shape the whole per-pass question turns on.
    `per_pass_files` maps a 1-based pass number to `{filename: body}` under
    `objectset_source/object-set-N/`.
    `use_separated_csv_files`, when not `None`, is written as the plan's top-level
    `useSeparatedCSVFiles` — the flag `Script.js`'s `rawSourceDirectoryPath` gates
    `objectset_source/object-set-N/` substitution on for every pass but the first.

    Synthetic rather than a copy of a real plan: a fixture carved out of one passes or fails for
    reasons the case did not choose, which is how a control ends up vacuous.
    """
    with tempfile.TemporaryDirectory() as td:
        export_data = {"objectSets": [{"objects": p} for p in passes]}
        if use_separated_csv_files is not None:
            export_data["useSeparatedCSVFiles"] = use_separated_csv_files
        plan = _write_plan(td, export_data, root_files, per_pass_files)
        result = V.SFDMUValidator(base_dir=str(plan.parent), verbose=False).validate_dataset(plan)
        return [f"{i.severity.value}/{i.object_name}: {i.message}" for i in result.issues
                if severity is None or i.severity == severity]


def raw_issues(body, root_files=None, per_pass_files=None):
    """Like `issues()`, but takes the whole `export.json` body verbatim.

    `issues()` wraps its argument in a well-formed `objectSets`, which is exactly what the
    malformed-container cases have to bypass: the shapes that aborted the whole run are wrong *at*
    the container level (`"objects": ["SELECT …"]`), so they cannot be expressed through a helper
    that builds the container for you.
    """
    with tempfile.TemporaryDirectory() as td:
        plan = _write_plan(td, body, root_files, per_pass_files)
        result = V.SFDMUValidator(base_dir=str(plan.parent), verbose=False).validate_dataset(plan)
        return [f"{i.severity.value}/{i.object_name}: {i.message}" for i in result.issues]


def method_survives(method_name, *args):
    """True if calling `method_name` on a fresh validator does not raise.

    `raw_issues` cannot exercise this: the shapes it probes are already intercepted, gracefully, by
    `validate_dataset`'s own container-type checks before they would reach a lower-level method — so
    a case that only calls through `validate_dataset` would pass whether or not that lower method
    still has the bug. This calls the method directly instead.
    """
    try:
        getattr(V.SFDMUValidator(base_dir="."), method_name)(*args)
        return True
    except Exception:
        return False


def fix_mode_writes(plan_body, root_files=None, per_pass_files=None, **fix_flags):
    """Run a fix mode over a synthetic plan and return the bytes of every CSV afterwards.

    The repo had no fix-mode coverage at all — nothing referenced `fix_headers` or
    `fix_composite_keys` — so a change to pass resolution could silently start or stop writing to a
    file. That is not hypothetical: normalizing flat plans made `--fix-headers` newly write into
    `objectset_source/object-set-1/` for a plan shape no shipped dataset happens to have, and
    both-bounds stopped it mutating an `object-set-0/` file it used to resolve against the last pass.
    """
    with tempfile.TemporaryDirectory() as td:
        plan = _write_plan(td, plan_body, root_files, per_pass_files)
        # Through `validate_dataset`, which is what the CLI drives — the fix loop runs from there
        # when the flags are set, so this exercises the same path a `--fix-all` run takes.
        V.SFDMUValidator(base_dir=str(plan.parent), verbose=False, **fix_flags).validate_dataset(plan)
        return {p.relative_to(plan).as_posix(): p.read_bytes()
                for p in sorted(plan.rglob("*.csv"))}


def fix_mode_proposals(plan_body, root_files=None, expect=None, per_pass_files=None, **fix_flags):
    """`--dry-run` proposal lines from a fix run — what an operator reads before applying it.

    `fix_mode_writes` cannot see this: a dry run writes nothing, so byte comparison is blind to a
    report that proposes two conflicting headers for one file, or double-counts a column. That is
    exactly what per-declaration iteration produced, because the `_is_csv_empty` /
    `_csv_missing_composite_key` probes that make a real run's second iteration a no-op stay true when
    nothing is written.

    `expect` makes the count assertable. Without it a caller could only test `[1:]` for emptiness,
    which holds when there is one proposal *and* when this probe observes nothing — so renaming the
    log line it greps for, or silencing the proposal, passed. Any stdout probe has that failure mode
    by construction; the fix is to assert the exact count rather than the absence of extras. In
    `expect` mode the return is inverted into the usual no-findings shape — empty on a match, and a
    line naming both numbers on a mismatch — so an over-count *and* a probe that observed nothing both
    fail, and the failure prints which it was.
    """
    with tempfile.TemporaryDirectory() as td:
        plan = _write_plan(td, plan_body, root_files, per_pass_files)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            V.SFDMUValidator(base_dir=str(plan.parent), verbose=True,
                             dry_run=True, **fix_flags).validate_dataset(plan)
        lines = [ln.strip() for ln in buf.getvalue().splitlines() if "Would add" in ln]
    if expect is None:
        return lines
    if len(lines) == expect:
        return []
    return [f"expected exactly {expect} proposal(s), observed {len(lines)}: {lines or 'nothing'}"]


def verbose_log_lines(plan_body, root_files=None, per_pass_files=None, **fix_flags):
    """All verbose-mode stdout lines from a real (non-dry-run) fix run.

    `fix_mode_proposals` is dry-run-only and filters to "Would add" lines, so it is blind to a WARN
    a real run logs on a path `--dry-run` never exercises — the fixer skipping a non-writable
    declaration, say. This is the same capture without either restriction.
    """
    with tempfile.TemporaryDirectory() as td:
        plan = _write_plan(td, plan_body, root_files, per_pass_files)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            V.SFDMUValidator(base_dir=str(plan.parent), verbose=True,
                             **fix_flags).validate_dataset(plan)
        return [ln.strip() for ln in buf.getvalue().splitlines()]


def merged_config_fix_converges(pass1=None):
    """Findings still standing after `--fix-all` on the merged-config shape — empty means converged.

    Report/fix parity, which is not the same property as either half working. The validation half was
    taught to check the root CSV against the passes that *read* it while the fix half kept reading the
    merged config, so with pass 1 `Readonly`/`Name` and pass 2 `Upsert`/`Name;Code` the validator asked
    for a `$$Name$Code` column and the fixer, seeing no `;` in `Name`, wrote nothing. Both halves
    self-consistent, `--fix-all` non-convergent.

    `pass1` defaults to Readonly. The excluded-in-pass-1 shape is a different skip: `fix_dataset_issues`
    used to `continue` on the merged first declaration before the per-reading-config loop, so even
    after the inner loop was taught the reading list, pass 1 `excluded=True` bypassed it entirely.

    Returns findings rather than a bool so a failure prints what survived.
    """
    first = _RO_FIRST if pass1 is None else pass1
    body = {"apiVersion": "68.0", "objectSets": [{"objects": [first]}, {"objects": [_UP_SECOND]}]}
    with tempfile.TemporaryDirectory() as td:
        plan = pathlib.Path(td) / "plan"
        plan.mkdir()
        (plan / "export.json").write_text(json.dumps(body))
        (plan / "Widget__c.csv").write_text("Name,Code\nwidget-a,c1\n")
        before = V.SFDMUValidator(base_dir=str(plan.parent), verbose=False).validate_dataset(plan)
        if not any("composite key column" in i.message for i in before.issues):
            return ["precondition failed: the fixture no longer reports the finding it is fixing"]
        V.SFDMUValidator(base_dir=str(plan.parent), verbose=False,
                         fix_headers=True, fix_composite_keys=True).validate_dataset(plan)
        after = V.SFDMUValidator(base_dir=str(plan.parent), verbose=False).validate_dataset(plan)
        return [f"{i.severity.value}/{i.object_name}: {i.message}" for i in after.issues]


def criticals(objects, root_files=None, per_pass_files=None):
    """Criticals for a single-pass plan — the common case, kept short."""
    return issues([objects], root_files,
                  {1: per_pass_files} if per_pass_files else None,
                  severity=V.Severity.CRITICAL)


def flat_plan(per_pass=None):
    """Criticals for a plan using the flat `objects` key rather than `objectSets`.

    Both older plans and hand-written ones use this shape, and it is the shape the three
    pass-resolving functions disagreed about. `per_pass` is keyed by directory number, so `{0: ...}`
    writes a literal `object-set-0/` — a name that maps to pass_index -1.
    """
    with tempfile.TemporaryDirectory() as td:
        plan = _write_plan(td, {"objects": [UPSERT]}, None, per_pass)
        result = V.SFDMUValidator(base_dir=str(plan.parent), verbose=False).validate_dataset(plan)
        return [f"{i.object_name}: {i.message}" for i in result.issues
                if i.severity == V.Severity.CRITICAL]


CASES = [
    # (label, expect_critical, criticals)
    ("an Upsert object with no CSV anywhere still fails — the finding worth keeping",
     True, criticals([UPSERT])),
    ("an Upsert object with its root CSV present passes — control for the case above",
     False, criticals([UPSERT], {"Widget__c.csv": HEADER})),
    ("a Readonly object with no CSV is silent: it is queried from the target org",
     False, criticals([READONLY])),
    # `_is_live_writable` used to coerce `cfg.get("operation") or "Readonly"` before checking the
    # enum — Python's `0 or "Readonly"` treats numeric Insert (enum index 0) as falsy, silently
    # replacing it with Readonly and exempting its CSV. `_resolve_operation` fixes this by checking
    # for `None` (absent/unresolvable) rather than truthiness.
    ("a numeric Insert operation (enum index 0) with no CSV anywhere still fails — the false "
     "negative `0 or \"Readonly\"` used to produce",
     True, criticals([dict(UPSERT, operation=0)])),
    ("...and with its root CSV present it passes — control for the case above",
     False, criticals([dict(UPSERT, operation=0)], {"Widget__c.csv": HEADER})),
    # SFDMU's `rawSourceDirectoryPath` (Script.ts) returns the plan root whenever `objectSetIndex`
    # is falsy, with no `useSeparatedCSVFiles` escape hatch — pass 1 never reads
    # `objectset_source/object-set-1/`. That directory becomes readable at all only through this
    # repo's opt-in `sync_objectset_source_to_source` step (`tasks/rlm_sfdmu.py:187-205,390-391`),
    # which copies it onto the root before a run — it is not a substitute for the root file. This
    # case used to pin the opposite (silent at the root), which protected the false negative
    # instead of catching it.
    ("an Upsert object supplied only under object-set-1/ still owes its root CSV — pass 1 is "
     "always root-backed, override or not",
     True, criticals([UPSERT], None, {"Widget__c.csv": HEADER})),
    # The gate keys on *this* object having a per-pass file, not on the plan having any. Keyed
    # on the plan, one override would excuse every missing CSV in it.
    #
    # The other object must be one the plan DECLARES in that pass. Written with an undeclared
    # `Unrelated__c`, this passed without ever constructing plan-wide coverage — the override was
    # discarded upstream, so the condition the label refutes never existed, and mutating the gate
    # to key on the plan left the case green.
    #
    # Pass 1 is left empty and both objects moved to pass 2: an object-set-1 override no longer
    # grants coverage at all (see the case above), so a same-pass override for a *different*
    # object has to live in a pass where coverage is possible for this case to isolate anything.
    ("an Upsert object whose per-pass CSV is absent still fails, even though a *different* "
     "object in the same pass has one",
     True, issues([[], [UPSERT, dict(UPSERT, query="SELECT Id, Name FROM Other__c")]], None,
                  {2: {"Other__c.csv": HEADER}}, severity=V.Severity.CRITICAL)),
    # `_parse_object_configs` keeps the first declaration, so a Readonly first pass decides the
    # merged operation. No plan in the repo declares that shape
    # (surveyed: 0 of the 76 export.json files under datasets/sfdmu, a superset of the 39 the
    # validator scans — it skips test/ and *.bak via _SKIP_SEGMENTS), and if one appears the gate
    # would silence a writable pass — so pin it now.
    # Two objectSets, not two entries in one — the label says "pass" and the case has to mean it.
    # Written as a single set, this passed for the wrong reason and left the multi-pass path it
    # advertises untested.
    ("a Readonly first pass followed by an Upsert pass for the same object is NOT silenced",
     True, issues([[READONLY], [dict(UPSERT, query="SELECT Id, Name FROM Gadget__c")]],
                  severity=V.Severity.CRITICAL)),
    # Same merged-config trap, different key: `excluded` is also read from the first declaration.
    ("an object excluded in pass 1 but Upsert in pass 2, with no CSV, still fails",
     True, issues([[dict(UPSERT, excluded=True)], [UPSERT]], severity=V.Severity.CRITICAL)),
    # The converse, and the direction a surviving mutation showed was unpinned: dropping the
    # `excluded` skip in _writable_passes_by_object makes pass 3 count as writable, so the pass-2
    # override no longer covers every writable pass and a spurious Critical appears.
    #
    # Pass 1 here is a filler `excluded` declaration, and the writable/covered pass is pushed to
    # pass 2: an object-set-1 override cannot demonstrate "owes nothing" any more (pass 1 is
    # always root-backed — see the CASES above), so proving a covered writable pass stays silent
    # needs a pass index of 1 or higher. `useSeparatedCSVFiles: true` is required alongside it —
    # see the USE_SEPARATED_CSV_FILES cases below — so every case in this file demonstrating a
    # pass 2+ override as real coverage sets it explicitly rather than relying on the flag's
    # absence being harmless.
    ("an object excluded in pass 1, Upsert in pass 2 with an override, owes nothing",
     False, issues([[dict(UPSERT, excluded=True)], [UPSERT]], None,
                   {2: {"Widget__c.csv": HEADER}}, severity=V.Severity.CRITICAL,
                   use_separated_csv_files=True)),
    # A flat `objects` plan (no objectSets) with per-pass CSVs: three functions disagreed about
    # normalizing that shape, so the CSVs were silently discarded behind a WARN suppressed at
    # default verbosity. And `object-set-0` maps to pass_index -1, which an upper-bound-only check
    # let through into a negative index — an IndexError aborting the whole run rather than
    # reporting the one bad plan.
    #
    # A flat plan normalizes to exactly one pass (pass 1), so this shape can never use a pass 2+
    # override — object-set-1/ is the only directory a flat plan could ever have, and it never
    # grants coverage. Was pinned as silent; fixed to match `criticals()`'s case above.
    ("a flat objects-key plan's object-set-1 CSV does not relieve the root requirement",
     True, flat_plan(per_pass={1: {"Widget__c.csv": HEADER}})),
    ("a flat objects-key plan with an object-set-0 directory does not treat it as coverage",
     True, flat_plan(per_pass={0: {"Widget__c.csv": HEADER}})),
    # A malformed plan must be reported, not crash the run — `.lower()` on a non-string aborts
    # every plan after it, which converts one bad plan into no validation at all.
    ("a non-string operation does not abort the run",
     False, issues([[{"query": "SELECT Id FROM Widget__c", "operation": True, "externalId": "Name"}]],
                   {"Widget__c.csv": HEADER}, severity=V.Severity.CRITICAL)),

    # ---- the shape that shipped broken, and the reason it shipped: nothing modelled a writable
    # pass with no override. This is `BillingPolicy` in qb/en-US/qb-billing (Upsert in pass 1,
    # Update in pass 3, override only for pass 3) and 15 other objects across 7 scanned plans — 11 of
    # them in the 5 plans cumulusci.yml wires.
    # Keyed on the object name, pass 1's root CSV stops being checked and the plan reports PASS
    # with it deleted — verified against the real plan, not only here.
    ("an object writable in two passes with an override for only ONE still owes its root CSV",
     True, issues([[UPSERT], [dict(UPSERT, operation="Update")]], None,
                  {2: {"Widget__c.csv": HEADER}}, severity=V.Severity.CRITICAL)),
    # A third, filler `excluded` pass 1 pushes both writable passes to indices 1 and 2 (object-set
    # directories 2 and 3): pass 1's own override can never grant coverage (see above), so proving
    # "silent once EVERY writable pass is covered" needs both real writable passes at index >= 1.
    ("...and is silent once EVERY writable pass is supplied per-pass",
     False, issues([[dict(UPSERT, excluded=True)], [UPSERT], [dict(UPSERT, operation="Update")]],
                   None, {2: {"Widget__c.csv": HEADER}, 3: {"Widget__c.csv": HEADER}},
                   severity=V.Severity.CRITICAL, use_separated_csv_files=True)),
    # Relabelled to what it proves. It previously claimed to pin a filter against misfiled
    # overrides; it passed on pass arithmetic alone and the filter turned out to be inert — a
    # coverage index cancels only its own pass, which is the property below and the reason no
    # filter is needed.
    ("a coverage index cancels only its own pass, so an override for a pass that does not declare "
     "the object leaves the declaring pass owing its root CSV",
     True, issues([[READONLY], [UPSERT]], None, {1: {"Widget__c.csv": HEADER}},
                  severity=V.Severity.CRITICAL)),
]

# `Script.js`'s `rawSourceDirectoryPath` substitutes `objectset_source/object-set-N/` (N > 1) only
# when the plan's top-level `useSeparatedCSVFiles` is `true`; otherwise every pass — pass 1
# included — reads the plan root regardless of what that directory holds. Crediting a pass-2+
# override as coverage without checking the flag let a plan with only
# `objectset_source/object-set-2/<Object>.csv` and no root CSV report clean while SFDMU, unable to
# find the flag, still reads (and fails to find) the root file at runtime — a false negative on
# the one finding (missing root CSV) this file exists to keep real. #264-review.
#
# Filler `excluded` pass 1 pushes both writable passes to indices 1 and 2 (object-set directories
# 2 and 3), same as the MERGED_CONFIG case this mirrors: pass 1's own override can never grant
# coverage regardless of the flag, so isolating what the flag controls needs both real writable
# passes at index >= 1.
_EXCLUDED_FILLER = dict(UPSERT, excluded=True)
_TWO_WRITABLE_PASSES_COVERED = [[_EXCLUDED_FILLER], [UPSERT], [dict(UPSERT, operation="Update")]]
_BOTH_OVERRIDES = {2: {"Widget__c.csv": HEADER}, 3: {"Widget__c.csv": HEADER}}

USE_SEPARATED_CSV_FILES = [
    ("pass-2/3 overrides with no `useSeparatedCSVFiles` key do not relieve the root requirement "
     "— SFDMU still reads the root for every pass without the flag",
     True, issues(_TWO_WRITABLE_PASSES_COVERED, None, _BOTH_OVERRIDES,
                  severity=V.Severity.CRITICAL)),
    ("...and neither does `useSeparatedCSVFiles: false` — explicit-false and absent must agree",
     True, issues(_TWO_WRITABLE_PASSES_COVERED, None, _BOTH_OVERRIDES,
                  severity=V.Severity.CRITICAL, use_separated_csv_files=False)),
    ("...and `useSeparatedCSVFiles: true` is what actually relieves it — control for both cases "
     "above",
     False, issues(_TWO_WRITABLE_PASSES_COVERED, None, _BOTH_OVERRIDES,
                   severity=V.Severity.CRITICAL, use_separated_csv_files=True)),
    # The same gate applies to *content* validation, not just coverage credit: a pass-2+ override
    # SFDMU never reads without the flag is inert, so validating what's in it reported a finding
    # (here, an empty file) against a file nothing loads.
    ("an empty pass-2 override's content is not validated when useSeparatedCSVFiles is not set "
     "— SFDMU never reads that file",
     False, [i for i in issues([[UPSERT], [dict(UPSERT, operation="Update")]],
                               {"Widget__c.csv": HEADER}, {2: {"Widget__c.csv": ""}})
            if "empty" in i.lower()]),
    ("...and IS validated once useSeparatedCSVFiles is true — control for the case above",
     True, [i for i in issues([[UPSERT], [dict(UPSERT, operation="Update")]],
                              {"Widget__c.csv": HEADER}, {2: {"Widget__c.csv": ""}},
                              use_separated_csv_files=True)
            if "empty" in i.lower()]),
]

# `useSeparatedCSVFiles` used to be read with plain `bool()`, not `_is_js_truthy` — the same
# Python/JS container-truthiness mismatch already fixed for `excluded`. `[]`/`{}` are JS-truthy
# (SFDMU reads the override) but Python-falsy, so `bool()` denied override coverage credit and
# produced a false missing-root-CSV Critical for a plan SFDMU runs correctly.
USE_SEPARATED_CSV_FILES_JS_TRUTHINESS = [
    ("`useSeparatedCSVFiles: []` relieves the root requirement like `true` does — SFDMU reads "
     "the flag with JS truthiness, not Python's",
     False, issues(_TWO_WRITABLE_PASSES_COVERED, None, _BOTH_OVERRIDES,
                   severity=V.Severity.CRITICAL, use_separated_csv_files=[])),
    ("...same for `useSeparatedCSVFiles: {}`",
     False, issues(_TWO_WRITABLE_PASSES_COVERED, None, _BOTH_OVERRIDES,
                   severity=V.Severity.CRITICAL, use_separated_csv_files={})),
]

# What SFDMU can actually resolve, which is not what the first version of this check assumed.
# `ScriptLoader._resolveOperation` trims and case-folds; `ScriptObject.getOperation` does neither,
# and reading the wrong one made the repo's nine `"ReadOnly"` declarations look like defects. These
# cases pin the rule to the loader, so the next reader cannot re-derive it from the other function.
OPERATION_RESOLUTION = [
    ("a case variant SFDMU resolves is accepted — 'ReadOnly' appears 9 times in this repo",
     False, [i for i in issues([[dict(READONLY, operation="ReadOnly")]], {"Gadget__c.csv": HEADER})
             if "resolve" in i]),
    ("...and so is a whitespace-padded value, which the loader trims",
     False, [i for i in issues([[dict(READONLY, operation=" Readonly ")]], {"Gadget__c.csv": HEADER})
             if "resolve" in i]),
    ("a word outside the enum is reported: SFDMU can't resolve it, and (verified against the "
     "installed source) does NOT reset the object to Readonly either — the raw value stays",
     True, [i for i in issues([[dict(UPSERT, operation="Upser")]], {"Widget__c.csv": HEADER})
            if "resolve" in i]),
    ("a non-string is reported rather than crashing the run",
     True, [i for i in issues([[dict(UPSERT, operation=True)]], {"Widget__c.csv": HEADER})
            if "resolve" in i]),
    ("an absent operation is legal — SFDMU applies its own default",
     False, [i for i in issues([[{"query": "SELECT Id, Name FROM Widget__c", "externalId": "Name"}]],
                               {"Widget__c.csv": HEADER}) if "resolve" in i]),
    # `ScriptLoader._resolveOperation` also resolves numeric enum indices (`OPERATION[value]`),
    # not just strings — the gap both Copilot review threads on PR #397 flagged. 2 is Upsert.
    ("a numeric operation SFDMU resolves is accepted — 2 is Upsert",
     False, [i for i in issues([[dict(UPSERT, operation=2)]], {"Widget__c.csv": HEADER})
             if "resolve" in i]),
    ("an out-of-range numeric operation is reported: there is no enum member at that index",
     True, [i for i in issues([[dict(UPSERT, operation=99)]], {"Widget__c.csv": HEADER})
            if "resolve" in i]),
    # TypeScript numeric enums are bidirectional at runtime, so SFDMU's own `_resolveOperation`
    # commits index 8 and the string "Unknown" to the same value 8, unlike "Upser"/99 above, which
    # fail resolution outright — confirmed by reading the installed sfdmu@5.8.0 source directly.
    # Still reported here (it is not a real operation a plan should declare), but as its own case,
    # not lumped in with a value that never resolves at all.
    ("numeric 8 (Unknown, the enum's own fallback) is reported — SFDMU resolves and commits it, "
     "it just isn't a real operation",
     True, [i for i in issues([[dict(UPSERT, operation=8)]], {"Widget__c.csv": HEADER})
            if "resolve" in i]),
    ("...and so is the string \"Unknown\", which SFDMU resolves to the same committed value 8",
     True, [i for i in issues([[dict(UPSERT, operation="Unknown")]], {"Widget__c.csv": HEADER})
            if "resolve" in i]),
    ("a Boolean is reported even though False == 0 in Python — JS typeof false is 'boolean', so "
     "the loader drops it rather than reading it as numeric Insert",
     True, [i for i in issues([[dict(UPSERT, operation=False)]], {"Widget__c.csv": HEADER})
            if "resolve" in i]),
    # `json.load` decodes a bare `2.0` literal as Python `float`, but JS has one numeric type —
    # `OPERATION[2.0]` is the same lookup as `OPERATION[2]` and resolves to Upsert. Rejecting the
    # float here would report a valid plan's operation as unresolvable.
    ("an integral float operation SFDMU resolves the same as its int is accepted — 2.0 is Upsert",
     False, [i for i in issues([[dict(UPSERT, operation=2.0)]], {"Widget__c.csv": HEADER})
             if "resolve" in i]),
    ("a non-integral float is reported: OPERATION[2.5] is undefined in SFDMU too",
     True, [i for i in issues([[dict(UPSERT, operation=2.5)]], {"Widget__c.csv": HEADER})
            if "resolve" in i]),
]

# `_validate_external_id` reads `operation` a second time to decide whether to skip the
# nested-path/SELECT-coverage checks for Insert mode. A raw `str(op or "Readonly")` there bypassed
# `_resolve_operation` entirely, so numeric Insert (index 0) was coerced to Readonly by Python's
# `0 or "Readonly"` and wrongly received checks string Insert correctly skips.
NUMERIC_OPERATION_GATING = [
    ("a numeric Insert operation (0) skips the nested-relationship-path check, same as string "
     "Insert — the false positive `0 or \"Readonly\"` used to produce",
     False, [i for i in issues([[dict(UPSERT, operation=0, externalId="A.B.C")]],
                                {"Widget__c.csv": HEADER})
             if "nested relationship path" in i]),
    ("...and a numeric Upsert (2) with the same nested path IS flagged — control proving the "
     "skip above is operation-gated, not a blanket exemption",
     True, [i for i in issues([[dict(UPSERT, operation=2, externalId="A.B.C")]],
                               {"Widget__c.csv": HEADER})
            if "nested relationship path" in i]),
    # A prior round of this PR treated a resolved-but-"unknown" operation (index 8 / the string
    # "Unknown") — and a genuinely-unresolvable one (typo/Boolean/out-of-range) — as not-writable,
    # on the theory that SFDMU resets an unresolved `operation` to its Readonly class default.
    # Verified against the installed sfdmu@5.8.0 source that this is wrong: that Readonly default
    # only survives when the `operation` *key* is absent. When it's present but invalid,
    # `plainToInstance` commits the raw value onto `ScriptObject.operation` before
    # `_resolveOperation` ever runs, and a failed resolve just skips the later overwrite — so the
    # raw invalid value (or, for index 8/"Unknown", the committed value 8) stays there. Neither
    # value is `===` Readonly(3) or Delete(4), the only two `MigrationJobTask.updateRecordsAsync`
    # checks before skipping a declaration, so both fall through to the same insert/update/upsert
    # dispatch a real writable operation gets — SFDMU *will* try to write the object from source.
    # Not demanding a CSV for it was the false negative; found by Copilot (comment 3888828061),
    # generalized here past the literal wording nit it raised.
    ("an object declared operation \"Unknown\" with no CSV anywhere IS flagged missing-CSV "
     "Critical — SFDMU commits the value, but the object still falls through to the "
     "insert/update/upsert write path with no real operation behind it",
     True, issues([[dict(UPSERT, operation="Unknown")]], severity=V.Severity.CRITICAL)),
    ("...and so is a completely unresolvable operation (a typo) with no CSV anywhere — the raw "
     "invalid value is retained on the object rather than reset to Readonly, so it is writable too",
     True, issues([[dict(UPSERT, operation="Upser")]], severity=V.Severity.CRITICAL)),
    ("...and an explicit `operation: null` with no CSV anywhere — same mechanism, the null value "
     "itself is committed and never reset",
     True, issues([[dict(UPSERT, operation=None)]], severity=V.Severity.CRITICAL)),
    ("...control — the same object declared plain Upsert with no CSV IS flagged Critical",
     True, issues([[UPSERT]], severity=V.Severity.CRITICAL)),
    ("...and the control the other direction still holds — a real Readonly declaration with no "
     "CSV is NOT flagged Critical, since Readonly really does hit the write-dispatch skip",
     False, issues([[READONLY]], severity=V.Severity.CRITICAL)),
]

# Fix modes had zero coverage anywhere in the repo, which is how a pass-resolution change could
# start or stop writing to a file with nothing to notice.
FIX_MODES = [
    ("--fix-headers writes a header into a flat plan's object-set-1 CSV, a file the pre-normalization "
     "version left untouched",
     True, [n for n, b in fix_mode_writes(
         {"apiVersion": "68.0", "objects": [UPSERT]}, {"Widget__c.csv": HEADER},
         {1: {"Widget__c.csv": ""}}, fix_headers=True).items()
         if n.endswith("object-set-1/Widget__c.csv") and b.strip()]),
    ("--fix-headers does NOT write into an object-set-0 directory, which maps to no pass and which "
     "an upper-bound-only check resolved against the last one",
     False, [n for n, b in fix_mode_writes(
         {"objectSets": [{"objects": [UPSERT]}, {"objects": [UPSERT]}]}, {"Widget__c.csv": HEADER},
         {0: {"Widget__c.csv": ""}}, fix_headers=True).items()
         if "object-set-0" in n and b.strip()]),
    ("--dry-run writes nothing",
     False, [n for n, b in fix_mode_writes(
         {"objectSets": [{"objects": [UPSERT]}]}, {"Widget__c.csv": ""}, None,
         fix_headers=True, dry_run=True).items() if b.strip()]),
    # The positive the case above needs. On its own, "--dry-run writes nothing" also passes when the
    # root-CSV fixer stops running at all — stubbing `fix_dataset_issues` to return `(0, 0)` left it
    # green — because its fixture has only a root CSV and it cannot tell "dry_run honored" from
    # "nothing attempted". The one other positive in this group exercises the *per-pass* fix loop, so
    # `fix_dataset_issues`, the root-CSV writer, had no positive coverage anywhere.
    ("--fix-headers writes a header into an empty ROOT CSV, so the root-CSV fixer has a positive",
     True, [n for n, b in fix_mode_writes(
         {"objectSets": [{"objects": [UPSERT]}]}, {"Widget__c.csv": ""}, None,
         fix_headers=True).items() if n == "Widget__c.csv" and b.strip()]),
    # The directory that maps to no pass is now a finding, not just a WARN suppressed at default
    # verbosity — before this, a mistyped name meant every CSV under it was silently never read.
    ("an object-set-0 directory is REPORTED, so a mistyped directory name is not invisible",
     True, [i for i in issues([[UPSERT]], {"Widget__c.csv": HEADER}, {0: {"Widget__c.csv": HEADER}})
            if "maps to no pass" in i]),
    # `re.match` alone accepts `object-set-1-backup` as a match on the `object-set-1` prefix (no
    # end anchor), which would have credited a stray directory as covering pass 1. Fullmatch fixes
    # that; this pins the report and, separately below, that the root Critical it would have
    # suppressed still fires.
    ("a non-canonical object-set-1-backup directory is REPORTED, not silently matched as object-set-1",
     True, [i for i in issues([[UPSERT]], None, {"1-backup": {"Widget__c.csv": HEADER}})
            if "not a canonical object-set-N directory" in i]),
    ("a non-canonical object-set-1-backup directory does NOT suppress the root-CSV Critical it "
     "would otherwise satisfy",
     True, [i for i in issues([[UPSERT]], None, {"1-backup": {"Widget__c.csv": HEADER}},
                               severity=V.Severity.CRITICAL) if "Widget__c" in i]),
    # `\d+` alone accepts a leading zero (`object-set-01`), a name the runtime sync in
    # `tasks/rlm_sfdmu.py` also does not special-case — it string-compares against the literal
    # `object-set-1`. `[1-9]\d*` rejects it the same way it rejects the `-backup` suffix above.
    ("a non-canonical object-set-01 directory (leading zero) is REPORTED, not treated as pass 1",
     True, [i for i in issues([[UPSERT]], None, {"01": {"Widget__c.csv": HEADER}})
            if "not a canonical object-set-N directory" in i]),
    # `writerow([])` emits only a line terminator, so an empty `fields` list left the file empty by
    # `_is_csv_empty` while returning True. Harmless while the next declaration re-fixed it; a real
    # regression once `header_written` trusted that return value, which suppressed a later pass's
    # correct header and left `b"\r\n"` on disk — a file SFDMU cannot read where a usable one had
    # been. Pass 1 here has no SELECT list, so only pass 2 can supply the header.
    ("--fix-headers takes the header from a later pass when the first has no SELECT fields",
     True, [n for n, b in fix_mode_writes(
         {"apiVersion": "68.0", "objectSets": [
             {"objects": [{"query": " FROM Widget__c", "operation": "Upsert", "externalId": "Name"}]},
             {"objects": [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
                           "externalId": "Name"}]}]},
         {"Widget__c.csv": ""}, fix_headers=True).items()
         if n == "Widget__c.csv" and b.strip() == b"Id,Name"]),
    # The case above has pass 1 contribute NOTHING, so "later wins" and "union of all" cannot be
    # told apart. Here pass 1 selects real fields of its own (`Id,Name`), so a header built from
    # its fields alone is non-empty and looks fixed — until pass 2's composite `externalId:
    # Name;Code` tries to add its `$$Name$Code` column and finds `Code` missing, leaving that
    # High standing after a `--fix-all` that reported success. Only the union of both declarations'
    # fields carries `Code` into the header at all.
    ("--fix-headers unions an empty ROOT CSV's header across every reading pass, not just the "
     "first that has fields, so a later pass's composite externalId is not stranded",
     True, [n for n, b in fix_mode_writes(
         {"apiVersion": "68.0", "objectSets": [
             {"objects": [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
                           "externalId": "Name"}]},
             {"objects": [{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
                           "externalId": "Name;Code"}]}]},
         {"Widget__c.csv": ""}, fix_headers=True, fix_composite_keys=True).items()
         if n == "Widget__c.csv" and b.strip() == b"$$Name$Code,Id,Name,Code"]),
    # Same shape, but the two declarations sit in ONE pass and the CSV lives under
    # `objectset_source/object-set-1/` — the per-pass fixer's own header-write loop, a separate
    # code path from the root fixer above and the one the two Copilot comments cited by line.
    ("--fix-headers unions an empty PER-PASS CSV's header across every writable declaration in "
     "that pass, not just the first",
     True, [n for n, b in fix_mode_writes(
         {"apiVersion": "68.0", "objectSets": [
             {"objects": [
                 {"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert", "externalId": "Name"},
                 {"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
                  "externalId": "Name;Code"},
             ]}]},
         {"Widget__c.csv": "Id,Name\n"}, {1: {"Widget__c.csv": ""}},
         fix_headers=True, fix_composite_keys=True).items()
         if n.endswith("object-set-1/Widget__c.csv") and b.strip() == b"$$Name$Code,Id,Name,Code"]),
    # Hoisting the header write out of the per-declaration loop (the fix above) moved it outside
    # the `for obj_config in writable_cfgs` loop too, so it now runs even when `writable_cfgs` is
    # empty — a misfiled override: a per-pass CSV exists for an object that is Readonly in that
    # pass. `_union_fields([])` is `[]`, and `_fix_empty_csv_header` logs a "no SELECT fields to
    # write" WARN for that, which is new noise on a case the diff had no reason to touch. Guarded
    # on `writable_cfgs` being non-empty, same as the root fixer's pre-existing `if not reading:
    # continue`.
    ("--fix-headers does not touch (or warn about) a per-pass CSV override for an object that "
     "is Readonly in that pass",
     False, [ln for ln in verbose_log_lines(
         {"apiVersion": "68.0", "objectSets": [
             {"objects": [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Readonly",
                           "externalId": "Name"}]}]},
         per_pass_files={1: {"Widget__c.csv": ""}}, fix_headers=True,
     ) if "no SELECT fields" in ln or "Cannot add header" in ln]),
    # The same useSeparatedCSVFiles gate applies to the per-pass FIXER, not just the validator:
    # writing a header into a pass-2+ override SFDMU never reads is a fix nothing reads either.
    ("--fix-headers does not write into a pass-2 override when useSeparatedCSVFiles is not set",
     False, [n for n, b in fix_mode_writes(
         {"apiVersion": "68.0", "objectSets": [
             {"objects": [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
                           "externalId": "Name"}]},
             {"objects": [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Update",
                           "externalId": "Name"}]}]},
         {"Widget__c.csv": HEADER}, {2: {"Widget__c.csv": ""}}, fix_headers=True).items()
         if n.endswith("object-set-2/Widget__c.csv") and b.strip()]),
    ("...and DOES write into it once useSeparatedCSVFiles is true — control for the case above",
     True, [n for n, b in fix_mode_writes(
         {"apiVersion": "68.0", "useSeparatedCSVFiles": True, "objectSets": [
             {"objects": [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
                           "externalId": "Name"}]},
             {"objects": [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Update",
                           "externalId": "Name"}]}]},
         {"Widget__c.csv": HEADER}, {2: {"Widget__c.csv": ""}}, fix_headers=True).items()
         if n.endswith("object-set-2/Widget__c.csv") and b.strip()]),
]

# Pins the premise the exemption rests on: that a per-pass CSV is actually validated where it
# lives. Deleting per-pass validation outright left the six cases above green, because they only
# assert on the *root* check — the exemption would have degraded to a blanket pass in silence.
PER_PASS_IS_VALIDATED = [
    ("an EMPTY per-pass CSV is reported, so the exemption rests on real validation and not on "
     "the file merely existing",
     True, [i for i in issues([[UPSERT]], None, {1: {"Widget__c.csv": ""}})
            if "empty" in i.lower()]),
    # `object-set-0` maps to pass_index -1. An upper-bound-only check (`pass_index >= len`) admits
    # it, and the negative index then resolves to the LAST pass — so a misnamed directory is
    # silently attributed to a real pass, and the per-pass loop reports the object as missing from
    # "pass 0". Pinning the absence of that phantom report is the only externally visible
    # difference the bounds fix makes, now that normalizing flat plans removed the IndexError it
    # also used to cause. A directory that maps to no pass is a separate, now-fixed gap — see "an
    # object-set-0 directory is REPORTED" above, which pins the High finding
    # `_find_objectset_source_overrides` reports for it.
    ("an object-set-0 directory is not silently attributed to the last pass",
     False, [i for i in issues([[UPSERT]], {"Widget__c.csv": HEADER}, {0: {"Widget__c.csv": HEADER}})
             if "no matching object" in i]),
    # The positive that negative needs. Nothing required the `no matching object` message to fire, so
    # renaming it left the case above green — a control that cannot distinguish "correctly silent" from
    # "the check is gone". Here the object is declared only in pass 1 while an override sits in
    # `object-set-2`, which is the misfiled-override shape that message exists to report.
    ("a misfiled override — a CSV in a pass that does not declare the object — is reported",
     True, [i for i in issues([[UPSERT], [{"query": "SELECT Id, Name FROM Other__c",
                                           "operation": "Upsert", "externalId": "Name"}]],
                              {"Widget__c.csv": HEADER, "Other__c.csv": HEADER},
                              {2: {"Widget__c.csv": HEADER}})
            if "no matching object" in i]),
    # Severity, not just presence. The empty-CSV case above filters on the message alone, so demoting
    # every empty CSV from Critical to High — `if obj_name in self.KNOWN_EMPTY_CSV_OBJECTS:` → `if
    # True:` — left it green, and the live baseline cannot see it either because the 7 mfg findings are
    # already High. `Widget__c` is not a known-empty object, so its empty CSV must be Critical.
    ("an empty CSV for an object NOT on the known-empty list is Critical, not merely reported",
     True, [i for i in issues([[UPSERT]], {"Widget__c.csv": ""})
            if i.startswith("Critical/") and "empty" in i.lower()]),
]


"""Same object, `Readonly` in pass 1 and `Upsert` with a composite key in pass 2."""
_RO_FIRST = {"query": "SELECT Id, Name FROM Widget__c", "operation": "Readonly", "externalId": "Name"}
_UP_SECOND = {"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
              "externalId": "Name;Code"}
_EX_FIRST = {"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
             "externalId": "Name", "excluded": True}

MERGED_CONFIG = [
    # `_parse_object_configs` keeps an object's FIRST declaration, so every check reading the merged
    # config validated pass 1 and exempted passes 2..n. The root file is read by pass 2 here, whose
    # composite key needs a `$$Name$Code` column; against pass 1's config a CSV carrying only `Name`
    # passed. This is the third instance of the same trap in this file (`operation` and `excluded`
    # were the first two), which is why the per-pass view is now a primitive.
    ("a pass-2 composite key is required of the root CSV, not just pass 1's simple key",
     True, [i for i in issues([[_RO_FIRST], [_UP_SECOND]], {"Widget__c.csv": "Name\nwidget-a\n"})
            if "composite key column" in i]),
    # `apiVersion` is filtered rather than supplied: `issues()` writes a minimal plan without one, so
    # an unfiltered control asserts "no findings at all" and fails on an unrelated High — a control
    # that passes for the wrong reason in one direction and fails for the wrong reason in the other.
    ("...and is silent when that column is present — control for the case above",
     False, [i for i in issues([[_RO_FIRST], [_UP_SECOND]],
                               {"Widget__c.csv": "$$Name$Code,Name,Code\nwidget-a;c1,widget-a,c1\n"})
             if "apiVersion" not in i]),
    # A `Readonly` declaration reads no *file*, but it still executes its own SOQL against the target
    # org in every pass, so its externalId fields still have to be in that pass's SELECT clause — a
    # requirement that has nothing to do with whether the object owes a root CSV. Scoping the
    # SELECT-coverage sweep to `objects_owing_root_csv` used to exempt this Readonly pass the moment
    # its Upsert sibling made the object CSV-covered; adding a writable sibling pass must not silence
    # an unrelated defect in this one. Pass 2 selects neither `Name` nor `Code`.
    ("a Readonly later pass's own narrow SELECT is still checked against its externalId",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Code"}],
          [{"query": "SELECT Id FROM Widget__c", "operation": "Readonly", "externalId": "Name;Code"}]],
         {"Widget__c.csv": "$$Name$Code,Name,Code\nwidget-a;c1,widget-a,c1\n"})
         if "not found in query SELECT clause" in i]),
    # `obj_config` in `_validate_object` is the merged (first-declaration) config, so `excluded` there
    # means "excluded in the first pass that declared it", not "excluded everywhere". The early return
    # gating on that flag used to sit BEFORE the SELECT-coverage loop, so an object excluded in pass 1
    # and genuinely live (Readonly, owing no root CSV) in pass 2 returned before pass 2's own SELECT
    # gap was ever checked — regardless of root-CSV coverage, since the early return's own
    # `obj_name not in objects_owing_root_csv` half is already true for a Readonly-only object. Pass 2
    # selects neither `Name` nor `Code`.
    ("a live later pass's own narrow SELECT is checked even when the first (merged) declaration is "
     "excluded",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
            "externalId": "Name", "excluded": True}],
          [{"query": "SELECT Id FROM Widget__c", "operation": "Readonly",
            "externalId": "Name;Code"}]])
         if "not found in query SELECT clause" in i]),
    # The inverse ordering of the case above: a Readonly *first* pass with a narrow SELECT, followed by
    # a writable pass fully supplied under `objectset_source/`. The object is then absent from
    # `objects_owing_root_csv` (nothing reads the root) — which used to mean nothing validated pass 1's
    # own SELECT either, even though pass 1 still runs that SOQL every time regardless of what a later
    # pass does or where its CSV lives. Pass 1 selects `Name` but not `Code`.
    ("a Readonly first pass's own narrow SELECT is checked even when a later pass is fully covered "
     "by an override",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Readonly",
            "externalId": "Name;Code"}],
          [{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Code"}]],
         None, {2: {"Widget__c.csv": "$$Name$Code,Name,Code\nwidget-a;c1,widget-a,c1\n"}})
         if "not found in query SELECT clause" in i]),
    # And the reason a raw declaration cannot be substituted for a normalized one: the checks read
    # derived keys (`fields`, the parsed SELECT), not the raw JSON. Passing raw declarations made
    # `fields` empty and every externalId component read as absent — 252 High on the live tree against
    # 7, which is the real mechanism behind the flood earlier notes misattributed to pass scoping.
    # Asserts the parsed *value*, not the key's presence: a raw declaration has no `fields` key at
    # all, so a presence check passes for a normalized config carrying an empty list — which is
    # exactly the broken state — and the case would read green while proving nothing.
    ("per-pass configs carry `fields` parsed from the SELECT, not an empty or absent one",
     True, [c for c in [V.SFDMUValidator(base_dir=".")._all_pass_configs(
         {"objectSets": [{"objects": [_UP_SECOND]}]})["Widget__c"][0][0]]
         if set(c.get("fields") or []) >= {"Name", "Code"}]),
    # One `objectSet` may declare the same object twice. Indexing per-pass configs by pass number
    # made the second declaration overwrite the first, so the merged view kept the first and the
    # per-pass view kept the LAST — and a defect in the overwritten declaration went silent. Here the
    # Upsert declaration (whose composite key the CSV does not satisfy) comes first and a Readonly
    # one second, so a last-wins collection reports nothing.
    ("a defect in the first of two same-pass declarations is still reported",
     True, [i for i in issues(
         [[_UP_SECOND, {"query": "SELECT Id FROM Widget__c", "operation": "Readonly",
                        "externalId": "Id"}]],
         {"Widget__c.csv": "Name,Code\nwidget-a,c1\n"})
         if "composite key column" in i]),
    # Same pass, not just a later one: a Readonly sibling still runs its own SOQL, so sharing a pass
    # with a covered Upsert declaration does not exempt it either. The Upsert sibling here selects
    # everything it keys on, so both findings below are attributable to the Readonly one.
    ("a Readonly declaration's own narrow SELECT is checked even when it shares a pass with a "
     "covered Upsert sibling",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Code"},
           {"query": "SELECT Id FROM Widget__c", "operation": "Readonly",
            "externalId": "Name;Code"}]],
         {"Widget__c.csv": "$$Name$Code,Name,Code\nwidget-a;c1,widget-a,c1\n"})
         if "not found in query SELECT clause" in i]),
    # Per-pass overrides still resolved the *first* declaration in the pass. Readonly/simple-key
    # first, writable composite second: the override was accepted without the required column.
    ("a per-pass override is checked against every writable declaration in the pass, not the first",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Readonly", "externalId": "Name"},
           _UP_SECOND]],
         None, {1: {"Widget__c.csv": "Name,Code\nwidget-a,c1\n"}})
         if "composite key column" in i]),
    # Deduping the reading list on a key narrower than one of its consumers reads truncates the list
    # before that consumer runs, and a dedup can only remove, never restore. Keying it on the CSV
    # check's fields — which exclude the parsed SELECT — dropped later passes before the externalId
    # SELECT-coverage check saw them: 96 lost findings across a 59,400-plan sweep, and a downstream
    # re-dedup on a wider key could not bring them back. Here pass 2 upserts on `Name;Code` while
    # selecting only `Name`, so its coverage gap is reportable only if pass 2 survives dedup.
    # Deliberately NOT a multiplicity assertion: the earlier version of this case asserted "reported
    # once, not twice", which two independent mechanisms could each satisfy alone, so it could not
    # detect a regression in either — which is how the truncation above shipped.
    ("a later pass's SELECT coverage is checked, not dropped by dedup on a narrower key",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Code"}],
          [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Code"}]],
         {"Widget__c.csv": "$$Name$Code,Name,Code\nwidget-a;c1,widget-a,c1\n"})
         if "'Code' not found in query SELECT clause" in i]),
    # A one-level `tuple()` in the dedup key left a list-of-list unhashable, so one malformed plan
    # raised TypeError out of main() and killed the whole 39-plan run with no report — the failure the
    # str() coercions elsewhere in the file exist to prevent. Asserts the malformed plan is *reported*.
    ("a nested-list config value is reported, not raised as TypeError over the whole run",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": [["x"]], "externalId": "Name"}]],
         {"Widget__c.csv": "Id,Name\n1,a\n"})
         if "operation" in i]),
    # Coercing externalId to str stops four downstream `.split(";")` sites aborting the whole run, but
    # the coerced repr matches no gate, so coercion alone traded a crash for silence — the plan reported
    # nothing. Both halves need pinning: dropping the `str()` reintroduces the crash, dropping the
    # report reintroduces the silence, and neither was detectable before.
    ("a non-string externalId is reported rather than silently accepted or raised",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
            "externalId": ["Name", "Code"]}]],
         {"Widget__c.csv": "Id,Name\n1,a\n"})
         if "externalId is not a string" in i]),
    # The malformed-value guards protect *values*; these shapes are wrong at the *container* level and
    # survived every one of them, aborting `main()` and losing all 39 plans with no report at all —
    # nine shapes did. One case per distinct failing site: `.get()` on a non-dict element at the top
    # level, at the nested level, and `len()` on a non-list `objects`. The lesson the file keeps
    # relearning is that a guard written against one shape of a defect does not cover its class.
    ("a non-dict element in objects[] is reported Critical, not raised out of the whole run",
     True, [i for i in raw_issues({"apiVersion": "68.0", "objects": ["SELECT Id FROM Account"]})
            if i.startswith("Critical/") and "not an object" in i]),
    ("a non-dict element in objectSets[].objects[] is reported Critical",
     True, [i for i in raw_issues({"apiVersion": "68.0", "objectSets": [{"objects": [7]}]})
            if i.startswith("Critical/") and "not an object" in i]),
    ("a non-list objectSets[].objects is reported Critical",
     True, [i for i in raw_issues({"apiVersion": "68.0", "objectSets": [{"objects": 7}]})
            if i.startswith("Critical/") and "not an array" in i]),
    # A sibling being a valid list used to skip the other's type check: `{"objects": 7, "objectSets":
    # []}` passed "either array exists" then `enumerate(7)` aborted the whole run. Same class as the
    # three cases above — a guard written against one shape of a container defect does not cover it.
    ("a non-list objects next to a valid objectSets is reported Critical, not raised",
     True, [i for i in raw_issues({"apiVersion": "68.0", "objects": 7, "objectSets": []})
            if i.startswith("Critical/") and "'objects' is int" in i]),
    ("a non-list objectSets next to a valid objects is reported Critical, not raised",
     True, [i for i in raw_issues({"apiVersion": "68.0", "objects": [], "objectSets": 7})
            if i.startswith("Critical/") and "'objectSets' is int" in i]),
    # JSON `null` is a present value, not a missing key. `get(k, [])` ignores the default when the
    # key exists, `is not None` treats null as absent, and `"x" not in 7` TypeErrors. Same class:
    # a guard written against one non-list shape does not cover null or a non-object root.
    ("a JSON-null export.json root is reported Critical, not raised out of the whole run",
     True, [i for i in raw_issues(None)
            if i.startswith("Critical/") and "root is" in i]),
    ("a JSON-scalar export.json root is reported Critical, not raised out of the whole run",
     True, [i for i in raw_issues(7)
            if i.startswith("Critical/") and "root is" in i]),
    ("a present objectSets[].objects null is reported Critical, not treated as an empty pass",
     True, [i for i in raw_issues({"apiVersion": "68.0", "objectSets": [{"objects": None}]})
            if i.startswith("Critical/") and "NoneType" in i]),
    # `_parse_object_configs` reimplemented `_normalized_object_sets`'s flat-vs-objectSets logic
    # separately rather than calling it — the fourth call site to do so, after the three
    # `_normalized_object_sets`'s own docstring names as having disagreed before it existed — and
    # disagreed on one edge: `export_data.get("objectSets", [])` only substitutes `[]` when the key
    # is *absent*, so a present `"objectSets": null` left `object_sets` as `None` and
    # `enumerate(None)` raised `TypeError`. `validate_dataset` already rejects this exact shape one
    # step earlier (a present non-list `objectSets` is Critical, case above), so the crash was latent
    # rather than live through the CLI — but `_parse_object_configs` is called directly here, and a
    # private reimplementation of a helper built for exactly this problem is one more place to
    # disagree the next time either changes.
    ("_parse_object_configs does not raise on a present objectSets: null",
     True, [True for _ in [1] if method_survives("_parse_object_configs", {"objectSets": None})]),
    ("a present query null is reported as High, not treated as absent",
     True, [i for i in issues(
         [[{"query": None, "operation": "Upsert", "externalId": "Name"}]],
         None)
         if "query" in i and "not a string" in i]),
    # Placement, not logic. Both per-declaration sweeps sat after an early return that reads the
    # *merged* config, so an object excluded in pass 1 but live in pass 2 exited before them whenever
    # pass 2 was covered by an override. For the malformed check that was the worse of the two
    # failures: the same plan aborted the run before the coercion landed and was silent after it.
    ("a malformed externalId on a LIVE later declaration is reported even when pass 1 is excluded",
     True, [i for i in issues(
         [[{"query": "SELECT Id FROM Widget__c", "operation": "Upsert", "externalId": "Name",
            "excluded": True}],
          [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
            "externalId": ["Name", "Code"]}]],
         None, {2: {"Widget__c.csv": "Id,Name\n1,a\n"}})
         if "externalId is not a string" in i]),
    # The other half of the same inversion: inert declarations were reported while live ones were
    # skipped. SFDMU never processes an excluded declaration, so its externalId cannot matter — the
    # stance the operation check six lines above already took.
    ("a malformed externalId on an EXCLUDED declaration is not reported",
     False, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert", "externalId": "Name"}],
          [{"query": "SELECT Id FROM Widget__c", "operation": "Upsert",
            "externalId": ["Name", "Code"], "excluded": True}]],
         {"Widget__c.csv": "Id,Name\n1,a\n"})
         if "externalId is not a string" in i]),
    # The repr alone cannot distinguish `1` from `"1"`, which is the one case where the reader needs
    # to be told which they have — and `str()` has already destroyed the type by then.
    ("the malformed-externalId finding names the type, not just the coerced value",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert", "externalId": 1}]],
         {"Widget__c.csv": "Id,Name\n1,a\n"})
         if "it is int: 1" in i]),
    # A non-string `query` reached `re.search` and raised TypeError out of main(), same whole-run abort.
    # The declaration is skipped (its object name is unknowable), so the assertion is that the run
    # completes — which for this plan means the *other* object is still validated rather than lost.
    ("a non-string query skips its declaration instead of aborting the run",
     True, [i for i in issues(
         [[{"query": ["SELECT Id FROM Widget__c"], "operation": "Upsert", "externalId": "Name"},
           {"query": "SELECT Id, Name FROM Other__c", "operation": "Upsert", "externalId": "Name"}]],
         None)
         if "Other__c" in i]),
    # The skip alone is not a finding. A plan of only the malformed declaration plus a valid
    # `apiVersion` used to return passed=True with zero objects validated.
    ("a non-string query is reported as High, not only skipped",
     True, [i for i in issues(
         [[{"query": ["SELECT Id FROM Widget__c"], "operation": "Upsert", "externalId": "Name"}]],
         None)
         if "query" in i and "not a string" in i]),
    # ...and the inverse: `deleteOldData` was NOT in the key but IS read (it waives the composite-key
    # requirement), so two passes differing only in it collapsed to whichever came first and the
    # verdict flipped with declaration order. The waiving declaration is first here; the other must
    # still be checked.
    ("a deleteOldData pass does not waive the composite-key check for a sibling pass that lacks it",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Code", "deleteOldData": True}],
          [{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Code"}]],
         {"Widget__c.csv": "Name,Code\nwidget-a,c1\n"})
         if "composite key column" in i]),
    # `deleteOldData` used to be read with plain Python truthiness at every site that checks it,
    # but SFDMU reads it with JS truthiness — same mismatch already fixed for `excluded`: `[]`/
    # `{}` waive the composite-key check (JS-truthy, delete-then-insert needs no upsert match)
    # while Python reads them as falsy and wrongly demands the column.
    ("`deleteOldData: []` waives the composite-key check like `true` does",
     False, [i for i in issues(
         [[{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Code", "deleteOldData": []}]],
         {"Widget__c.csv": "Name,Code\nwidget-a,c1\n"})
         if "composite key column" in i]),
    ("...same for `deleteOldData: {}`",
     False, [i for i in issues(
         [[{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Code", "deleteOldData": {}}]],
         {"Widget__c.csv": "Name,Code\nwidget-a,c1\n"})
         if "composite key column" in i]),
    ("control: `deleteOldData: false` still requires the composite-key column",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Code", "deleteOldData": False}]],
         {"Widget__c.csv": "Name,Code\nwidget-a,c1\n"})
         if "composite key column" in i]),
    # The shape no config-dedup key can fix, and the one that bit real plans: two declarations that
    # genuinely differ (`Upsert` vs `Update`) produce a finding that does not depend on how they
    # differ, because "CSV file not found" depends only on the path. `qb-prm-pricing/Account` emitted
    # three identical Criticals this way. Deduped at `ValidationResult.add_issue` instead, which is
    # what makes per-declaration loops safe by construction rather than by key choice.
    ("a missing CSV is one finding however many passes read it",
     False, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert", "externalId": "Name"}],
          [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Update", "externalId": "Name"}]],
         None)
         if "not found" in i][1:]),
    # Report/fix parity for the class this PR added. The fixer read the merged config while validation
    # read the reading passes, so `--fix-all` wrote nothing and left the finding standing — a checker
    # reporting what its own fixer cannot clear is one people learn to ignore. Asserts convergence:
    # validate, fix, re-validate clean.
    ("--fix-all clears the pass-2 composite-key finding rather than leaving it standing",
     False, merged_config_fix_converges()),
    # Same skip, different flag: the merged first declaration is `excluded`, so the `if excluded:
    # continue` at the top of `fix_dataset_issues` returned before the reading-config loop. Inner
    # loop taught, outer skip still merged — `--fix-all` non-convergent for pass 1 excluded / pass 2
    # writable, which is the `qb-billing` shape.
    ("--fix-all still converges when pass 1 is excluded rather than Readonly",
     False, merged_config_fix_converges(_EX_FIRST)),
    # The same `excluded` stance, one layer down and reached by a different route. `writable_passes`
    # drops a pass whose *only* declaration is excluded, but a pass declaring the object twice — once
    # excluded — contributed the excluded one to the reading list, and widening the dedup key to
    # include `fields` stopped it collapsing into its sibling. The non-excluded declaration here
    # selects `Code`, so a coverage finding can only come from the excluded one.
    ("an excluded declaration sharing a pass contributes no externalId coverage finding",
     False, [i for i in issues(
         [[{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Code"},
           {"query": "SELECT Id FROM Widget__c", "operation": "Upsert", "externalId": "Name;Code",
            "excluded": True}]],
         {"Widget__c.csv": "$$Name$Code,Name,Code\nwidget-a;c1,widget-a,c1\n"})
         if "not found in query SELECT clause" in i]),
    # One file, one header proposal. Two reading passes with different SELECTs proposed two — and only
    # the first is what a real run writes, so the dry run described an outcome that would not happen.
    # Worse than a wrong count: the dry run is what an operator reads before deciding to apply it.
    # Asserted as "exactly one", not as "nothing after the first". `[1:]` on the probe's output is
    # empty both when there is one proposal and when the probe sees *nothing at all*, so renaming the
    # log line or silencing the proposal entirely left this green — an unpaired negative of exactly the
    # kind the round that added it claimed to have eliminated. `== 1` fails in both directions.
    ("--dry-run proposes exactly one header per file, not one per reading pass",
     False, fix_mode_proposals(
         {"apiVersion": "68.0", "objectSets": [
             {"objects": [{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
                           "externalId": "Name;Code"}]},
             {"objects": [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
                           "externalId": "Name;Code"}]}]},
         {"Widget__c.csv": ""}, fix_headers=True, expect=1)),
    # Same defect on the composite-key half, which the case above cannot reach: an empty CSV skips the
    # composite fix entirely (`not _is_csv_empty`), so it takes a populated file missing the column.
    # Both passes differ in SELECT, so both survive dedup on the reading key and both would propose.
    ("--dry-run proposes exactly one composite column per file, not one per reading pass",
     False, fix_mode_proposals(
         {"apiVersion": "68.0", "objectSets": [
             {"objects": [{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
                           "externalId": "Name;Code"}]},
             {"objects": [{"query": "SELECT Id, Name, Code, X__c FROM Widget__c",
                           "operation": "Upsert", "externalId": "Name;Code"}]}]},
         {"Widget__c.csv": "Name,Code\nwidget-a,c1\n"}, fix_composite_keys=True, expect=1)),
    # Same bookkeeping, other write path. The per-pass fixer gained per-declaration iteration and
    # did not gain the header/column tracking the root fixer already had, so two same-pass
    # declarations proposed twice against one override file.
    ("--dry-run proposes exactly one header per per-pass file, not one per same-pass declaration",
     False, fix_mode_proposals(
         {"apiVersion": "68.0", "objectSets": [{"objects": [
             {"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
              "externalId": "Name;Code"},
             {"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
              "externalId": "Name;Code"}]}]},
         per_pass_files={1: {"Widget__c.csv": ""}},
         fix_headers=True, expect=1)),
    # SFDMU does not process an excluded declaration, so its `operation` is inert. Sweeping every
    # declaration reported one anyway — a false positive the merged-config version never produced,
    # and the only new one this refactor introduced.
    ("a bogus operation on an excluded declaration is not reported",
     False, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert", "externalId": "Name"}],
          [{"query": "SELECT Id FROM Widget__c", "operation": "Upsurt", "externalId": "Name",
            "excluded": True}]],
         {"Widget__c.csv": "Id,Name\n1,a\n"})
         if "is not one SFDMU can resolve" in i]),
    # An unresolvable operation string is not a "not readonly" free pass, but it is also not a
    # "resets to Readonly" one either. `_resolveOperation` rejects "Upser" and returns undefined,
    # but — verified against the installed sfdmu@5.8.0 source — `ScriptObject.operation` does NOT
    # fall back to its Readonly class default for a *present* invalid value; `plainToInstance`
    # already committed the raw "Upser" onto the instance before `_resolveOperation` ran, and the
    # failed resolve just means that commit is never overwritten. "Upser" matches neither
    # Readonly(3) nor Delete(4) at SFDMU's write-dispatch gate, so the object still falls through
    # to the insert/update/upsert path and SFDMU *will* try to read a CSV for it. Both the
    # malformed-operation High and the missing-CSV Critical are real findings here. Two
    # assertions, not one `or`-ed list: both must fire, and collapsing them into one list would
    # pass on "either fired" as readily as on "both fired".
    ("a bogus operation with no CSV anywhere still reports the malformed-operation High",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Gizmo__c", "operation": "Upser", "externalId": "Name"}]])
         if "is not one SFDMU can resolve" in i]),
    ("...and ALSO reports a missing-CSV Critical for that same declaration — the raw invalid "
     "value is retained, not reset to Readonly, so the object still falls through to SFDMU's "
     "write-dispatch path and needs the CSV it does not have",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Gizmo__c", "operation": "Upser", "externalId": "Name"}]])
         if "CSV file not found" in i]),
    # The deleteOldData check read the merged `obj_config`, so a flag set only in pass 2 — with
    # pass 1 declaring none — was always answered by pass 1's absence: the same merged-config trap
    # already fixed above for `operation`/excluded/externalId, one check later.
    ("a deleteOldData flag set only in a later (non-merged) pass is still reported",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert", "externalId": "Name"}],
          [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert", "externalId": "Name",
            "deleteOldData": True}]],
         {"Widget__c.csv": "Id,Name\n1,a\n"})
         if "deleteOldData: true' but not in documented list" in i]),
    # The fix above put the new sweep AFTER the excluded-merged-config early return — the same
    # placement bug already fixed for operation/externalId/SELECT-coverage. An object excluded in
    # its first-declaring pass and owing no root CSV in its second (Readonly here) exits at that
    # return before a loop placed after it, so the live pass's own deleteOldData flag went
    # unreported.
    ("a deleteOldData flag on a live later pass is still reported when the first (merged) "
     "declaration is excluded and the object owes no root CSV",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
            "externalId": "Name", "excluded": True}],
          [{"query": "SELECT Id FROM Widget__c", "operation": "Readonly",
            "externalId": "Name", "deleteOldData": True}]])
         if "deleteOldData: true' but not in documented list" in i]),
]


# `_report_non_string_query` runs on the raw declaration, before `_all_pass_configs` filters
# `excluded` ones out — so it is the one query-validity check that can see the field at all.
QUERY_EXCLUDED_EXEMPTION = [
    ("a missing query on an already-excluded declaration is not reported — SFDMU already drops "
     "it with an objectIsExcluded warning, the outcome the author asked for",
     False, [i for i in issues([[{"operation": "Upsert", "externalId": "Name", "excluded": True}]])
            if "query' is missing" in i]),
    ("...but a missing query on a live (non-excluded) declaration still is — control for the "
     "case above",
     True, [i for i in issues([[{"operation": "Upsert", "externalId": "Name"}]])
            if "query' is missing" in i]),
]

UNSTRIPPED_EXTERNAL_ID = [
    # `_validate_external_id` used to split `externalId` on `;` without stripping, unlike every
    # other splitting site in this file (the fixer, and the composite-column-name builder below).
    # "Name; Code" (a space after the delimiter — easy to type by hand) left ' Code', which never
    # matches the parsed (trimmed) SELECT-field set even when the query correctly selects Code —
    # a false HIGH on correct data.
    ("a space after the externalId delimiter does not cause a false SELECT-coverage finding when "
     "the query selects every component",
     False, [i for i in issues(
         [[{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name; Code"}]])
         if "not found in query SELECT clause" in i]),
    # Control for the case above: a genuinely missing SELECT component is still caught once
    # stripped, proving the fix did not just silence the check.
    ("...but a genuinely missing SELECT component is still reported — control for the case above",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
            "externalId": "Name; Code"}]])
         if "not found in query SELECT clause" in i]),
    # `_validate_csv_file`'s composite-column-name construction had the same unstripped-split bug,
    # independently: "Name; Code" built the expected column as '$$Name$ Code' (an embedded space),
    # which a correctly-written CSV header ('$$Name$Code') never has — a false "missing composite
    # key column" HIGH on a CSV the fixer itself would never flag.
    ("a space after the externalId delimiter does not cause a false missing-composite-key-column "
     "finding when the CSV header is correct",
     False, [i for i in issues(
         [[{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name; Code"}]],
         {"Widget__c.csv": "$$Name$Code,Name,Code\nwidget-a;c1,widget-a,c1\n"})
         if "composite key column" in i]),
    # Control for the case above: a CSV genuinely missing the composite column is still caught.
    ("...but a CSV genuinely missing the composite column is still reported — control for the "
     "case above",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name; Code"}]],
         {"Widget__c.csv": "Name,Code\nwidget-a,c1\n"})
         if "composite key column" in i]),
]

EXCLUDED_INFO_MESSAGE = [
    # The excluded-early-return's own Info message read the merged (first-declaration)
    # `obj_config.get("excluded")`, so an object excluded in pass 1 but genuinely live (Readonly,
    # owing no root CSV) in pass 2 got a spurious "excluded but not in known excluded list" —
    # the same merged-config trap already fixed above for what each check *validates*, here in a
    # check's own message instead. `not live_declarations` — every non-excluded declaration
    # across every pass — is the correct "excluded everywhere" test, so a live pass-2 declaration
    # must suppress it.
    ("an object excluded in pass 1 but live in pass 2 does not get the 'excluded but not in "
     "known excluded list' Info",
     False, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
            "externalId": "Name", "excluded": True}],
          [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Readonly",
            "externalId": "Name"}]])
         if "excluded but not in known excluded list" in i]),
    # Control for the case above: an object excluded in every pass — no live declaration anywhere
    # — must still get it.
    ("...but an object excluded in every pass still does — control for the case above",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
            "externalId": "Name", "excluded": True}]])
         if "excluded but not in known excluded list" in i]),
]

EXCLUDED_JS_TRUTHINESS = [
    # `excluded` was read with plain Python truthiness at every site that checks it, but SFDMU
    # reads `object.excluded` with JS truthiness, and the two disagree on empty containers: `[]`/
    # `{}` are truthy in JS (SFDMU drops the declaration as excluded) but falsy in Python (these
    # sites read it as live/writable and demanded a CSV SFDMU never asks for).
    # `_is_live_writable` — writability -> CSV owed:
    ("an object excluded via an empty list (`excluded: []`) owes no CSV — SFDMU reads it as "
     "truthy/excluded, not the Python-falsy empty container it looks like",
     False, criticals([dict(UPSERT, excluded=[])])),
    ("...same for an empty dict (`excluded: {}`)",
     False, criticals([dict(UPSERT, excluded={})])),
    ("control: `excluded: false` still owes its CSV, same as the unset default",
     True, criticals([dict(UPSERT, excluded=False)])),
    # The reverse mismatch this control case used to pin — JSON's `NaN` extension decodes to a
    # Python-truthy `float('nan')`, JS treats NaN as falsy — is only worth testing if a NaN could
    # reach `_is_js_truthy` at all. It can't: SFDMU loads export.json with JavaScript's strict
    # `JSON.parse` (`ScriptLoader.js:54`), which rejects a bare `NaN`/`Infinity`/`-Infinity` token
    # outright — the file never loads, so `excluded` is never evaluated for truthiness. Python's
    # `json` module accepts those tokens by default; the validator now rejects them at load time
    # too, matching SFDMU's real failure mode instead of assigning truthiness to an unreachable
    # state.
    ("a NaN JSON constant fails to load like SFDMU's own strict JSON.parse would — never "
     "reaches excluded-truthiness at all",
     True, [i for i in issues([[dict(UPSERT, excluded=float("nan"))]])
           if "not valid JSON" in i]),
    # `_report_non_string_query` — the missing-query exemption:
    ("a missing query on a declaration excluded via `excluded: []` is not reported, same "
     "exemption as `excluded: true`",
     False, [i for i in issues([[{"operation": "Upsert", "externalId": "Name", "excluded": []}]])
            if "query' is missing" in i]),
    # `live_declarations` — the excluded-object Info message:
    ("an object excluded via `excluded: []` in every pass still gets the 'excluded but not in "
     "known excluded list' Info — same live_declarations test as `excluded: true`",
     True, [i for i in issues([[dict(UPSERT, excluded=[])]])
            if "excluded but not in known excluded list" in i]),
]

EXPLICIT_NULL_DEFAULTS = [
    # `obj.get(key, default)` only substitutes when the key is *absent*. `externalId` gets the
    # default anyway for an explicit `null` too, because SFDMU's own runtime does the same:
    # `ScriptObject.js`'s init path ends with `this.externalId = this.externalId ||
    # DEFAULT_EXTERNAL_ID_FIELD_NAME`, a falsy-OR fallback that treats `null` and absent
    # identically. `operation` gets no such fallback anywhere in `ScriptObject.js` — an absent
    # key resolves to the class's `Readonly` default via `class-transformer`'s
    # `exposeDefaultValues`, but an explicit `null` is committed onto the instance by that same
    # transform step *before* `ScriptLoader._resolveOperation` ever runs, and nothing resets it
    # afterward. So `"operation": null` and an absent `operation` key are NOT equivalent at
    # runtime — only `externalId`'s null/absent are.
    ("an explicit `operation: null` is reported as unresolvable, like any other bad value — it "
     "is NOT coalesced to Readonly the way an absent key is",
     True, [i for i in issues([[{"query": "SELECT Id, Name FROM Widget__c", "operation": None,
                                  "externalId": "Name"}]])
           if "is not one SFDMU can resolve" in i]),
    ("...and so it IS judged writable, and a missing CSV for it IS a Critical — the committed "
     "`null` is not Readonly(3)/Delete(4) at SFDMU's write-dispatch gate either, so the object "
     "still falls through to the insert/update/upsert path with no CSV to read",
     True, criticals([{"query": "SELECT Id, Name FROM Widget__c", "operation": None,
                       "externalId": "Name"}])),
    ("an explicit `externalId: null` defaults to \"Id\" like an absent key — no 'not a string' "
     "finding",
     False, [i for i in issues([[{"query": "SELECT Id FROM Widget__c", "operation": "Upsert",
                                  "externalId": None}]])
            if "not a string" in i]),
    # SFDMU's `this.externalId || DEFAULT_EXTERNAL_ID_FIELD_NAME` is a full JS falsy-OR, not a
    # null-only check — `0`, `false`, and `""` are exactly as falsy as `null` in JS and default the
    # same way. An earlier version here checked only `is None`, so these three fell through
    # unchanged and were reported malformed instead of silently defaulted to "Id".
    ("an explicit `externalId: 0` defaults to \"Id\" like null — 0 is falsy in JS too",
     False, [i for i in issues([[{"query": "SELECT Id FROM Widget__c", "operation": "Upsert",
                                  "externalId": 0}]])
            if "not a string" in i]),
    ("...same for `externalId: false`",
     False, [i for i in issues([[{"query": "SELECT Id FROM Widget__c", "operation": "Upsert",
                                  "externalId": False}]])
            if "not a string" in i]),
    ("...same for `externalId: \"\"`",
     False, [i for i in issues([[{"query": "SELECT Id FROM Widget__c", "operation": "Upsert",
                                  "externalId": ""}]])
            if "not a string" in i]),
    ("control — `externalId: []` is JS-truthy (an empty array is still an object), so it is NOT "
     "defaulted and IS reported malformed, same as any other non-string",
     True, [i for i in issues([[{"query": "SELECT Id FROM Widget__c", "operation": "Upsert",
                                 "externalId": []}]])
            if "not a string" in i]),
]

UNPARSEABLE_QUERY_REPORTED = [
    # `_extract_object_name` returns `""` for a non-blank string with no ` FROM <Object>` clause,
    # the same silent-drop `_report_non_string_query` already exists to report for a missing,
    # blank, or non-string query — just reached via a fourth shape it did not yet cover.
    ("a non-blank query with no parseable ' FROM <Object>' clause is reported, not silently "
     "dropped with zero objects validated and zero issues",
     True, [i for i in issues([[{"query": "SELECT Id", "operation": "Upsert",
                                 "externalId": "Id"}]])
            if "no parseable" in i]),
    ("...but a well-formed query does not — control for the case above",
     False, [i for i in issues([[{"query": "SELECT Id FROM Widget__c", "operation": "Upsert",
                                  "externalId": "Id"}]])
            if "no parseable" in i]),
]

MALFORMED_EXTERNAL_ID_NOT_DOUBLE_REPORTED = [
    # The SELECT-coverage sweep used to run on every live declaration unconditionally, including
    # one already flagged malformed (non-string, `str()`-coerced). A coerced repr that happens to
    # contain ';' (e.g. a list) was then split and checked component-by-component against the
    # SELECT clause, piling extra HIGHs onto the dedicated malformed-externalId HIGH for the same
    # one root cause.
    ("a malformed (list) externalId that stringifies with a ';' is not also split for "
     "SELECT-coverage — one finding for the root cause, not one per side effect",
     False, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
            "externalId": ["Name;Code"]}]],
         {"Widget__c.csv": "Id,Name\n1,a\n"})
         if "not found in query SELECT clause" in i]),
    ("...the dedicated malformed-externalId finding still fires — control for the case above",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
            "externalId": ["Name;Code"]}]],
         {"Widget__c.csv": "Id,Name\n1,a\n"})
         if "externalId is not a string" in i]),
]

# A malformed declaration's `externalId` coerces via `str()` (`_normalize_object_config`) and can
# equal a well-formed sibling's string value in a later pass — a dict `{"A.B.C": 1}` coerces to
# `"{'A.B.C': 1}"`, same as a literal string of that exact text. `_READING_CONFIG_KEYS` alone
# (externalId/operation/deleteOldData/fields) does not distinguish the two, so `_dedup_configs`
# collapsed them into one entry; when the malformed one sorted first (its declaring pass ran
# earlier), the SELECT-coverage loop's own `if cfg.get("externalId_malformed"): continue` then
# skipped the *kept* entry — silently dropping the well-formed sibling's own checks (here, the
# nested-relationship-path MEDIUM: the coerced text has two dots) instead of skipping only the
# malformed one.
DEDUP_KEY_MALFORMED_VS_WELLFORMED_EXTERNAL_ID = [
    ("a malformed externalId does not shadow a same-coerced-string well-formed sibling's "
     "own checks",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Readonly",
            "externalId": {"A.B.C": 1}}],
          [{"query": "SELECT Id, Name FROM Widget__c", "operation": "Readonly",
            "externalId": "{'A.B.C': 1}"}]])
         if "nested relationship path" in i]),
]

# `_split_external_id_fields` split on ';' with no empty-segment filter: a trailing or doubled ';'
# (an authoring typo, not a structural error `_normalize_object_config` flags) yielded a `""` field
# that flowed into the SELECT-coverage check as a component to look for, reporting a confusing
# `externalId component '' not found in query SELECT clause` HIGH instead of nothing.
TRAILING_SEMICOLON_EMPTY_SEGMENT = [
    ("a trailing ';' in externalId does not produce an empty-component SELECT-coverage finding",
     False, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert", "externalId": "Name;"}]])
         if "externalId component '' not found" in i]),
    ("...but a genuinely missing component in the same externalId is still caught — control",
     True, [i for i in issues(
         [[{"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Bogus__c"}]])
         if "externalId component 'Bogus__c' not found" in i]),
]


def live_baseline():
    """The validator's findings on the real tree, by severity.

    Several files state this baseline so a reader can tell a regression from the known state. The
    set is **discovered** by `baseline_sites()` below rather than listed here, because listing it
    was wrong twice: "four documents" was written while adding two more, and the recount to "seven
    sites across five files" missed three (`AGENTS.md`'s checklist item, `pr_gate.py`'s module
    docstring, and `sfdmu-data-plans/SKILL.md`, whose file the list omitted entirely) and
    double-counted one file's pair while counting another's as one. A hand-maintained list of the
    places a number must be swept is itself a number that must be swept.

    An unpinned number in prose drifts — `pr_gate.py`'s advisory note said "9 findings ... are
    validator false positives" for one commit past the point where that became false, while the
    adjacent `678` figure stayed correct because a test forces it. This is that forcing function
    for the baseline: when pack 110 deletes `mfg-multicurrency` the count goes to zero, this fails,
    and every site gets updated in the same change rather than a later one.
    """
    validator = V.SFDMUValidator(base_dir=str(REPO), verbose=False)
    by_sev, plans = {}, set()
    for plan in validator.find_sfdmu_datasets():
        res = validator.validate_dataset(plan)
        for issue in res.issues:
            if issue.severity in (V.Severity.CRITICAL, V.Severity.HIGH):
                by_sev[issue.severity.value] = by_sev.get(issue.severity.value, 0) + 1
                plans.add(res.dataset_name)
    return by_sev, plans


# The count words the repo actually writes, plus every neighbour of 7 — a wrong claim is most
# likely to be off by one, and a detector that only knows the right word cannot see a wrong one.
# `no`/`none` are in the table because "no High findings remain" is the most likely wording the day
# pack 110 lands, which is the exact moment this sweep exists for.
_WORD_COUNTS = {"zero": 0, "no": 0, "none": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}

# The plan holding the whole High baseline, written **repo-root-relative** rather than as the
# `mfg/en-US/mfg-multicurrency` the validator reports. The suffix is what the assertion below needs;
# the prefix is what makes this suite's dependency on `datasets/sfdmu/` visible to
# `tests/test_pr_gate.py`, whose path enumerator reads string constants and cannot see a path built
# inside `find_sfdmu_datasets()`. `pr_gate.py` argues at length that the `datasets/sfdmu/` trigger is
# essential — pack 110 deleting this plan must select the suite that fails on it — and nothing
# enforced the argument: the trigger could be deleted with all 680 pr_gate checks green. It cannot now.
_BASELINE_PLAN = "datasets/sfdmu/mfg/en-US/mfg-multicurrency"

# The baseline sites, pinned as `{file: how many times it states the baseline}`.
#
# Pinned because validating the discovered values cannot defend discovery itself. With only a
# non-empty assertion downstream, a site left the sweep silently whenever its wording stopped
# matching, and its now-stale claim went unread: `**seven High**` → `**eight remaining High**` passed
# green (one ordinary word between count and noun), as did moving the number after the noun
# ("High findings remaining: eight") and dropping the count altogether. Broadening the pattern helps
# and is not sufficient — two of those three used words the table already had — because the failure is
# structural: a regex-discovered set has no floor.
#
# **Per-file counts, not a set of files**, and the distinction is the whole guard. The first version
# pinned `frozenset(files)`, which defended only the four single-hit files: three of these state the
# baseline more than once, and a multi-hit file keeps its dict key while *any* one of its hits
# survives, so 7 of the 11 sites could be deleted outright with the suite green — including the
# after-the-noun reword this comment names as one of the failures the pin exists to catch. The count
# needed to see it was already being computed and printed in the passing message, then discarded.
# That is the same shape as the defect, one level up: a guard whose own coverage nobody measured.
_EXPECTED_BASELINE_SITES = {
    ".cursor/skills/doc-consistency/SKILL.md": 2,
    ".cursor/skills/sfdmu-data-plans/SKILL.md": 1,
    "AGENTS.md": 2,
    "docs/features/composable-quote-approvals.md": 1,
    "scripts/ai/README.md": 1,
    "scripts/ai/pr_gate.py": 3,
    # Found only after the pattern was loosened to allow words between the count and the noun
    # ("the seven remaining High findings"). It had been stating the baseline outside the sweep the
    # whole time, which is the failure mode this pin exists to make loud.
    "tests/test_pr_gate.py": 1,
}


def baseline_sites():
    """Every tracked file that states the High-findings baseline, with the value each one claims.

    Discovery is deliberately **independent of the expected number**, and that is the whole design.
    An earlier version matched only `7`/`seven`, which inverted the guard: editing a site to say
    "8 High" removed it from the result set rather than failing, and the only assertion downstream
    was that the set is non-empty — so the one edit the sweep exists to catch was the one edit it
    could not see. Matching *any* count and validating the captured values afterwards is what makes
    a wrong claim a failure instead of a disappearance.

    Anchored on the nouns the repo attaches the count to. That list is wider than it looks
    necessary, and deliberately: a first version matched only `High` and missed
    `sfdmu-data-plans/SKILL.md`, which spells the same baseline "7 zero-byte `Upsert` CSVs" —
    reproducing, in the detector, the exact omission the detector exists to prevent. `findings` is
    *not* in the list, though every real site does end "…High findings": as a standalone noun it
    also matches unrelated review narration ("five of its seven findings"), and a sweep set with a
    false member sends a reader to edit a line that must not change. A noun the repo has not used
    yet is the remaining gap in the other direction; that is why the assertion below prints the set
    rather than trusting it silently.

    Deliberately *not* keyed on `mfg-multicurrency` alone: `plan-dependency-graph.md` names the
    plan and its pack-110 removal without quoting a count, so it needs no edit when the count
    changes and including it would send a reader to a file with nothing to sweep.

    Returns `{path: [(line_number, claimed_count), ...]}`.
    """
    counts = "|".join(_WORD_COUNTS)
    # Up to two intervening words between the count and the anchor noun, because "eight remaining
    # High findings" is an ordinary sentence and the tighter `[\s\-*`]*` form missed it — dropping the
    # site from the sweep rather than failing. Bounded rather than open-ended so the count and the noun
    # still have to be in the same clause; an unbounded gap matches across unrelated sentences.
    #
    # Two alternatives, not one: `scripts/validate_sfdmu_v5_datasets.py:1154` writes "leaves High
    # at 7" — the anchor before the count, which the count-before-anchor form above cannot match
    # and would drop from the sweep silently, the same failure mode this whole function exists to
    # avoid. Named groups because `findall` on a two-group pattern returns a tuple per match, and
    # the single `raw.lower()` below expects a string; whichever branch fires leaves the other
    # group `None`.
    pattern = re.compile(
        rf"(?:\b(?P<count_before>\d+|{counts})\b[\s\-*`]*(?:\w+[\s\-*`]+){{0,2}}(?:high|zero-byte)"
        rf"|(?:high|zero-byte)[\s\-*`]*(?:\w+[\s\-*`]+){{0,2}}\b(?P<count_after>\d+|{counts})\b)",
        re.IGNORECASE)
    # `"tests"` (no slash) named a directory here, and `tests/test_pr_gate.py`'s trigger-coverage
    # sweep (`named_paths()`) keeps a slash-free constant only when it names a *file* — a directory
    # is admitted then dropped by its own return filter. So this suite's dependency on `tests/` was
    # invisible to "no suite reads a file that cannot select it": narrowing `tests` back to just
    # this file would have stayed green. A trailing slash does not fix it either —
    # `named_paths()`'s slash branch does `.strip("/")` before its own return filter re-checks
    # `"/" in p`, so `"tests/"` becomes `"tests"` and is filtered out exactly as before; only a
    # *multi*-segment root (`"scripts/ai"` etc.) survives that round trip. `tests/test_pr_gate.py`
    # is the only file this root exists to reach (verified: nothing else under `tests/` matches
    # `pattern`), so naming it directly is both the fix and a narrower, more precise root than
    # rglobbing the whole directory for every `.py`/`.md` file ever added there.
    #
    # `scripts/validate_sfdmu_v5_datasets.py` is deliberately not a root, even though two of its
    # docstrings once stated the live baseline ("7 High", "High at 7") — see the rewording at the
    # cited lines instead. Adding it would not just find those two: `_normalize_object_config`'s
    # docstring also says "252 High" and "245", the measured result of a *hypothetical* regression
    # this file is not tracking, sitting on the same line as the real "7". A generic count-before/
    # after-"High" pattern cannot tell "the current baseline" from "what breaks if you remove this
    # normalizer" — both are "NUMBER High" — and including them would fail "every hit claims 7"
    # below for a reason that has nothing to do with drift. Better to stop stating the bare number
    # there (the fix actually applied) than to teach this sweep the difference.
    roots = ["AGENTS.md", "scripts/ai", "docs/features", ".cursor/skills", "tests/test_pr_gate.py"]
    sites = {}
    for root in roots:
        base = REPO / root
        paths = [base] if base.is_file() else [
            p for p in base.rglob("*") if p.suffix in (".md", ".py") and p.is_file()]
        for path in paths:
            if path.name == pathlib.Path(__file__).name:
                continue  # this file describes the mechanism; it is not a site to sweep
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            hits = []
            for n, line in enumerate(lines, 1):
                # `finditer`, not `findall`: two named groups now share the pattern (count-before
                # and count-after), so a match carries one populated group and one `None` rather
                # than a single string `findall` could return directly.
                for m in pattern.finditer(line):
                    token = (m.group("count_before") or m.group("count_after")).lower()
                    hits.append((n, int(token) if token.isdigit() else _WORD_COUNTS.get(token)))
            if hits:
                sites[path.relative_to(REPO).as_posix()] = hits
    return sites


_sev, _plans = live_baseline()
_sites = baseline_sites()
# Symmetric difference, so both directions fail with the offending file named: a site that stopped
# matching the pattern (the silent-drop failure this pin exists for) and a new one nobody pinned.
_observed_sites = {f: len(hits) for f, hits in _sites.items()}
_site_drift = sorted(
    f"{f}: {_observed_sites.get(f, 0)} site(s), pinned {_EXPECTED_BASELINE_SITES.get(f, 0)}"
    for f in set(_observed_sites) | set(_EXPECTED_BASELINE_SITES)
    if _observed_sites.get(f, 0) != _EXPECTED_BASELINE_SITES.get(f, 0))
BASELINE = [
    ("the live tree has 0 Critical findings — the two pack 123 fixed were false positives",
     False, [f"{k}={v}" for k, v in _sev.items() if k == V.Severity.CRITICAL.value]),
    ("the live tree has exactly 7 High findings, the documented baseline",
     True, [f"High={_sev.get(V.Severity.HIGH.value, 0)}"]
           if _sev.get(V.Severity.HIGH.value, 0) == 7 else []),
    # The exact dataset name, not a substring. `"multicurrency" in p` also accepts a restored
    # `q3-multicurrency` — the very plan `dab545ab` deleted for carrying zero-byte CSVs of its own —
    # so the loose form would report the documentation green while the findings had moved to a
    # different plan than every one of those documents names.
    (f"all 7 are in {_BASELINE_PLAN} exactly, so the docs name the plan that has them",
     True, sorted(_plans) if _plans == {_BASELINE_PLAN.split("datasets/sfdmu/", 1)[1]} else []),
    # The per-file site counts are pinned, which is what gives discovery a floor: a site reworded out
    # of the pattern, or deleted outright, fails here rather than leaving the sweep with its stale
    # claim unread. Counts rather than a file set because three of these files state the baseline more
    # than once, and a file set stays satisfied by any one surviving hit.
    (f"the baseline is stated in {sum(len(v) for v in _sites.values())} place(s) across "
     f"{len(_EXPECTED_BASELINE_SITES)} pinned file(s): "
     + ", ".join(f"{f}:{','.join(str(n) for n, _ in ls)}" for f, ls in sorted(_sites.items())),
     True, sorted(_sites) if not _site_drift else []),
    # Prints the per-file delta with both numbers, so a failure names the file and the direction rather
    # than leaving a maintainer to diff two lists by eye.
    ("...and every pinned file states it exactly as many times as pinned"
     + (f" — DRIFT: {_site_drift}" if _site_drift else ""),
     False, _site_drift),
    (f"...and every one of them claims {_sev.get(V.Severity.HIGH.value, 0)}, the live High count",
     True, [f"{f}:{n}={c}" for f, ls in sorted(_sites.items()) for n, c in ls]
           if _sites and all(c == _sev.get(V.Severity.HIGH.value, 0)
                             for ls in _sites.values() for _, c in ls) else []),
]


def own_case_count_is_quoted_correctly(total):
    """`scripts/ai/README.md` quotes this suite's size; pin it where the size is known.

    It went stale twice in a row — two commits each raised the suite and each said the new number
    in its own message while leaving the sentence reading 13. The adjacent `680` in that same
    paragraph never drifted, because a test forces it, which is the whole argument. Pinned here
    rather than in `tests/test_pr_gate.py` next to the other two figures: this suite already knows
    its own total, so the check costs nothing, while over there it would mean importing this module
    and paying for a full validator run to learn a number.
    """
    quoted = re.search(r"pins both\s*\n?directions in (\d+) cases",
                       (REPO / "scripts/ai/README.md").read_text(encoding="utf-8"))
    if quoted is None:
        return ["the sentence in scripts/ai/README.md quoting this suite's size is gone"]
    return [] if int(quoted.group(1)) == total else [f"README says {quoted.group(1)}, suite has {total}"]


def main() -> int:
    failures = []
    all_cases = [("root-CSV expectation", CASES),
                 ("useSeparatedCSVFiles gates pass-2+ override coverage", USE_SEPARATED_CSV_FILES),
                 ("useSeparatedCSVFiles is read with JS truthiness, not Python's",
                  USE_SEPARATED_CSV_FILES_JS_TRUTHINESS),
                 ("per-pass validation actually runs", PER_PASS_IS_VALIDATED),
                 ("operation values SFDMU can and cannot resolve", OPERATION_RESOLUTION),
                 ("a numeric operation gates the externalId Insert-mode skip, not just a string one",
                  NUMERIC_OPERATION_GATING),
                 ("fix modes write where they should and nowhere else", FIX_MODES),
                 ("later passes are validated, not just the merged first declaration", MERGED_CONFIG),
                 ("a missing query is exempt on an already-excluded declaration", QUERY_EXCLUDED_EXEMPTION),
                 ("an unstripped externalId delimiter does not cause false SELECT/composite-key findings",
                  UNSTRIPPED_EXTERNAL_ID),
                 ("the excluded-object Info message tracks live_declarations, not merged excluded",
                  EXCLUDED_INFO_MESSAGE),
                 ("excluded is read with JS truthiness, not Python's, at every call site",
                  EXCLUDED_JS_TRUTHINESS),
                 ("an explicit null externalId defaults like an absent key, operation does not",
                  EXPLICIT_NULL_DEFAULTS),
                 ("a query with no parseable FROM clause is reported, not silently dropped",
                  UNPARSEABLE_QUERY_REPORTED),
                 ("a malformed externalId is not double-reported by the SELECT-coverage sweep too",
                  MALFORMED_EXTERNAL_ID_NOT_DOUBLE_REPORTED),
                 ("a malformed externalId does not shadow a same-coerced-string well-formed "
                  "sibling's own SELECT-coverage check",
                  DEDUP_KEY_MALFORMED_VS_WELLFORMED_EXTERNAL_ID),
                 ("a trailing/doubled ';' in externalId does not yield an empty-component finding",
                  TRAILING_SEMICOLON_EMPTY_SEGMENT),
                 ("the documented live baseline still holds", BASELINE)]
    # +1 for the self-count check appended below, which needs the total it asserts against.
    total = sum(len(c) for _, c in all_cases) + 1
    all_cases.append(("this suite's own size, as quoted in prose", [
        (f"scripts/ai/README.md says this suite pins both directions in {total} cases",
         False, own_case_count_is_quoted_correctly(total))]))
    print("=" * 100)
    for group, cases in all_cases:
        print(f"-- {group}")
        for label, expect_finding, found in cases:
            ok = bool(found) == expect_finding
            if not ok:
                failures.append(label)
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
            if not ok:
                print(f"         expected a finding={expect_finding}, got={found or 'none'}")
    print("=" * 100)
    if failures:
        for label in failures:
            print(f"FAILED: {label}")
        print(f"\n{total - len(failures)}/{total} checks passed")
        return 1
    print(f"{total}/{total} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

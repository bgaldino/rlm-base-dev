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

import importlib.util
import json
import pathlib
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


def issues(passes, root_files=None, per_pass_files=None, severity=None):
    """Validate a synthetic plan and return its issue strings, optionally filtered by severity.

    `passes` is a list of objectSets, each a list of object configs, so a case can put the same
    object in more than one pass — the shape the whole per-pass question turns on.
    `per_pass_files` maps a 1-based pass number to `{filename: body}` under
    `objectset_source/object-set-N/`.

    Synthetic rather than a copy of a real plan: a fixture carved out of one passes or fails for
    reasons the case did not choose, which is how a control ends up vacuous.
    """
    with tempfile.TemporaryDirectory() as td:
        plan = pathlib.Path(td) / "plan"
        plan.mkdir()
        (plan / "export.json").write_text(json.dumps({"objectSets": [{"objects": p} for p in passes]}))
        for name, body in (root_files or {}).items():
            (plan / name).write_text(body)
        for pass_number, files in (per_pass_files or {}).items():
            d = plan / "objectset_source" / f"object-set-{pass_number}"
            d.mkdir(parents=True, exist_ok=True)
            for name, body in files.items():
                (d / name).write_text(body)
        result = V.SFDMUValidator(base_dir=str(plan.parent), verbose=False).validate_dataset(plan)
        return [f"{i.severity.value}/{i.object_name}: {i.message}" for i in result.issues
                if severity is None or i.severity == severity]


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
        plan = pathlib.Path(td) / "plan"
        plan.mkdir()
        (plan / "export.json").write_text(json.dumps({"objects": [UPSERT]}))
        for n, files in (per_pass or {}).items():
            d = plan / "objectset_source" / f"object-set-{n}"
            d.mkdir(parents=True, exist_ok=True)
            for name, body in files.items():
                (d / name).write_text(body)
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
    ("an Upsert object supplied per-pass is silent at the root: the file lives under "
     "objectset_source/ and is validated there",
     False, criticals([UPSERT], None, {"Widget__c.csv": HEADER})),
    # The gate keys on *this* object having a per-pass file, not on the plan having any. Keyed
    # on the plan, one override would excuse every missing CSV in it.
    ("an Upsert object whose per-pass CSV is absent still fails, even though a *different* "
     "object has one",
     True, criticals([UPSERT], None, {"Unrelated__c.csv": HEADER})),
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
    # `excluded` skip in _writable_passes_by_object makes pass 2 count as writable, so the pass-1
    # override no longer covers every writable pass and a spurious Critical appears.
    ("an object Upsert in pass 1 with an override, excluded in pass 2, owes nothing",
     False, issues([[UPSERT], [dict(UPSERT, excluded=True)]], None,
                   {1: {"Widget__c.csv": HEADER}}, severity=V.Severity.CRITICAL)),
    # A flat `objects` plan (no objectSets) with per-pass CSVs: three functions disagreed about
    # normalizing that shape, so the CSVs were silently discarded behind a WARN suppressed at
    # default verbosity. And `object-set-0` maps to pass_index -1, which an upper-bound-only check
    # let through into a negative index — an IndexError aborting the whole run rather than
    # reporting the one bad plan.
    ("a flat objects-key plan supplies its CSV per-pass and owes nothing at the root",
     False, flat_plan(per_pass={1: {"Widget__c.csv": HEADER}})),
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
    ("...and is silent once EVERY writable pass is supplied per-pass",
     False, issues([[UPSERT], [dict(UPSERT, operation="Update")]], None,
                   {1: {"Widget__c.csv": HEADER}, 2: {"Widget__c.csv": HEADER}},
                   severity=V.Severity.CRITICAL)),
    # A CSV in the wrong object-set-N/ is never read, so counting it as coverage trades a Critical
    # for a High about the misfiling — a downgrade on the only automated check over this data.
    ("a per-pass CSV misfiled into a pass that does not declare the object does not excuse the "
     "root CSV",
     True, issues([[READONLY], [UPSERT]], None, {1: {"Widget__c.csv": HEADER}},
                  severity=V.Severity.CRITICAL)),
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
    # also used to cause. Known gap, deliberately not fixed here: a directory that maps to no pass
    # still produces only a WARN, suppressed at default verbosity, rather than a finding.
    ("an object-set-0 directory is not silently attributed to the last pass",
     False, [i for i in issues([[UPSERT]], {"Widget__c.csv": HEADER}, {0: {"Widget__c.csv": HEADER}})
             if "no matching object" in i]),
]


def live_baseline():
    """The validator's findings on the real tree, by severity.

    Seven sites across five files state this baseline so a reader can tell a regression from the
    known state — `AGENTS.md`, `scripts/ai/README.md`, `pr_gate.py` twice (trigger comment and the
    runtime `note=`), `.cursor/skills/doc-consistency/SKILL.md` twice, and
    `docs/features/composable-quote-approvals.md`. Counting them was itself wrong once ("four
    documents", written while adding two of the seven), which is the argument for the pin below
    rather than against it. And
    an unpinned number in prose drifts — `pr_gate.py`'s advisory note said "9 findings ... are
    validator false positives" for one commit past the point where that became false, while the
    adjacent `678` figure stayed correct because a test forces it. This is that forcing function
    for the baseline: when pack 110 deletes `mfg-multicurrency` the count goes to zero, this fails,
    and the four documents get updated in the same change rather than a later one.
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


_sev, _plans = live_baseline()
BASELINE = [
    # Stated in AGENTS.md, scripts/ai/README.md, pr_gate.py's docstring and its runtime note.
    ("the live tree has 0 Critical findings — the two pack 123 fixed were false positives",
     False, [f"{k}={v}" for k, v in _sev.items() if k == V.Severity.CRITICAL.value]),
    ("the live tree has exactly 7 High findings, the documented baseline",
     True, [f"High={_sev.get(V.Severity.HIGH.value, 0)}"]
           if _sev.get(V.Severity.HIGH.value, 0) == 7 else []),
    ("all of them are in mfg-multicurrency, so the baseline names one plan and not a scatter",
     True, [p for p in _plans if "multicurrency" in p] if _plans and all(
         "multicurrency" in p for p in _plans) else []),
]


def main() -> int:
    failures = []
    all_cases = [("root-CSV expectation", CASES),
                 ("per-pass validation actually runs", PER_PASS_IS_VALIDATED),
                 ("the documented live baseline still holds", BASELINE)]
    total = sum(len(c) for _, c in all_cases)
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

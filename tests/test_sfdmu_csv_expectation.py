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


def criticals(objects, root_files=None, per_pass_files=None):
    """Validate a synthetic one-plan tree and return its Critical messages.

    Synthetic rather than a copy of `procedure-plans`: a fixture carved out of a real plan
    passes or fails for reasons the case did not choose, which is how a control ends up
    vacuous.
    """
    with tempfile.TemporaryDirectory() as td:
        plan = pathlib.Path(td) / "plan"
        plan.mkdir()
        (plan / "export.json").write_text(json.dumps({"objectSets": [{"objects": objects}]}))
        for name, body in (root_files or {}).items():
            (plan / name).write_text(body)
        if per_pass_files:
            d = plan / "objectset_source" / "object-set-1"
            d.mkdir(parents=True)
            for name, body in per_pass_files.items():
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
    # (surveyed: 0 of the 76 export.json files under datasets/sfdmu, a superset of the 39 tracked
    # plans), and if one appears the Readonly gate would silence a writable pass — so pin it now.
    ("a Readonly first pass followed by an Upsert pass for the same object is NOT silenced",
     True, criticals([dict(READONLY), dict(UPSERT, query="SELECT Id, Name FROM Gadget__c")])),
]


def main() -> int:
    failures = []
    print("=" * 100)
    for label, expect_critical, found in CASES:
        got_critical = bool(found)
        ok = got_critical == expect_critical
        if not ok:
            failures.append(label)
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        if not ok:
            print(f"         expected Critical={expect_critical}, got={found or 'none'}")
    print("=" * 100)
    if failures:
        for label in failures:
            print(f"FAILED: {label}")
        print(f"\n{len(CASES) - len(failures)}/{len(CASES)} checks passed")
        return 1
    print(f"{len(CASES)}/{len(CASES)} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

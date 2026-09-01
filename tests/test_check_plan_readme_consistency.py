#!/usr/bin/env python3
"""Does `check_plan_readme_consistency.py` parse a README object table the way it says it does?

Only `tests/test_pr_gate.py`'s argv/meta-shape assertions touched this module before this suite —
nothing exercised `load_plan()`/`parse_object_tables()`/`check_plan()`'s actual parsing semantics
against a crafted README/export.json pair. That left several PR #406 fixes (pack 147) with no
regression guard but the module's own comments: Pass-column narrowing to the row's own pass
(round 16), a bogus Pass claim reported rather than silently falling back to ANY-variant match —
for an out-of-range number (round 17) and for non-numeric garbage (round 18) — the
IGNORE_MARKER/seen_objects composition (round 15), the OMIT_MARKER missing-object opt-out, and
KEYLIKE_RE gating the externalId comparison to literal-looking cells only.

Run: `python tests/test_check_plan_readme_consistency.py` (offline, no org).
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
CHECKER = REPO / "scripts" / "ai" / "check_plan_readme_consistency.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("plan_readme_checker", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C = load_checker()

OBJECT_TABLE_HEADER = "| # | Object | Pass | Operation | External ID | Records |"
OBJECT_TABLE_SEP = "|---|--------|------|-----------|-------------|---------|"


def _row(num, name, pass_cell, operation, ext_id, records="—"):
    return f"| {num} | {name} | {pass_cell} | {operation} | {ext_id} | {records} |"


def _check(passes, readme_rows, extra_readme_lines=None, csvs=None):
    """Materialize a synthetic plan dir (export.json + README.md [+ CSVs]) and run check_plan().

    `passes` is a list of objectSets, each a list of object configs — same shape
    tests/test_sfdmu_csv_expectation.py uses, so a case can put the same object in more than one
    pass. `readme_rows` are literal object-table row strings (built by `_row()`, or a raw ignore-
    marker row); `extra_readme_lines` go anywhere else in the file (e.g. an OMIT_MARKER).
    """
    with tempfile.TemporaryDirectory() as td:
        plan = pathlib.Path(td) / "plan"
        plan.mkdir()
        export_data = {"objectSets": [{"objects": p} for p in passes]}
        (plan / "export.json").write_text(json.dumps(export_data))
        for name, body in (csvs or {}).items():
            (plan / name).write_text(body)
        lines = ["# Test Plan", "", "## Objects", "", OBJECT_TABLE_HEADER, OBJECT_TABLE_SEP,
                 *readme_rows, "", *(extra_readme_lines or [])]
        (plan / "README.md").write_text("\n".join(lines) + "\n")
        return C.check_plan(str(plan))


UPSERT_P1 = {"query": "SELECT Id FROM Widget__c", "operation": "Upsert", "externalId": "Name"}
UPDATE_P3 = {"query": "SELECT Id FROM Widget__c", "operation": "Update", "externalId": "Name"}

PASS_NARROWING = [
    ("a row matching its own pass's operation is clean",
     False, _check([[UPSERT_P1], [], [UPDATE_P3]],
                   [_row(1, "Widget__c", 1, "Upsert", "Name")])[1]),
    ("a row claiming Pass 1 but a different pass's operation is flagged, not matched ANY-variant",
     True, _check([[UPSERT_P1], [], [UPDATE_P3]],
                   [_row(1, "Widget__c", 1, "Update", "Name")])[1]),
    ("the same object's OTHER pass, correctly labelled, is independently clean",
     False, _check([[UPSERT_P1], [], [UPDATE_P3]],
                   [_row(1, "Widget__c", 3, "Update", "Name")])[1]),
]

NO_PASS_CELL_FALLBACK = [
    ("no Pass cell at all still matches ANY variant (Upsert)",
     False, _check([[UPSERT_P1], [], [UPDATE_P3]],
                   [_row(1, "Widget__c", "", "Upsert", "Name")])[1]),
    ("no Pass cell at all still matches ANY variant (Update, the other pass)",
     False, _check([[UPSERT_P1], [], [UPDATE_P3]],
                   [_row(1, "Widget__c", "", "Update", "Name")])[1]),
]

BOGUS_PASS = [
    ("an out-of-range numeric Pass is reported, not silently ANY-variant matched",
     True, _check([[UPSERT_P1], [], [UPDATE_P3]],
                   [_row(1, "Widget__c", 99, "Upsert", "Name")])[1]),
    ("a non-numeric Pass ('N/A') is reported too, not treated as 'no Pass cell' (round 18)",
     True, _check([[UPSERT_P1], [], [UPDATE_P3]],
                   [_row(1, "Widget__c", "N/A", "Upsert", "Name")])[1]),
    ("a bogus Pass produces exactly one warning, not a second confusing empty-wants warning",
     1, len(_check([[UPSERT_P1], [], [UPDATE_P3]],
                    [_row(1, "Widget__c", "N/A", "Upsert", "Name")])[1])),
]

IGNORE_MARKER = [
    ("an ignored row with the wrong operation is not flagged",
     False, _check([[UPSERT_P1]],
                   [_row(1, "Widget__c", 1, "Delete", "Name") + " <!-- readme-check: ignore -->"])[1]),
    ("an ignored row's object still counts as 'seen' — no missing-object WARN (round 15)",
     False, any("absent from the README object table" in w for w in
                _check([[UPSERT_P1]],
                       [_row(1, "Widget__c", 1, "Delete", "Name") + " <!-- readme-check: ignore -->"])[1])),
]

GADGET_P1 = {"query": "SELECT Id FROM Gadget__c", "operation": "Upsert", "externalId": "Name"}
# A table with a row for some OTHER object, so object_table_found is True and the
# missing-object sweep actually runs — with no row at all, check_plan() never sets
# object_table_found and the sweep (correctly) doesn't fire, which would make a "no
# Widget__c row" case pass for the wrong reason (no table, not "table omits it").
_ONE_OTHER_ROW = [_row(1, "Gadget__c", 1, "Upsert", "Name")]

OMIT_MARKER = [
    ("an object never tabulated is flagged missing by default",
     True, any("absent from the README object table" in w for w in
              _check([[UPSERT_P1, GADGET_P1]], _ONE_OTHER_ROW)[1])),
    ("...unless a readme-check: omit marker names it",
     False, any("absent from the README object table" in w for w in
                _check([[UPSERT_P1, GADGET_P1]], _ONE_OTHER_ROW,
                       extra_readme_lines=["<!-- readme-check: omit: Widget__c -->"])[1])),
]

KEYLIKE_GATING = [
    ("a literal externalId mismatch is flagged",
     True, _check([[UPSERT_P1]], [_row(1, "Widget__c", 1, "Upsert", "OtherField")])[1]),
    ("prose in the External ID cell is not compared at all (KEYLIKE_RE gate)",
     False, _check([[UPSERT_P1]], [_row(1, "Widget__c", 1, "Upsert", "4-field composite")])[1]),
]


def main() -> int:
    failures = []
    all_cases = [
        ("Pass-column narrowing matches a row against its own pass, not the union", PASS_NARROWING),
        ("no Pass cell falls back to ANY-variant matching", NO_PASS_CELL_FALLBACK),
        ("a Pass cell with a bad value (numeric or not) is reported, never silently matched", BOGUS_PASS),
        ("readme-check: ignore composes with the missing-object seen_objects check", IGNORE_MARKER),
        ("readme-check: omit opts an object out of the missing-object WARN", OMIT_MARKER),
        ("KEYLIKE_RE gates the externalId comparison to literal-looking cells", KEYLIKE_GATING),
    ]
    print("=" * 100)
    for group, cases in all_cases:
        print(f"-- {group}")
        for label, expect_finding, found in cases:
            ok = bool(found) == bool(expect_finding) if isinstance(expect_finding, bool) else found == expect_finding
            if not ok:
                failures.append(label)
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
            if not ok:
                print(f"         expected={expect_finding}, got={found}")
    print("=" * 100)
    total = sum(len(c) for _, c in all_cases)
    if failures:
        for label in failures:
            print(f"FAILED: {label}")
        print(f"\n{total - len(failures)}/{total} checks passed")
        return 1
    print(f"{total}/{total} checks passed")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

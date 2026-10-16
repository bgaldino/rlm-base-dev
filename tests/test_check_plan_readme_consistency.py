#!/usr/bin/env python3
"""Does `check_plan_readme_consistency.py` parse a README object table the way it says it does?

Only `tests/test_pr_gate.py`'s argv/meta-shape assertions touched this module before this suite —
nothing exercised `load_plan()`/`parse_object_tables()`/`check_plan()`'s actual parsing semantics
against a crafted README/export.json pair. That left several PR #406 fixes (pack 147) with no
regression guard but the module's own comments: Pass-column narrowing to the row's own pass
(round 16), a bogus Pass claim reported rather than silently falling back to ANY-variant match —
for an out-of-range number (round 17) and for non-numeric garbage (round 18) — the
IGNORE_MARKER/seen_objects composition (round 15), the OMIT_MARKER missing-object opt-out,
KEYLIKE_RE gating the externalId comparison to literal-looking cells only, a comma-joined
multi-pass cell rejected rather than misparsed as one larger number (round 19), and missing-
object coverage tracked per-pass rather than per-name (round 19).

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


def _check(passes, readme_rows, extra_readme_lines=None, csvs=None, export_options=None):
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
        export_data.update(export_options or {})
        (plan / "export.json").write_text(json.dumps(export_data))
        for name, body in (csvs or {}).items():
            (plan / name).parent.mkdir(parents=True, exist_ok=True)
            (plan / name).write_text(body)
        lines = ["# Test Plan", "", "## Objects", "", OBJECT_TABLE_HEADER, OBJECT_TABLE_SEP,
                 *readme_rows, "", *(extra_readme_lines or [])]
        (plan / "README.md").write_text("\n".join(lines) + "\n")
        return C.check_plan(str(plan))


UPSERT_P1 = {"query": "SELECT Id FROM Widget__c", "operation": "Upsert", "externalId": "Name"}
UPDATE_P3 = {"query": "SELECT Id FROM Widget__c", "operation": "Update", "externalId": "Name"}

# Widget__c has two non-excluded passes (1 and 3) — per-pass missing-object coverage
# (round 19) means a row for only one of them leaves the other flagged missing, which
# would add unrelated noise to these operation-matching cases. Pair each row under test
# with a correctly-labelled row for the object's OTHER pass so only the behavior under
# test produces a warning.
OTHER_PASS_ROW = _row(2, "Widget__c", 3, "Update", "Name")
OTHER_PASS_ROW_P1 = _row(2, "Widget__c", 1, "Upsert", "Name")

PASS_NARROWING = [
    ("a row matching its own pass's operation is clean",
     False, _check([[UPSERT_P1], [], [UPDATE_P3]],
                   [_row(1, "Widget__c", 1, "Upsert", "Name"), OTHER_PASS_ROW])[1]),
    ("a row claiming Pass 1 but a different pass's operation is flagged, not matched ANY-variant",
     True, _check([[UPSERT_P1], [], [UPDATE_P3]],
                   [_row(1, "Widget__c", 1, "Update", "Name"), OTHER_PASS_ROW])[1]),
    ("the same object's OTHER pass, correctly labelled, is independently clean",
     False, _check([[UPSERT_P1], [], [UPDATE_P3]],
                   [_row(1, "Widget__c", 3, "Update", "Name"), OTHER_PASS_ROW_P1])[1]),
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
                    [_row(1, "Widget__c", "N/A", "Upsert", "Name"),
                     OTHER_PASS_ROW, OTHER_PASS_ROW_P1])[1])),
]

IGNORE_MARKER = [
    ("an ignored row with the wrong operation is not flagged",
     False, _check([[UPSERT_P1]],
                   [_row(1, "Widget__c", 1, "Delete", "Name") + " <!-- readme-check: ignore -->"])[1]),
    ("an ignored row's object still counts as 'seen' — no missing-object WARN (round 15)",
     False, any("absent from the README object table" in w for w in
                _check([[UPSERT_P1]],
                       [_row(1, "Widget__c", 1, "Delete", "Name") + " <!-- readme-check: ignore -->"])[1])),
    ("an ignored row for ONE pass doesn't vouch for the object's other, real pass (round 20)",
     True, any("absent from the README object table" in w for w in
              _check([[UPSERT_P1], [], [UPDATE_P3]],
                     [_row(1, "Widget__c", 3, "Update", "Name") + " <!-- readme-check: ignore -->"])[1])),
    ("...but an ignored row with no Pass cell still vouches for every pass (unchanged fallback)",
     False, any("absent from the README object table" in w for w in
                _check([[UPSERT_P1], [], [UPDATE_P3]],
                       [_row(1, "Widget__c", "", "Update", "Name") + " <!-- readme-check: ignore -->"])[1])),
]

GADGET_P1 = {"query": "SELECT Id FROM Gadget__c", "operation": "Upsert", "externalId": "Name"}
SPROCKET_P1 = {"query": "SELECT Id FROM Sprocket__c", "operation": "Upsert", "externalId": "Name"}
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
    ("two omit markers sharing ONE line both take effect, not just the first (round 20)",
     False, any("absent from the README object table" in w for w in
                _check([[UPSERT_P1, GADGET_P1, SPROCKET_P1]],
                       [_row(1, "Sprocket__c", 1, "Upsert", "Name")],
                       extra_readme_lines=["<!-- readme-check: omit: Widget__c --> "
                                           "<!-- readme-check: omit: Gadget__c -->"])[1])),
]

KEYLIKE_GATING = [
    ("a literal externalId mismatch is flagged",
     True, _check([[UPSERT_P1]], [_row(1, "Widget__c", 1, "Upsert", "OtherField")])[1]),
    ("prose in the External ID cell is not compared at all (KEYLIKE_RE gate)",
     False, _check([[UPSERT_P1]], [_row(1, "Widget__c", 1, "Upsert", "4-field composite")])[1]),
]

COMMA_PASS = [
    ("a comma-joined Pass cell ('1,3') is reported, not silently parsed as 13 (round 19)",
     True, _check([[UPSERT_P1], [], [UPDATE_P3]],
                   [_row(1, "Widget__c", "1,3", "Upsert", "Name"),
                    OTHER_PASS_ROW, OTHER_PASS_ROW_P1])[1]),
    ("the comma-Pass warning names the raw cell, not parse_int()'s comma-stripped 13",
     True, any("1,3" in w and "13" not in w for w in
              _check([[UPSERT_P1], [], [UPDATE_P3]],
                     [_row(1, "Widget__c", "1,3", "Upsert", "Name"),
                      OTHER_PASS_ROW, OTHER_PASS_ROW_P1])[1])),
]

EXCLUDED_P2 = {"query": "SELECT Id FROM Widget__c", "operation": "Delete", "externalId": "Name",
               "excluded": True}

PER_PASS_COVERAGE = [
    ("a row for only the excluded pass doesn't vouch for the object's real, unlisted pass 1 (round 19)",
     True, any("absent from the README object table" in w for w in
              _check([[UPSERT_P1], [EXCLUDED_P2]],
                     [_row(1, "Widget__c", 2, "Delete", "Name")])[1])),
    ("...and the warning calls out pass 1 specifically, not a bare 'absent' with no pass detail",
     True, any("[1]" in w for w in
              _check([[UPSERT_P1], [EXCLUDED_P2]],
                     [_row(1, "Widget__c", 2, "Delete", "Name")])[1])),
    ("a row for each real, non-excluded pass leaves no missing-object warning",
     False, any("absent from the README object table" in w for w in
                _check([[UPSERT_P1], [EXCLUDED_P2]],
                       [_row(1, "Widget__c", 1, "Upsert", "Name")])[1])),
]



def _count_check(records=(5, 3), flag=True, passes=(1, 3), extra_csvs=None,
                 ignore=False, extra_readme_lines=None):
    csvs = {"Widget__c.csv": "Id\n" + "root\n" * 5,
            "objectset_source/object-set-3/Widget__c.csv": "Id\n" + "override\n" * 3}
    csvs.update(extra_csvs or {})
    rows = [_row(1, "Widget__c", passes[0], "Upsert", "Name", records[0]),
            _row(2, "Widget__c", passes[1], "Update", "Name", records[1])]
    if ignore:
        rows = [row + " <!-- readme-check: ignore -->" for row in rows]
    return _check([[UPSERT_P1], [], [UPDATE_P3]], rows, csvs=csvs,
                  export_options={"useSeparatedCSVFiles": flag},
                  extra_readme_lines=extra_readme_lines)


_SWAPPED = _count_check(records=(3, 5))
PASS_COUNTS = [
    ("correct counts for passes 1 and 3 pass", ([], [], True), _count_check()),
    ("swapping counts reports both incorrect rows", 2, len(_SWAPPED[0])),
    ("each swapped-count error identifies its pass and actual source",
     True, all(any(f"Pass={n}" in e and source in e and f"actual CSV={actual}" in e
                   for e in _SWAPPED[0])
               for n, source, actual in [(1, "Widget__c.csv", 5),
                                         (3, "objectset_source/object-set-3/Widget__c.csv", 3)])),
    ("pass 1 ignores object-set-1 even with separated files enabled", ([], [], True),
     _count_check(extra_csvs={"objectset_source/object-set-1/Widget__c.csv": "Id\none\n"})),
    ("disabled separated files make both passes read the root", ([], [], True),
     _count_check(records=(5, 5), flag=False)),
    ("a disabled override cannot justify a pass-3 count", 1,
     len(_count_check(flag=False)[0])),
    ("missing override falls back to root even with unrelated CSV copies", ([], [], True),
     _check([[UPSERT_P1], [], [UPDATE_P3]],
            [_row(1, "Widget__c", 1, "Upsert", "Name", 5),
             _row(2, "Widget__c", 3, "Update", "Name", 5)],
            csvs={"Widget__c.csv": "Id\n" + "root\n" * 5,
                  "archive/Widget__c.csv": "Id\nold\n"},
            export_options={"useSeparatedCSVFiles": True})),
    ("pass-1 override cannot justify a wrong root count", 1,
     len(_count_check(records=(1, 3), extra_csvs={
         "objectset_source/object-set-1/Widget__c.csv": "Id\none\n"})[0])),
    ("a CSV for another pass cannot justify a count when this pass has no source", 1,
     len(_check([[UPSERT_P1], [], [UPDATE_P3]],
                [_row(1, "Widget__c", 1, "Upsert", "Name", 3),
                 _row(2, "Widget__c", 3, "Update", "Name", 3)],
                csvs={"objectset_source/object-set-3/Widget__c.csv": "Id\n" + "row\n" * 3},
                export_options={"useSeparatedCSVFiles": True})[0])),
    ("zero-row override is a real count", ([], [], True),
     _count_check(records=(5, 0), extra_csvs={"objectset_source/object-set-3/Widget__c.csv": "Id\n"})),
    ("ignored rows keep their count exemption", ([], [], True),
     _count_check(records=(999, 999), ignore=True)),
    ("legacy rows without a Pass retain unordered CSV matching", ([], [], True),
     _count_check(records=(3, 5), passes=("", ""))),
    ("legacy repeated counts still cannot reuse a distinct CSV count", 1,
     len(_count_check(records=(5, 5), passes=("", ""))[0])),
    ("file listings retain independent unordered CSV matching", ([], [], True),
     _count_check(extra_readme_lines=["Widget__c.csv # 3 records", "Widget__c.csv # 5 records"])),
    ("JS-truthy separated flag uses the override", ([], [], True), _count_check(flag=[])),
    ("JS-falsy separated flag reads the root", ([], [], True), _count_check(records=(5, 5), flag="")),
]



MIXED_PASS_COUNTS = [
    ("a blank-Pass row cannot reuse the CSV already bound to pass 1", 1,
     len(_count_check(records=(5, 5), passes=(1, ""))[0])),
    ("a blank-Pass row can use the other CSV count", ([], [], True),
     _count_check(passes=(1, ""))),
    ("legacy row order does not affect reserved CSV matching", 1,
     len(_count_check(records=(3, 3), passes=("", 3))[0])),
    ("a legacy row before the bound row can match the remaining source", ([], [], True),
     _count_check(passes=("", 3))),
    ("two explicit passes sharing root reserve it only once for legacy matching", ([], [], True),
     _check([[UPSERT_P1], [UPSERT_P1], [UPDATE_P3]],
            [_row(1, "Widget__c", 1, "Upsert", "Name", 5),
             _row(2, "Widget__c", 2, "Upsert", "Name", 5),
             _row(3, "Widget__c", "", "Update", "Name", 3)],
            csvs={"Widget__c.csv": "Id\n" + "root\n" * 5,
                  "objectset_source/object-set-3/Widget__c.csv": "Id\n" + "other\n" * 3},
            export_options={"useSeparatedCSVFiles": True})),
    ("two legacy rows cannot reuse the sole remaining count in a mixed-count plan", 1,
     len(_check([[UPSERT_P1], [], [UPDATE_P3]],
                [_row(1, "Widget__c", 1, "Upsert", "Name", 5),
                 _row(2, "Widget__c", "", "Update", "Name", 3),
                 _row(3, "Widget__c", "", "Update", "Name", 3)],
                csvs={"Widget__c.csv": "Id\n" + "root\n" * 5,
                      "objectset_source/object-set-3/Widget__c.csv": "Id\n" + "other\n" * 3},
                export_options={"useSeparatedCSVFiles": True})[0])),
]


def _nonwritable_counts(operation, excluded=False, csvs=None):
    config = dict(UPSERT_P1, operation=operation, excluded=excluded)
    return _check([[config]], [_row(1, "Widget__c", 1, operation, "Name", 999)], csvs=csvs)


COUNT_SOURCE_REQUIREMENTS = [
    ("a writable numeric count with no CSV anywhere is an error", 1,
     len(_nonwritable_counts("Upsert")[0])),
    ("a missing-source error names the object and pass", True,
     any("Widget__c" in e and "Pass=1" in e and "no source CSV" in e
         for e in _nonwritable_counts("Upsert")[0])),
    ("Readonly numeric claims without files retain org-count semantics", ([], [], True),
     _nonwritable_counts("Readonly")),
    ("Delete numeric claims do not require a source CSV", ([], [], True),
     _nonwritable_counts("Delete")),
    ("excluded writable declarations do not require a source CSV", ([], [], True),
     _nonwritable_counts("Upsert", excluded=True)),
    ("Readonly optional CSV counts remain checked when a file exists", 1,
     len(_nonwritable_counts("Readonly", csvs={"Widget__c.csv": "Id\none\n"})[0])),
    ("a Readonly pass without its own source does not inherit writable requirements", ([], [], True),
     _check([[dict(UPSERT_P1, operation="Readonly")], [], [UPDATE_P3]],
            [_row(1, "Widget__c", 1, "Readonly", "Name", 3),
             _row(2, "Widget__c", 3, "Update", "Name", 3)],
            csvs={"objectset_source/object-set-3/Widget__c.csv": "Id\n" + "row\n" * 3},
            export_options={"useSeparatedCSVFiles": True})),
]



def _org_marker(operation, records, csvs=None, excluded=False):
    config = dict(UPSERT_P1, operation=operation, excluded=excluded)
    return _check([[config]], [_row(1, "Widget__c", 1, operation, "Name", records)], csvs=csvs)


# pack 151: the `N (org)` marker disambiguates the Records column. It is a HUMAN-supplied assertion
# that the count is *org records* (resolved from the target org), not *file rows* loaded from a CSV,
# so a marked count is never validated against a file — which is what makes deleting an optional
# Readonly CSV correctly silent. The marker is valid only when EVERY matched declaration is
# source-free; if any matched variant is live-writable the count IS file rows, so the marker
# (numbered or bare) is an authoring mistake. The generator never mints `(org)` — it renders `—`.
ORG_COUNT_MARKER = [
    ("`(org)` on a Readonly row is an org-count — file rows are NOT checked even when they differ",
     ([], [], True),
     _org_marker("Readonly", "999 (org)", csvs={"Widget__c.csv": "Id\none\n"})),
    ("control: the same Readonly row WITHOUT the marker is still checked against the file (mismatch → error)",
     1, len(_org_marker("Readonly", "999", csvs={"Widget__c.csv": "Id\none\n"})[0])),
    ("`(org)` on a fileless Readonly row is accepted (org record count, no source required)",
     ([], [], True), _org_marker("Readonly", "2 (org)")),
    ("`(org)` on a live-writable declaration is an authoring mistake — reported",
     True, any("(org) marker on a writable" in e
               for e in _org_marker("Upsert", "5 (org)",
                                    csvs={"Widget__c.csv": "Id\n" + "row\n" * 5})[0])),
    # A blank-Pass row does not resolve to one pass, so the source-binding branch can't fire —
    # but if every variant is live-writable the row is still unambiguously writable, and `(org)`
    # on its file-row count is the same authoring mistake. Without the blank-Pass arm of the
    # guard, `(org)` would silence both the guard and the legacy file check (code-review, 151).
    ("`(org)` on a blank-Pass row whose every variant is live-writable is also reported",
     True, any("(org) marker on a writable" in e
               for e in _check([[UPSERT_P1]],
                               [_row(1, "Widget__c", "", "Upsert", "Name", "5 (org)")],
                               csvs={"Widget__c.csv": "Id\n" + "row\n" * 5})[0])),
    # codex 4022218305: a blank-Pass row matching BOTH a writable and a Readonly variant is
    # rejected — `any_writable`, not `all_writable`. It still vouches for the writable pass's
    # file rows, so `(org)` must not exempt it (was silently accepted when not ALL were writable).
    ("`(org)` on a blank-Pass row matching a writable AND a Readonly variant is reported",
     True, any("(org) marker on a writable" in e
               for e in _check([[UPSERT_P1], [dict(UPSERT_P1, operation="Readonly")]],
                               [_row(1, "Widget__c", "", "", "Name", "999 (org)")],
                               csvs={"Widget__c.csv": "Id\nr\nr\n"})[0])),
    # copilot 4022218776: a bare `(org)` / `— (org)` cell with NO leading integer on a writable
    # row must still be rejected — the guard runs before parse_int(), so a missing number can't
    # let it slip past (previously the whole count block was skipped when claimed was None).
    ("a bare `(org)` (no number) on a writable declaration is still reported",
     True, any("(org) marker on a writable" in e
               for e in _org_marker("Upsert", "(org)",
                                    csvs={"Widget__c.csv": "Id\n" + "row\n" * 5})[0])),
    ("a `— (org)` (dash, no number) on a writable declaration is still reported",
     True, any("(org) marker on a writable" in e
               for e in _org_marker("Upsert", "— (org)",
                                    csvs={"Widget__c.csv": "Id\n" + "row\n" * 5})[0])),
    # A bare `(org)` on a source-free Readonly row is accepted (no number, no file check).
    ("a bare `(org)` (no number) on a Readonly row is accepted",
     ([], [], True), _org_marker("Readonly", "(org)")),
    # copilot 4022398078: a blank-Pass row NAMING the Readonly variant must not bypass the guard.
    # count_variants would narrow `matched` to Readonly, but a blank-Pass row vouches for every
    # pass, so the guard evaluates all compare_variants — the pass-1 Upsert makes it writable.
    ("`(org)` on a blank-Pass row naming Readonly is reported when another pass is writable",
     True, any("(org) marker on a writable" in e
               for e in _check([[UPSERT_P1], [dict(UPSERT_P1, operation="Readonly")]],
                               [_row(1, "Widget__c", "", "Readonly", "Name", "999 (org)")],
                               csvs={"Widget__c.csv": "Id\nr\nr\n"})[0])),
    # ...but when EVERY pass is source-free, a blank-Pass `(org)` row is still legitimately accepted.
    ("`(org)` on a blank-Pass row is accepted when every pass is source-free",
     ([], [], True),
     _check([[dict(UPSERT_P1, operation="Readonly")], [dict(UPSERT_P1, operation="Readonly")]],
            [_row(1, "Widget__c", "", "Readonly", "Name", "5 (org)")])),
    # copilot 4022437332: an explicit Pass does not uniquely identify a declaration when the same
    # object is declared twice in ONE objectSet. A `Pass 1 | Readonly | 999 (org)` row where pass 1
    # also has an Upsert declaration must be reported — the guard evaluates every declaration in the
    # selected pass, not just the operation-named one (seen_specific_passes marks the whole pass).
    ("`(org)` on an explicit-Pass row naming Readonly is reported when the SAME pass has a writable dup",
     True, any("(org) marker on a writable" in e
               for e in _check([[UPSERT_P1, dict(UPSERT_P1, operation="Readonly")]],
                               [_row(1, "Widget__c", 1, "Readonly", "Name", "999 (org)")],
                               csvs={"Widget__c.csv": "Id\nr\nr\n"})[0])),
    ("the marker is case-insensitive and space-tolerant (`( ORG )`)",
     ([], [], True),
     _org_marker("Readonly", "999 ( ORG )", csvs={"Widget__c.csv": "Id\none\n"})),
]


def _same_pass_counts(optional_operation="Readonly", optional_excluded=False,
                      optional_key="Name", writable_count=3, indistinguishable=False):
    optional = dict(UPSERT_P1, operation=optional_operation,
                    excluded=optional_excluded, externalId=optional_key)
    return _check([[], [], [UPSERT_P1, optional]],
                  [_row(1, "Widget__c", 3, "Upsert", "Name", writable_count),
                   _row(2, "Widget__c", 3, optional_operation,
                        "shared key" if indistinguishable else optional_key, 5)],
                  csvs={"Widget__c.csv": "Id\n" + "root\n" * 5,
                        "objectset_source/object-set-3/Widget__c.csv": "Id\n" + "override\n" * 3},
                  export_options={"useSeparatedCSVFiles": True})


SAME_PASS_DECLARATIONS = [
    ("an unspecified externalId cannot suppress a unique writable declaration's count check", 1,
     len(_check([[{"query": "SELECT Id FROM Widget__c", "operation": "Upsert"}]],
                [_row(1, "Widget__c", 1, "Upsert", "Name", 5)])[0])),
    ("Readonly sibling keeps optional counts even beside writable declaration", ([], [], True),
     _same_pass_counts()),
    ("Delete sibling keeps optional counts even beside writable declaration", ([], [], True),
     _same_pass_counts(optional_operation="Delete")),
    ("externalId distinguishes excluded and writable declarations with the same operation",
     ([], [], True), _same_pass_counts(optional_operation="Upsert", optional_excluded=True,
                                     optional_key="OtherKey")),
    ("identical displayed declarations do not prove that a row is writable", ([], [], True),
     _same_pass_counts(optional_operation="Upsert", optional_excluded=True)),
    ("a prose externalId cannot disambiguate excluded and writable variants", ([], [], True),
     _same_pass_counts(optional_operation="Upsert", optional_excluded=True, indistinguishable=True)),
    ("a matched writable row still rejects the other CSV's count", 1,
     len([e for e in _same_pass_counts(writable_count=5)[0] if "Pass=3" in e])),
    ("a writable row distinguished by externalId still binds to its own source", 1,
     len([e for e in _same_pass_counts(optional_operation="Upsert", optional_excluded=True,
                                     optional_key="OtherKey", writable_count=5)[0] if "Pass=3" in e])),
]



def _unmatched_writable_count(count, variants=None):
    variants = variants or [{"query": "SELECT Id FROM Widget__c", "operation": "Upsert"},
                            {"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert"}]
    return _check([variants, [], [UPDATE_P3]],
                  [_row(1, "Widget__c", 1, "Upsert", "Name", count), OTHER_PASS_ROW],
                  csvs={"Widget__c.csv": "Id\n" + "root\n" * 5,
                        "objectset_source/object-set-3/Widget__c.csv": "Id\n" + "override\n" * 3},
                  export_options={"useSeparatedCSVFiles": True})


BOUND_SOURCE_ACCOUNTING = [
    ("unmatched metadata cannot use another source when all pass declarations are writable", 1,
     len(_unmatched_writable_count(3)[0])),
    ("unmatched metadata still accepts the correct root count", ([], [], True),
     _unmatched_writable_count(5)),
    ("a bad bound count still reserves its real source from a legacy row", 2,
     len(_count_check(records=(3, 5), passes=(1, ""))[0])),
    ("the bad bound count and the legacy reuse are each reported at their own row", True,
     all(any(f":{line} " in e for e in _count_check(records=(3, 5), passes=(1, ""))[0])
         for line in (7, 8))),
    ("a bad bound count does not consume the other source's legitimate claim", 1,
     len(_count_check(records=(3, 3), passes=(1, ""))[0])),
    ("failed pass binding reserves its source regardless of table order", 2,
     len(_count_check(records=(3, 5), passes=("", 3))[0])),
]


def _equal_count_claims(passes, copies=1, records=None, operation="Upsert", listing=False):
    records = records if records is not None else [5] * len(passes)
    obj = dict(UPSERT_P1, operation=operation)
    return _check([[obj], [obj]],
                  [_row(i + 1, "Widget__c", pass_no, operation, "Name", count)
                   for i, (pass_no, count) in enumerate(zip(passes, records))],
                  csvs={name: "Id\n" + "row\n" * 5 for name in
                        ["Widget__c.csv"] + [f"archive-{i}/Widget__c.csv" for i in range(copies - 1)]},
                  extra_readme_lines=(["Widget__c.csv # 5 records"] * 3 if listing else None))


EQUAL_COUNT_RESERVATIONS = [
    ("sole root reserved by an explicit pass cannot be reused by a blank pass", 1,
     len(_equal_count_claims([1, ""])[0])),
    ("equal-count reservation works with legacy row first", 1,
     len(_equal_count_claims(["", 1])[0])),
    ("one unreserved equal-count file supports one blank-Pass claim", ([], [], True),
     _equal_count_claims([1, ""], copies=2)),
    ("one unreserved equal-count file cannot support two blank-Pass claims", 1,
     len(_equal_count_claims([1, "", ""], copies=2)[0])),
    ("explicit passes sharing a root reserve it once", ([], [], True),
     _equal_count_claims([1, 2, ""], copies=2)),
    ("wrong bound count still reserves a sole root", 2,
     len(_equal_count_claims([1, ""], records=[3, 5])[0])),
    ("optional pass source also reserves a sole root", 1,
     len(_equal_count_claims([1, ""], operation="Readonly")[0])),
    ("all-legacy equal-count claims keep duplicate semantics", ([], [], True),
     _equal_count_claims(["", "", ""])),
    ("all-explicit rows can share a sole root", ([], [], True),
     _equal_count_claims([1, 2])),
    ("file listings remain independent of equal-count table reservations", ([], [], True),
     _equal_count_claims([1, 2], listing=True)),
]


# pack 169: object_name() delegates to the shared case-insensitive extractor. The old literal
# " FROM " split matched only uppercase, single-space-delimited, and fell through to a `"?"` that
# then vanished from the object table on re-parse. Direct unit cases plus an end-to-end plan.
OBJECT_NAME_CASE_INSENSITIVE = [
    ("lowercase 'from' resolves the object (was silently '?' before)",
     "Widget__c", C.object_name({"query": "SELECT Id, Name from Widget__c"})),
    ("mixed-case 'From' resolves the object",
     "Widget__c", C.object_name({"query": "SELECT Id From Widget__c"})),
    ("uppercase 'FROM' still resolves the object (control)",
     "Widget__c", C.object_name({"query": "SELECT Id FROM Widget__c"})),
    ("tab/newline before the keyword resolves the object",
     "Widget__c", C.object_name({"query": "SELECT Id\n\tFROM Widget__c"})),
    ("a SELECT-clause subquery does not steal the object name",
     "Account", C.object_name({"query": "SELECT Id, (SELECT Id FROM Contacts) FROM Account"})),
    ("a query with no parseable FROM yields a visible Unparseable(...) sentinel, not a silent '?'",
     True, C.object_name({"query": "SELECT Id"}).startswith("Unparseable")),
    # End-to-end: a lowercase-`from` plan object with a correct README row. Before the fix the plan
    # object keyed as `"?"`, so the README's `Widget__c` row referenced an object absent from the
    # plan — a hard ERROR — while the real object silently vanished. After the fix the row matches.
    ("end-to-end: a lowercase-from plan object matches its README row — no error",
     False, _check([[{"query": "SELECT Id from Widget__c", "operation": "Upsert",
                      "externalId": "Name"}]],
                   [_row(1, "Widget__c", 1, "Upsert", "Name")])[0]),
    ("end-to-end: ...and no missing-object warning either",
     False, _check([[{"query": "SELECT Id from Widget__c", "operation": "Upsert",
                      "externalId": "Name"}]],
                   [_row(1, "Widget__c", 1, "Upsert", "Name")])[1]),
]


def main() -> int:
    failures = []
    all_cases = [
        ("object_name() is case-insensitive and subquery-aware (shared extractor)",
         OBJECT_NAME_CASE_INSENSITIVE),
        ("equal-count CSV reservations", EQUAL_COUNT_RESERVATIONS),
        ("bound sources remain authoritative despite bad claims", BOUND_SOURCE_ACCOUNTING),
        ("same-pass declaration matching respects optional rows", SAME_PASS_DECLARATIONS),
        ("mixed explicit and legacy rows preserve distinct-CSV matching", MIXED_PASS_COUNTS),
        ("source requirements respect the declared operation", COUNT_SOURCE_REQUIREMENTS),
        ("the `(org)` marker disambiguates org-record counts from file-row counts", ORG_COUNT_MARKER),
        ("record counts follow the CSV read by the declared pass", PASS_COUNTS),
        ("Pass-column narrowing matches a row against its own pass, not the union", PASS_NARROWING),
        ("no Pass cell falls back to ANY-variant matching", NO_PASS_CELL_FALLBACK),
        ("a Pass cell with a bad value (numeric or not) is reported, never silently matched", BOGUS_PASS),
        ("readme-check: ignore composes with the missing-object seen_objects check", IGNORE_MARKER),
        ("readme-check: omit opts an object out of the missing-object WARN", OMIT_MARKER),
        ("KEYLIKE_RE gates the externalId comparison to literal-looking cells", KEYLIKE_GATING),
        ("a comma-joined Pass cell is reported, not parsed as a single larger number", COMMA_PASS),
        ("missing-object coverage is tracked per-pass, not just per-name", PER_PASS_COVERAGE),
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

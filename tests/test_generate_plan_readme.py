#!/usr/bin/env python3
"""Does `generate_plan_readme.py` actually write what it claims to?

Comment 3901323059 (PR #406, round-21 hosted review, pack 147): no automated test
invoked this module's writer at all — `tests/test_check_plan_readme_consistency.py`
only exercises `check_plan()`'s *parsing* of an already-written README, never
`write_readme()`/`generate_block()`/`resolve_pass_csv()` themselves. That left the
marker-preservation logic, the --force wholesale-replace path, and the per-pass CSV
resolution rule (mirroring `_objects_owing_root_csv`) with no regression guard but the
module's own comments.

Run: `python tests/test_generate_plan_readme.py` (offline, no org).
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
GENERATOR = REPO / "scripts" / "ai" / "generate_plan_readme.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("plan_readme_generator", GENERATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = load_generator()


def _plan(td, export_data, csvs=None):
    plan = pathlib.Path(td) / "plan"
    plan.mkdir()
    (plan / "export.json").write_text(json.dumps(export_data))
    for relpath, body in (csvs or {}).items():
        p = plan / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    return plan


def _csv(n_rows):
    return "Id,Name\n" + "".join(f"{i},Row{i}\n" for i in range(n_rows))


UPSERT_WIDGET = {"query": "SELECT Id FROM Widget__c", "operation": "Upsert", "externalId": "Name"}
READONLY_GADGET = {"query": "SELECT Id FROM Gadget__c", "operation": "Readonly", "externalId": "Name"}
UPSERT_SPROCKET_NO_CSV = {"query": "SELECT Id FROM Sprocket__c", "operation": "Upsert", "externalId": "Name"}


def _case_fresh_write():
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [{"objects": [UPSERT_WIDGET]}]}, {"Widget__c.csv": _csv(3)})
        wrote, message = G.write_readme(str(plan))
        content = (plan / "README.md").read_text()
        return (wrote, "(new)" in message, G.BEGIN_MARKER in content, G.END_MARKER in content,
                "Widget__c" in content, "3" in content)


def _case_regen_preserves_narrative():
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [{"objects": [UPSERT_WIDGET]}]}, {"Widget__c.csv": _csv(3)})
        G.write_readme(str(plan))
        readme = plan / "README.md"
        original = readme.read_text()
        begin_idx = original.find(G.BEGIN_MARKER)
        end_idx = original.find(G.END_MARKER) + len(G.END_MARKER)
        narrated = (original[:begin_idx] + "HAND-WRITTEN INTRO\n\n"
                    + original[begin_idx:end_idx] + "\nHAND-WRITTEN OUTRO\n")
        readme.write_text(narrated)

        # Change the plan (add a second object) and regenerate.
        (plan / "export.json").write_text(json.dumps(
            {"objectSets": [{"objects": [UPSERT_WIDGET, READONLY_GADGET]}]}))
        wrote, message = G.write_readme(str(plan))
        regenerated = readme.read_text()
        return (wrote, "regenerated" in message, "narrative preserved" in message,
                "HAND-WRITTEN INTRO" in regenerated, "HAND-WRITTEN OUTRO" in regenerated,
                "Gadget__c" in regenerated)


def _case_skip_no_markers():
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [{"objects": [UPSERT_WIDGET]}]}, {"Widget__c.csv": _csv(3)})
        readme = plan / "README.md"
        readme.write_text("# Hand-written plan doc, no markers at all.\n")
        wrote, message = G.write_readme(str(plan))
        unchanged = readme.read_text()
        return (wrote, "skip" in message, "--force" in message,
                unchanged == "# Hand-written plan doc, no markers at all.\n")


def _case_force_replaces():
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [{"objects": [UPSERT_WIDGET]}]}, {"Widget__c.csv": _csv(3)})
        readme = plan / "README.md"
        readme.write_text("# Hand-written plan doc, no markers at all.\n")
        wrote, message = G.write_readme(str(plan), force=True)
        replaced = readme.read_text()
        return (wrote, "--force" in message, "replaced whole file" in message,
                "Hand-written plan doc" not in replaced, "Widget__c" in replaced)


def _case_duplicate_markers_skipped():
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [{"objects": [UPSERT_WIDGET]}]}, {"Widget__c.csv": _csv(3)})
        readme = plan / "README.md"
        readme.write_text(
            f"# Doc\n{G.BEGIN_MARKER}\nblock one\n{G.END_MARKER}\n"
            f"stray extra:\n{G.BEGIN_MARKER}\nblock two\n{G.END_MARKER}\n"
        )
        wrote, message = G.write_readme(str(plan))
        return wrote, "skip" in message


WRITE_README = [
    ("a fresh README is written with markers and the object row",
     (True, True, True, True, True, True), _case_fresh_write()),
    ("regenerating preserves hand-written narrative outside the markers, updates the block",
     (True, True, True, True, True, True), _case_regen_preserves_narrative()),
    ("a marker-less README is left untouched without --force",
     (False, True, True, True), _case_skip_no_markers()),
    ("--force replaces a marker-less README wholesale",
     (True, True, True, True, True), _case_force_replaces()),
    ("duplicated markers are treated as 'no clean markers' and skipped without --force",
     (False, True), _case_duplicate_markers_skipped()),
]


def _resolve_case_setup(td, use_separated, override_pass2=True, override_pass1=True):
    plan = _plan(
        td,
        {"objectSets": [{"objects": [UPSERT_WIDGET]}, {"objects": [UPSERT_WIDGET]}],
         "useSeparatedCSVFiles": use_separated},
    )
    (plan / "Widget__c.csv").write_text(_csv(5))
    if override_pass1:
        p1 = plan / "objectset_source" / "object-set-1"
        p1.mkdir(parents=True)
        (p1 / "Widget__c.csv").write_text(_csv(1))
    if override_pass2:
        p2 = plan / "objectset_source" / "object-set-2"
        p2.mkdir(parents=True)
        (p2 / "Widget__c.csv").write_text(_csv(2))
    return plan


def _case_pass1_always_root():
    with tempfile.TemporaryDirectory() as td:
        plan = _resolve_case_setup(td, use_separated=True)
        csv_idx = G.csv_index(str(plan))
        count, relpath = G.resolve_pass_csv(str(plan), csv_idx, True, "Widget__c", 1, {})
        return count, relpath


def _case_pass2_separated_override():
    with tempfile.TemporaryDirectory() as td:
        plan = _resolve_case_setup(td, use_separated=True)
        csv_idx = G.csv_index(str(plan))
        count, relpath = G.resolve_pass_csv(str(plan), csv_idx, True, "Widget__c", 2, {})
        return count, relpath


def _case_pass2_not_separated_falls_back_to_root():
    with tempfile.TemporaryDirectory() as td:
        plan = _resolve_case_setup(td, use_separated=False)
        csv_idx = G.csv_index(str(plan))
        count, relpath = G.resolve_pass_csv(str(plan), csv_idx, False, "Widget__c", 2, {})
        return count, relpath


def _case_no_csv_at_all():
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [{"objects": [UPSERT_WIDGET]}]})
        csv_idx = G.csv_index(str(plan))
        return G.resolve_pass_csv(str(plan), csv_idx, True, "Widget__c", 1, {})


RESOLVE_PASS_CSV = [
    ("pass 1 always reads the root CSV even with an object-set-1 override present",
     (5, "Widget__c.csv"), _case_pass1_always_root()),
    ("pass 2 reads the object-set-2 override when useSeparatedCSVFiles is true",
     (2, str(pathlib.Path("objectset_source") / "object-set-2" / "Widget__c.csv")),
     _case_pass2_separated_override()),
    ("pass 2 falls back to root when useSeparatedCSVFiles is false, even with an override present",
     (5, "Widget__c.csv"), _case_pass2_not_separated_falls_back_to_root()),
    ("an object with no CSV anywhere resolves to (None, None)",
     (None, None), _case_no_csv_at_all()),
]


def _case_generate_block_counts_and_missing():
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(
            td,
            {"objectSets": [{"objects": [UPSERT_WIDGET, READONLY_GADGET, UPSERT_SPROCKET_NO_CSV]}]},
            {"Widget__c.csv": _csv(4)},
        )
        block = G.generate_block(str(plan))
        return ("| 1 |" in block and "Widget__c" in block and "| 4 |" in block,
                "Gadget__c" in block and "—" in block,
                "missing CSV" in block)



def _case_readonly_only_optional_csv_not_required():
    """PR #445 review 4022308405: a Readonly-only plan's optional CSV must NOT be emitted into the
    Files listing — the checker asserts every listed file exists on disk, so listing it would make
    deleting that optional CSV a `no such CSV on disk` error, contradicting the org-resolved
    contract (the row renders `—`). Generate with the CSV, confirm it isn't listed, delete it, and
    confirm the checker stays silent."""
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [{"objects": [READONLY_GADGET]}]}, {"Gadget__c.csv": _csv(3)})
        G.write_readme(str(plan))
        import check_plan_readme_consistency as checker
        content = (plan / "README.md").read_text()
        listed = "Gadget__c.csv" in content  # Files section only (row uses the bare name)
        # The section is labeled for required source CSVs and its empty state says "no required
        # CSVs" (not "no CSVs") — accurate now that an optional CSV may exist but be omitted here
        # (copilot 4022353180). "Delete" is named among the source-free operations too.
        labeled = "## Required source CSVs" in content and "no required CSVs" in content
        (plan / "Gadget__c.csv").unlink()
        errors, warns, _ = checker.check_plan(str(plan))
        return (not listed, labeled, len(errors), warns)


def _case_shared_writable_readonly_csv_still_listed():
    """The caveat to the fix above: a CSV SHARED by a writable declaration must stay listed even
    though a Readonly pass also references it. Upsert(pass1) + Readonly(pass2) on one object over a
    single root CSV — the file is required by pass 1, so it must appear in the Files listing and the
    plan must round-trip cleanly."""
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [{"objects": [UPSERT_WIDGET]}, {"objects": [READONLY_GADGET]}]},
                     {"Widget__c.csv": _csv(4)})
        # Reuse the same object across passes so the physical file is genuinely shared.
        (plan / "export.json").write_text(json.dumps(
            {"objectSets": [{"objects": [UPSERT_WIDGET]},
                            {"objects": [dict(UPSERT_WIDGET, operation="Readonly")]}]}))
        G.write_readme(str(plan))
        import check_plan_readme_consistency as checker
        listed = "Widget__c.csv" in (plan / "README.md").read_text()
        errors, warns, _ = checker.check_plan(str(plan))
        return (listed, len(errors), warns)


def _case_same_pass_duplicate_note():
    """pack 165: the same object declared twice in one pass renders two rows identical in
    every compared cell. The generator must surface it as a visible note (not two silently
    identical rows), and the README must still round-trip through the checker cleanly (the
    note lives below the table where parse_object_tables doesn't look)."""
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [{"objects": [UPSERT_WIDGET, UPSERT_WIDGET]}]},
                     {"Widget__c.csv": _csv(3)})
        G.write_readme(str(plan))
        import check_plan_readme_consistency as checker
        content = (plan / "README.md").read_text()
        errors, warns, _ = checker.check_plan(str(plan))
        rows = list(checker.parse_object_tables(content.splitlines()))
        widget_rows = [r for r in rows if r["object"] == "Widget__c"]
        return ("Same-pass duplicate" in content,
                len(widget_rows) == 2,
                all(checker.parse_pass(r["pass"]) == 1 for r in widget_rows),
                len(errors))


def _case_no_duplicate_note_when_distinct_passes():
    """A legitimately per-pass-varying object (two passes, one declaration each) must NOT
    trigger the note — the '×N in one pass' condition is what matters, not two rows."""
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [{"objects": [UPSERT_WIDGET]}, {"objects": [UPSERT_WIDGET]}]},
                     {"Widget__c.csv": _csv(3)})
        block = G.generate_block(str(plan))
        return "Same-pass duplicate" not in block


def _case_excluded_duplicate_not_noted():
    """A live declaration beside an EXCLUDED one in the same pass is a single load — SFDMU
    drops the excluded ScriptObject before task creation. The generator must count only live
    variants so its note fires on exactly the set validate_sfdmu_v5_datasets.py gates; else
    the README would cite a 'gating HIGH' the validator never raises (pack 165 review)."""
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [{"objects": [
            UPSERT_WIDGET, dict(UPSERT_WIDGET, excluded=True)]}]},
            {"Widget__c.csv": _csv(3)})
        block = G.generate_block(str(plan))
        return "Same-pass duplicate" not in block


def _case_unparseable_duplicate_not_noted():
    """Two identical MALFORMED-query declarations in one pass must NOT be noted. object_name()
    keeps them under an `Unparseable(...)` sentinel so their row stays visible, but the validator's
    `_all_pass_configs` drops them (no object name resolves), so it raises no HIGH — the generator
    must not cite one either (PR #436 review, comment 4018180287)."""
    with tempfile.TemporaryDirectory() as td:
        bad = {"query": "not a query", "operation": "Upsert", "externalId": "Name"}
        plan = _plan(td, {"objectSets": [{"objects": [bad, dict(bad)]}]})
        block = G.generate_block(str(plan))
        return "Same-pass duplicate" not in block


def _case_case_variant_duplicate_noted():
    """`Widget__c` and `widget__c` in one pass are one Salesforce target object (case-insensitive
    API names) loaded twice. The generator groups the note case-insensitively to match the
    validator's HIGH, and names both casings (PR #436 review, Codex comment 4018188326)."""
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [{"objects": [
            UPSERT_WIDGET, dict(UPSERT_WIDGET, query="SELECT Id FROM widget__c")]}]},
            {"Widget__c.csv": _csv(3)})
        block = G.generate_block(str(plan))
        return ("Same-pass duplicate" in block, "Widget__c/widget__c" in block)


def _case_optional_csv_roundtrip(operation, excluded=False):
    """Preserve optional-file documentation while checking writable pass counts."""
    with tempfile.TemporaryDirectory() as td:
        plan = _plan(td, {"objectSets": [
            {"objects": [UPSERT_WIDGET]},
            {"objects": [dict(UPSERT_WIDGET, operation=operation, excluded=excluded)]},
        ]}, {"Widget__c.csv": _csv(4)})
        G.write_readme(str(plan))
        # Import via the generator's canonical module, including the shared resolver.
        import check_plan_readme_consistency as checker
        errors, warns, _ = checker.check_plan(str(plan))
        rows = list(checker.parse_object_tables((plan / "README.md").read_text().splitlines()))
        return [row["records"] for row in rows], errors, warns


def _case_shared_optional_source(operation, excluded=False, same_pass=True,
                                 reverse=False, legacy=False):
    """Generated explicit rows may share a source; blank-Pass rows may not."""
    with tempfile.TemporaryDirectory() as td:
        optional = dict(UPSERT_WIDGET, operation=operation, excluded=excluded)
        if same_pass:
            pair = [UPSERT_WIDGET, optional]
            if reverse:
                pair.reverse()
            sets = [[], [], pair]
        else:
            # The optional second pass falls back to the first pass's root;
            # a third-pass override makes distinct-CSV matching observable.
            sets = [[UPSERT_WIDGET], [optional], [UPSERT_WIDGET]]
        plan = _plan(td, {"useSeparatedCSVFiles": True,
                          "objectSets": [{"objects": objects} for objects in sets]},
                     {"Widget__c.csv": _csv(5),
                      "objectset_source/object-set-3/Widget__c.csv": _csv(3)})
        G.write_readme(str(plan))
        import check_plan_readme_consistency as checker
        readme = plan / "README.md"
        if legacy:
            # Add a blank-Pass row reusing the explicit rows' shared count.
            lines = readme.read_text().splitlines()
            rows = list(checker.parse_object_tables(lines))
            cells = lines[rows[-1]["line"] - 1].split("|")
            header = next(line for line in lines if "| Pass |" in line).split("|")
            cells[header.index(" Pass ")] = " "
            lines.insert(rows[-1]["line"], "|".join(cells))
            readme.write_text("\n".join(lines) + "\n")
        errors, warns, _ = checker.check_plan(str(plan))
        return len(errors), warns


SHARED_OPTIONAL_SOURCES = [
    (f"generated {operation}/{excluded} optional source: same_pass={same_pass}, reverse={reverse}",
     (0, []), _case_shared_optional_source(operation, excluded, same_pass, reverse))
    for operation, excluded in [("Readonly", False), ("Delete", False), ("Upsert", True)]
    for same_pass, reverse in [(True, False), (True, True), (False, False)]
] + [
    (f"blank-Pass row cannot reuse generated optional source: {operation}/{excluded}",
     # pack 151 (revised): a Readonly count is generated as `—` (no org count offline), which the
     # checker never file-matches — so a duplicate blank-Pass `—` row is NOT a reuse conflict
     # (nothing was reserved to reuse). Delete/excluded rows stay bare counts and still flag the
     # reuse, so only the Readonly instance is 0.
     (0 if operation == "Readonly" else 1, []),
     _case_shared_optional_source(operation, excluded, legacy=True))
    for operation, excluded in [("Readonly", False), ("Delete", False), ("Upsert", True)]
]


GENERATE_BLOCK = [
    # pack 151 (revised, PR #445 review): the Readonly pass's count renders `—`, not the optional
    # CSV's row count — the generator has no org count offline and must not relabel file rows as an
    # org count. The writable pass stays a bare `4`. Round-trips cleanly: the checker never
    # file-matches a `—` row, so the optional CSV is documentation, not a load requirement.
    ("writable pass keeps its file count; Readonly pass renders — and round-trips cleanly",
     (["4", "—"], [], []), _case_optional_csv_roundtrip("Readonly")),
    ("writable + Delete passes retain optional-file counts and round-trip cleanly",
     (["4", "4"], [], []), _case_optional_csv_roundtrip("Delete")),
    ("writable + excluded passes retain optional-file counts and round-trip cleanly",
     (["4", "4"], [], []), _case_optional_csv_roundtrip("Update", excluded=True)),
    ("row count reflects the actual CSV, Readonly gets '—', a writable object with no CSV is flagged",
     (True, True, True), _case_generate_block_counts_and_missing()),
    ("a Readonly-only plan's optional CSV is not listed as required; section labeled + deleting it stays silent",
     (True, True, 0, []), _case_readonly_only_optional_csv_not_required()),
    ("a CSV shared by a writable declaration stays listed even when a Readonly pass references it",
     (True, 0, []), _case_shared_writable_readonly_csv_still_listed()),
    ("same-pass duplicate declaration renders a visible note, two Pass-1 rows, and still round-trips",
     (True, True, True, 0), _case_same_pass_duplicate_note()),
    ("an object appearing once per pass across two passes triggers no same-pass note",
     True, _case_no_duplicate_note_when_distinct_passes()),
    ("a live + excluded declaration in one pass triggers no note — only live counts, matching the validator",
     True, _case_excluded_duplicate_not_noted()),
    ("two unparseable-query declarations in one pass trigger no note — the validator drops them, so no HIGH to cite",
     True, _case_unparseable_duplicate_not_noted()),
    ("case-variant declarations in one pass are noted case-insensitively, naming both casings",
     (True, True), _case_case_variant_duplicate_noted()),
]


def main() -> int:
    failures = []
    all_cases = [
        ("generator/checker shared optional source round trips", SHARED_OPTIONAL_SOURCES),
        ("write_readme: fresh write / narrative-preserving regen / skip-without-force / --force / dup-markers",
         WRITE_README),
        ("resolve_pass_csv mirrors the pass-1-always-root, pass-N-separated-override rule", RESOLVE_PASS_CSV),
        ("generate_block: per-object record counts, Readonly dash, missing-CSV flag", GENERATE_BLOCK),
    ]
    print("=" * 100)
    for group, cases in all_cases:
        print(f"-- {group}")
        for label, expect, got in cases:
            ok = got == expect
            if not ok:
                failures.append(label)
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
            if not ok:
                print(f"         expected={expect}, got={got}")
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

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


GENERATE_BLOCK = [
    ("row count reflects the actual CSV, Readonly gets '—', a writable object with no CSV is flagged",
     (True, True, True), _case_generate_block_counts_and_missing()),
]


def main() -> int:
    failures = []
    all_cases = [
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

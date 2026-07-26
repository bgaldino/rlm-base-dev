#!/usr/bin/env python3
"""
Offline invariants for ImportCML's failure reporting.

    python tests/test_rlm_cml_import_failure.py

No org and no CumulusCI install required.

Why this file exists
--------------------
``ImportCML`` calls ``create_record()`` inline as it walks the ESC list, so any
failure part-way leaves the org holding the rows that already succeeded plus the
entire previous generation (step 6, which deletes the old rows, only runs on a
clean pass). There were two ways to fail and they behaved very differently:

A. A reference will not resolve -- ``unresolved_tags`` is non-empty, and the task
   raised. But it raised *before* the step-6 warning, so the operator was never
   told the org had been left holding a mix.

B. ``create_record()`` returned ``None`` while every reference resolved --
   ``import_failed`` was True but ``unresolved_tags`` was empty, so the
   ``if unresolved_tags:`` raise never fired. Execution fell through, the
   ConstraintModel blob uploaded over a partial ESC set, "Import complete" was
   logged, and the task returned **exit 0**. ``prepare_constraints`` runs this
   task, so a build went green carrying a partial constraint model.

B is the dangerous one: a partial apply reported as success. It is the
"reporting without failing" class from REVIEW.md. Both paths now converge on
``describe_esc_import_failure``; a truthy detail means "fail, and do not upload
the blob".

These assert on the decision, not on an exit code -- the old behaviour exited 0,
so an exit-code test would have passed against the bug.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tasks.rlm_cml import (  # noqa: E402
    MAX_INLINE_UNRESOLVED_TAGS,
    describe_esc_import_failure,
)

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}{(' -- ' + detail) if detail else ''}")
        FAILURES.append(label)


print("A successful import reports nothing")
detail, overflow = describe_esc_import_failure(False, [], 57, 57)
check("clean pass yields an empty detail", detail == "", repr(detail))
check("clean pass yields no overflow list", overflow is None, repr(overflow))
# import_failed False dominates: even if a caller passed stray tags, a successful
# run must not be reported as a failure.
detail, _ = describe_esc_import_failure(False, ["StrayTag (Type)"], 57, 57)
check("import_failed=False wins over stray tags", detail == "", repr(detail))

print()
print("Mode A -- an unresolved reference")
detail, overflow = describe_esc_import_failure(
    True, ["QuantumBitDatabaseTokenCommitBounded (Port)"], 57, 56
)
check("reports the unresolved count", "1 ESC association(s) could not be resolved" in detail, detail)
check("names the offending tag", "QuantumBitDatabaseTokenCommitBounded (Port)" in detail, detail)
check("points at the usual cause (qb-pcm)", "qb-pcm" in detail, detail)
check("no overflow list below the cap", overflow is None, repr(overflow))

# Duplicate tags are deduped -- the same tag can appear once per failing row.
detail, _ = describe_esc_import_failure(True, ["Dup (Type)", "Dup (Type)", "Dup (Type)"], 10, 7)
check("duplicate tags are deduped", detail.startswith("1 ESC association(s)"), detail[:60])

print()
print(f"Mode A -- more than {MAX_INLINE_UNRESOLVED_TAGS} unresolved tags truncate")
many = [f"Tag{i:02d} (Type)" for i in range(MAX_INLINE_UNRESOLVED_TAGS + 5)]
detail, overflow = describe_esc_import_failure(True, many, 57, 40)
check("counts every unique tag", f"{len(many)} ESC association(s)" in detail, detail[:70])
check("truncates the inline list", "and 5 more (see log above)" in detail, detail)
check("returns the full list for separate logging", overflow == sorted(many), repr(overflow)[:80])
check(
    "inline list is capped",
    detail.count("(Type)") == MAX_INLINE_UNRESOLVED_TAGS,
    f"found {detail.count('(Type)')}",
)

print()
print("Mode B -- create_record failed while every reference resolved")
# THE REGRESSION THIS FILE EXISTS FOR: this combination used to return success.
detail, overflow = describe_esc_import_failure(True, [], 57, 55)
check("mode B is reported as a failure at all", detail != "", "empty detail == silent partial apply")
check("reports how many rows failed", "2 of 57 ESC record(s) failed" in detail, detail)
check("points at the create errors in the log", "Failed to create ExpressionSetConstraintObj" in detail, detail)
check(
    "distinguishes it from a data-matching problem",
    "API/validation/limit failure" in detail,
    detail,
)
check("does not blame qb-pcm", "qb-pcm" not in detail, detail)
check("no overflow list for mode B", overflow is None, repr(overflow))

# A single failed row still fails.
detail, _ = describe_esc_import_failure(True, [], 57, 56)
check("a single failed create still fails", "1 of 57 ESC record(s) failed" in detail, detail)

# Nothing created at all.
detail, _ = describe_esc_import_failure(True, [], 57, 0)
check("total create failure reports all rows", "57 of 57 ESC record(s) failed" in detail, detail)

print()
print("Mode A takes precedence when both signals are present")
detail, _ = describe_esc_import_failure(True, ["Unresolved (Port)"], 57, 40)
check(
    "unresolved references are reported over create failures",
    "could not be resolved" in detail and "failed to be created" not in detail,
    detail,
)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILING CHECK(S): " + "; ".join(FAILURES))
    sys.exit(1)
print("All checks passed.")

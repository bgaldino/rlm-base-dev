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
    ImportCML,
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
print("=" * 70)
print("SAFETY BEHAVIOUR -- _finalize_esc_import (steps 6-7)")
print("=" * 70)
print("""
The checks above exercise only the message formatter. On their own they would
still pass if _run_task stopped raising, or uploaded the blob before raising --
which is the very behaviour this change exists to guarantee. These drive the
real step 6-7 sequence against a stub and assert on what it *did*.
""".strip())
print()


class _Recorder:
    """Minimal stand-in for the parts of CMLBaseTask that touch an org."""

    def __init__(self):
        self.deleted = []
        self.uploaded = []
        self.logger = self
        self.messages = []

    # logger surface
    def info(self, msg, *a):
        self.messages.append(("info", str(msg) % a if a else str(msg)))

    def warning(self, msg, *a):
        self.messages.append(("warning", str(msg) % a if a else str(msg)))

    def error(self, msg, *a):
        self.messages.append(("error", str(msg) % a if a else str(msg)))

    # org surface
    def delete_record(self, obj, record_id):
        self.deleted.append((obj, record_id))
        return True

    def upload_blob(self, obj, record_id, field, path):
        self.uploaded.append((obj, record_id, field, path))
        return True


def run_finalize(**overrides):
    """Drive ImportCML._finalize_esc_import against a recorder. Returns (rec, raised)."""
    rec = _Recorder()
    kwargs = dict(
        import_failed=False,
        unresolved_tags=[],
        esc_total=57,
        created_count=57,
        existing_esc_ids=["1JE000000000001", "1JE000000000002"],
        dry_run=False,
        esdv={"VersionNumber": "1"},
        devname="QuantumBitComplete_V1",
        # A path that cannot exist, so upload_blob is only reached when the code
        # decides to -- the "Blob file not found" branch still proves we got there.
        blob_dir="/nonexistent-blob-dir",
        esdv_id="9QB000000000001",
    )
    kwargs.update(overrides)
    raised = None
    try:
        ImportCML._finalize_esc_import(rec, **kwargs)
    except Exception as exc:  # noqa: BLE001 -- the type is asserted by the caller
        raised = exc
    return rec, raised


def reached_blob_step(rec):
    """True if execution got as far as step 7 (upload or the not-found warning)."""
    return bool(rec.uploaded) or any("Blob file not found" in m for _, m in rec.messages)


print("Success -- deletes the old rows and proceeds to the blob step")
rec, raised = run_finalize()
check("does not raise", raised is None, repr(raised))
check("deletes every old ESC row", len(rec.deleted) == 2, repr(rec.deleted))
check("reaches the blob upload step", reached_blob_step(rec))
check("logs Import complete", any("Import complete" in m for _, m in rec.messages))

print()
print("Mode B -- create failure with every reference resolved (THE regression)")
rec, raised = run_finalize(import_failed=True, unresolved_tags=[], created_count=55)
check(
    "RAISES -- this path used to fall through and exit 0",
    raised is not None,
    "no exception == the original defect",
)
check("raises CumulusCIFailure", type(raised).__name__ in ("CumulusCIFailure", "Exception"), type(raised).__name__)
check("does NOT upload the blob", not rec.uploaded, repr(rec.uploaded))
check(
    "does NOT reach the blob step at all",
    not reached_blob_step(rec),
    "execution continued past the raise",
)
check("does NOT delete the old rows", not rec.deleted, repr(rec.deleted))
check(
    "warns that the org was left holding both generations",
    any("skipping deletion of old ESC records" in m for lvl, m in rec.messages if lvl == "warning"),
    repr(rec.messages),
)
check("explains the create failure", "failed to be created" in str(raised), str(raised)[:90])
check("says the blob was not uploaded", "NOT uploaded" in str(raised), str(raised)[:90])
check("tells the operator to re-run", "re-run" in str(raised), str(raised)[:90])

print()
print("Mode A -- an unresolved reference")
rec, raised = run_finalize(
    import_failed=True, unresolved_tags=["somethingport (Port)"], created_count=29
)
check("raises", raised is not None)
check("does NOT upload the blob", not rec.uploaded, repr(rec.uploaded))
check("does NOT reach the blob step", not reached_blob_step(rec))
check("does NOT delete the old rows", not rec.deleted, repr(rec.deleted))
check(
    "warns BEFORE raising -- mode A never used to show this",
    any("skipping deletion of old ESC records" in m for lvl, m in rec.messages if lvl == "warning"),
    repr(rec.messages),
)
check("explains the unresolved reference", "could not be resolved" in str(raised), str(raised)[:90])

print()
print("Overflow tags are logged separately, not just truncated into the message")
many = [f"Tag{i:02d} (Type)" for i in range(MAX_INLINE_UNRESOLVED_TAGS + 3)]
rec, raised = run_finalize(import_failed=True, unresolved_tags=many, created_count=10)
check(
    "full tag list reaches the log",
    any("Full unresolved tag list" in m for lvl, m in rec.messages if lvl == "error"),
    repr([m for lvl, m in rec.messages if lvl == "error"])[:120],
)

print()
print("Dry run -- reports without raising and without writing")
rec, raised = run_finalize(import_failed=True, unresolved_tags=["x (Port)"], dry_run=True)
check("does NOT raise on a dry run", raised is None, repr(raised))
check("does NOT upload", not rec.uploaded, repr(rec.uploaded))
check("does NOT delete", not rec.deleted, repr(rec.deleted))
check(
    "logs the failure at error level",
    any(lvl == "error" for lvl, _ in rec.messages),
    repr(rec.messages),
)
check(
    "does not claim the org was changed",
    any("nothing was written" in m for _, m in rec.messages),
    repr(rec.messages),
)
check(
    "does not emit the real-org 'skipping deletion' warning",
    not any("skipping deletion" in m for _, m in rec.messages),
    repr(rec.messages),
)

print()
print("A successful dry run still skips the destructive steps")
rec, raised = run_finalize(dry_run=True)
check("no raise", raised is None, repr(raised))
check("deletes nothing", not rec.deleted, repr(rec.deleted))
check("uploads nothing", not rec.uploaded, repr(rec.uploaded))

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILING CHECK(S): " + "; ".join(FAILURES))
    sys.exit(1)
print("All checks passed.")

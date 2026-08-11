#!/usr/bin/env python3
"""Upload CSV rows into a CSV Based (``CsvUpload``) Decision Table (MUTATING).

A Decision Table has **two layers**: the DEFINITION (columns/source binding) and
the DATA (the rows the engine evaluates). For a ``CsvUpload`` table the rows do
NOT live on a queryable SObject — they are loaded from an uploaded CSV. This tool
performs the **two-phase** load (live-verified 262 / v67.0):

1. Insert a ``ContentVersion`` holding the CSV (its first row must be the column
   headers, matching the table's INPUT/OUTPUT ``fieldName``s) → a ``068…`` id.
2. POST that id to the table's Connect ``/file`` sub-resource
   (``connect/business-rules/decision-table/{0lD…}/file[?versionNumber=N]``).

The import is **asynchronous** — the POST returns *"We are uploading and
processing the CSV file."*; the rows become queryable via the data GET within
seconds (read them with ``dump_decision_table_data.py``). ``uploadStatus``
(``UploadInProgress`` → ``Completed``/``CompletedWithErrors``/``Failed``) lags the
data landing (live-verified: rows queryable in ~5s while ``uploadStatus`` can take
~1 min to go terminal). ``--wait-for-status`` (opt-in) polls that status to a
terminal state and reports it — its value is surfacing ``CompletedWithErrors``
(some rows silently dropped — see per-row validation below) and ``Failed``, which
the fire-and-forget POST response hides.

* **Append (default)** adds the CSV rows to any existing rows. Rows whose values
  don't match a column's ``dataType`` are **dropped silently** and the import
  finishes ``CompletedWithErrors`` (no per-row error is surfaced). Type encodings
  are strict — notably a ``DateTime`` column requires the full
  ``YYYY-MM-DDTHH:MM:SS.sssZ`` form (milliseconds + ``Z``) and a ``Boolean`` accepts
  only case-insensitive ``true``/``false`` (``1``/``0`` are rejected).
* ``--overwrite`` sets ``deleteAllRows:true`` — intended to **delete every existing
  row** before inserting. **⚠ It is REFUSED on the pinned release (262 / v67.0):
  ``deleteAllRows:true`` FAILS reproducibly there** — the import returns
  ``uploadStatus = Failed`` and loads 0 rows (any pre-existing rows are left intact).
  Rather than submit a doomed write and report it as success (and, with
  ``--activate-version``, risk activating the stale prior rows), the tool errors out
  up front. The reliable "replace all rows" path on this release is to **create a
  fresh version/table and append**.

``--activate-version N`` optionally activates version *N* after the upload (Connect
``PATCH .../definitions/{id}/versions/N`` ``{"versionStatus":"Active"}``) so the
table can then be activated for a given date — an explicit version number is
required (the toolkit builds only on the live-verified PATCH shape, not on an
unverified versions-list read).

**Preview by default.** Without ``--confirm`` the tool validates the CSV against
the definition's columns and logs the planned two-phase upload but performs no
write. Re-run with ``--confirm`` to upload.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled here.
``--target-org`` is the *SF CLI* alias (e.g. ``rlm-base__beta``), never the CCI
alias. Pinned to Release 262 / v67.0 (where ``--overwrite`` is refused — see below).

Usage
-----
    # preview (validates CSV headers vs columns; no write), then confirm
    python scripts/decision_tables/upload_decision_table_data.py \
        --target-org rlm-base__scratch --developer-name RLM_MyCsvTable --csv rows.csv
    python scripts/decision_tables/upload_decision_table_data.py \
        --target-org rlm-base__scratch --developer-name RLM_MyCsvTable --csv rows.csv --confirm

    # append into version 1, wait for the import to finish, then activate it
    python scripts/decision_tables/upload_decision_table_data.py \
        --target-org rlm-base__scratch --developer-name RLM_MyCsvTable --csv rows.csv \
        --version-number 1 --wait-for-status --activate-version 1 --confirm
"""

import argparse
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.decision_tables._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    DecisionTableClientError,
    Transport,
    eprint,
)
from scripts.decision_tables._lifecycle import (  # noqa: E402
    _UPLOAD_ERROR,
    LifecycleEngine,
    LifecycleError,
)
from scripts.decision_tables._resolve import ResolveError, load_definition  # noqa: E402


def _read_csv(path):
    """Read the CSV (or stdin for '-') and return (text, header_list)."""
    if path == "-":
        text = sys.stdin.read()
    else:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    if not text.strip():
        raise ValueError("the CSV file is empty.")
    reader = csv.reader(io.StringIO(text))
    header = next(reader, [])
    return text, [h.strip() for h in header]


# The CsvUpload file contract is INPUT/OUTPUT ``fieldName`` headers only.
# ROWCRITERIA columns are row-filter criteria on the definition, NOT columns in
# the uploaded CSV — requiring their headers would reject a valid file before
# Salesforce sees it.
_CSV_HEADER_USAGES = {"INPUT", "OUTPUT"}


def _check_headers(header, defn):
    """Compare CSV headers to the definition's INPUT/OUTPUT column fieldNames.

    Returns ``(missing, extra)``. Only INPUT/OUTPUT columns belong in the uploaded
    CSV (ROWCRITERIA are definition-level row filters, not file columns), so only
    those are required. Missing INPUT/OUTPUT columns are fatal because the platform
    rejects that CSV asynchronously; extra columns remain a warning because a valid
    superset and reordered headers are accepted."""
    columns = {p.get("FieldName") for p in defn.get("parameters", [])
               if p.get("FieldName") and p.get("Usage") in _CSV_HEADER_USAGES}
    if not columns:
        return [], []
    header_set = {h for h in header if h}
    missing = sorted(columns - header_set)
    extra = sorted(header_set - columns)
    return missing, extra


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Upload CSV rows into a CsvUpload Decision Table (two-phase: "
                    "ContentVersion → Connect /file). MUTATING (preview by default; "
                    "--confirm to upload).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--csv", required=True,
                        help="Path to the CSV file ('-' for stdin). First row = column headers.")
    parser.add_argument("--overwrite", action="store_true",
                        help="deleteAllRows:true — intended to DELETE all existing rows "
                             "first. ⚠ REFUSED on 262/v67.0: deleteAllRows:true FAILS "
                             "reproducibly there (uploadStatus=Failed, 0 rows loaded), so "
                             "the tool errors out instead of submitting a doomed write. "
                             "To replace rows, use a fresh version/table + append.")
    parser.add_argument("--version-number", type=int,
                        help="Optional versionNumber to upload into (default: current version).")
    parser.add_argument("--activate-version", type=int, metavar="N",
                        help="After upload, activate version N via the lifecycle engine "
                             "(Connect versions PATCH + fail-closed poll of the table "
                             "Status to Active). The upload targets the SAME version: "
                             "omit --version-number (it defaults to N), or pass the "
                             "matching value — a mismatch is rejected.")
    parser.add_argument("--wait-for-status", action="store_true",
                        help="After upload, poll Metadata.uploadStatus to a terminal "
                             "state and report it (surfaces CompletedWithErrors/Failed "
                             "that the async POST hides). Opt-in: the import can lag ~1 "
                             "min. A terminal CompletedWithErrors/Failed exits non-zero.")
    parser.add_argument("--max-wait", type=int, default=120, metavar="SECONDS",
                        help="Max seconds to poll uploadStatus with --wait-for-status "
                             "(default 120; the import can take ~1 min to go terminal).")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually upload. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    # Fail closed on --overwrite. deleteAllRows:true FAILS reproducibly on the pinned
    # release (uploadStatus=Failed, 0 rows loaded), so submitting it would burn a
    # ContentVersion, report a known-broken operation as "submitted", and — with
    # --activate-version — risk activating the stale prior rows. Refuse up front rather
    # than let a doomed write proceed. To replace all rows on this release, create a
    # fresh version/table and append. (Retained as an option so a caller gets this
    # actionable error, not an argparse "unrecognized argument"; drop the guard if a
    # later release fixes deleteAllRows.)
    if args.overwrite:
        eprint(
            "Error: --overwrite (deleteAllRows:true) is refused on the pinned release "
            "262/v67.0 — it FAILS reproducibly there (uploadStatus=Failed, 0 rows "
            "loaded; existing rows kept). Submitting it would report a known-broken "
            "operation as success and, with --activate-version, could activate the "
            "stale prior rows. To replace all rows, create a fresh version/table and "
            "append.")
        return 1

    # The upload target and the activation target must be the SAME version — uploading
    # into version 2 then activating version 1 would put a different, potentially stale
    # version live while reporting success. If only --activate-version is given, default
    # the upload target to it; if both are given, they must match.
    if args.activate_version is not None:
        if args.version_number is None:
            args.version_number = args.activate_version
        elif args.version_number != args.activate_version:
            eprint(f"Error: --version-number ({args.version_number}) and "
                   f"--activate-version ({args.activate_version}) must be the same "
                   "version — activating a version other than the one just uploaded "
                   "would put a different (possibly stale) version live. Omit "
                   "--version-number to upload into the version being activated.")
            return 1

    try:
        csv_text, header = _read_csv(args.csv)
    except (OSError, ValueError) as exc:
        eprint(f"Error: could not read CSV '{args.csv}': {exc}")
        return 1

    preview = not args.confirm
    transport = Transport(args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)

    try:
        defn = load_definition(transport, args.developer_name)
    except (DecisionTableClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    table_row = defn["table"]
    record_id = table_row["Id"]
    source_type = (defn.get("metadata") or {}).get("dataSourceType") or table_row.get("SourceObject")
    if source_type not in ("CsvUpload", "CSV"):
        eprint(f"Error: '{args.developer_name}' dataSourceType is {source_type!r}, not "
               f"'CsvUpload'. The /file upload only applies to CSV Based Decision Tables.")
        return 1

    # --overwrite is refused up front (see the guard after arg parsing), so the mode
    # is always append past this point.
    eprint(f"\nUpload CSV into DecisionTable '{args.developer_name}' ({record_id}), "
           f"mode=append, version={args.version_number or 'current'}, "
           f"{'PREVIEW' if preview else 'CONFIRM'}")
    missing_headers, extra_headers = _check_headers(header, defn)
    if missing_headers:
        eprint("Error: CSV is missing a header for these definition columns: "
               f"{missing_headers}. The platform rejects this file; no upload submitted.")
        return 1
    if extra_headers:
        eprint(f"  note: CSV has headers with no matching column: {extra_headers}.")
    eprint("Note: the import is async — poll the data GET (dump_decision_table_data.py) "
           "for the rows; uploadStatus lags the data landing.")

    summary = {"action": "upload", "developerName": args.developer_name,
               "id": record_id, "mode": "append",
               "versionNumber": args.version_number, "dryRun": preview}

    if preview:
        eprint("\n[preview] Would (1) insert a ContentVersion with the CSV, then "
               "(2) POST its id to the /file sub-resource"
               + (f", then activate version {args.activate_version}." if args.activate_version
                  else ".")
               + (" Then poll uploadStatus to terminal." if args.wait_for_status else "")
               + " No mutation performed. Re-run with --confirm to upload.")
        if args.json:
            print(json.dumps(summary, indent=2, default=str))
        return 0

    def _emit_failure(phase: str, message: str) -> int:
        # A failure in either phase is a partial mutation. Emit the accumulated
        # --json summary — including fileId once phase 1 created the ContentVersion —
        # so a structured caller can diagnose/clean up the orphan rather than getting
        # empty stdout, then exit 1.
        summary["phase"] = phase
        summary["error"] = message
        eprint(f"\nFAILED: {message}")
        if args.json:
            print(json.dumps(summary, indent=2, default=str))
        return 1

    try:
        # Phase 1 — ContentVersion insert (base64 CSV) → 068… id.
        title = f"DecisionTable {args.developer_name} rows"
        path_on_client = Path(args.csv).name if args.csv != "-" else "decision_table_rows.csv"
        cv = transport.content_version_insert(title, csv_text, path_on_client=path_on_client)
        file_id = cv.get("id") if isinstance(cv, dict) else None
        if not file_id:
            return _emit_failure(
                "content-version",
                f"ContentVersion insert returned no id (response: {cv!r}).")
        summary["fileId"] = file_id

        # Phase 2 — POST the file id to the /file sub-resource (async import).
        # Always append: --overwrite is refused up front, so deleteAllRows is never
        # sent (the client-layer flag stays available for a future release fix).
        upload = transport.upload_decision_table_csv(
            record_id, file_id, version_number=args.version_number,
        )
        summary["upload"] = upload
    except DecisionTableClientError as exc:
        return _emit_failure(
            "file-upload" if summary.get("fileId") else "content-version", str(exc))

    eprint("\nUpload submitted. Confirm the rows landed with "
           "dump_decision_table_data.py --developer-name "
           f"{args.developer_name} --limit 5.")

    # Optional — poll Metadata.uploadStatus to terminal and report it. Surfaces
    # CompletedWithErrors (silent per-row drops) / Failed (e.g. --overwrite) that
    # the fire-and-forget POST response hides. Opt-in because it can lag ~1 min.
    exit_code = 0
    if args.wait_for_status:
        engine = LifecycleEngine(transport, logger=eprint, max_wait_seconds=args.max_wait)
        try:
            final = engine.wait_for_upload_status(record_id)
        except (LifecycleError, DecisionTableClientError) as exc:
            eprint(f"  note: could not read uploadStatus ({exc}); the rows may still "
                   "have landed — confirm with dump_decision_table_data.py.")
            final = None
        summary["uploadStatus"] = final
        if final in _UPLOAD_ERROR:
            eprint(f"  WARNING: uploadStatus = {final} — some or all rows did NOT load "
                   "(bad rows drop silently). "
                   "Inspect what landed with dump_decision_table_data.py.")
            exit_code = 1
        elif final not in ("Completed",):
            eprint(f"  WARNING: uploadStatus did not reach 'Completed' within "
                   f"--max-wait (last seen: {final!r}). The import may still be "
                   f"processing — re-check with dump_decision_table_data.py.")
            exit_code = 1
    elif not args.wait_for_status:
        eprint("  note: the import is async — the rows may not be visible yet. "
               "Pass --wait-for-status to poll uploadStatus to terminal.")

    # Optional — activate a version AFTER confirming the import reached a good
    # terminal state. The outer `exit_code == 0` IS the completed-status gate: when
    # --wait-for-status was passed, the polling block above set exit_code = 1 for
    # every value except uploadStatus == 'Completed', so reaching here with
    # exit_code == 0 proves it completed (no separate `final` re-check needed — that
    # nested guard was unreachable). Without --wait-for-status exit_code stays 0 and
    # we activate fire-and-forget with a warning, since the async import may not have
    # landed yet. (`preview` returned earlier, so this only runs under --confirm.)
    if args.activate_version is not None and exit_code == 0:
        if not args.wait_for_status:
            eprint("  WARNING: activating version without --wait-for-status — the "
                   "async import may not have completed yet. If rows are missing, "
                   "re-upload or wait for uploadStatus=Completed first.")
        engine = LifecycleEngine(transport, logger=eprint, max_wait_seconds=args.max_wait)
        # One guarded block over BOTH the version-status pre-check read and the
        # activation. Route the activation through engine.activate() (NOT a bare
        # Connect PATCH) so it is verified fail-closed: activate() PATCHes the
        # version's versionStatus and then POLLS the table Status to Active — a
        # no-op / partially-applied PATCH therefore fails the poll and raises,
        # instead of a raw 200 being reported as success. The get_version_status
        # pre-check is the idempotency guard (the platform rejects re-activating an
        # already-Active version). Both the read and the guarded activate can raise
        # DecisionTableClientError OR LifecycleError; this runs AFTER the upload
        # already mutated the org, so catching both here turns any activation-phase
        # failure into a WARNING + exit_code=1 while the accumulated JSON summary
        # still emits, rather than escaping main() as a traceback.
        try:
            current = engine.get_version_status(record_id, args.activate_version)
            if current == "Active":
                eprint(f"  Version {args.activate_version} already Active; nothing to do.")
                summary["versionActivation"] = {
                    "versionNumber": args.activate_version, "alreadyActive": True}
            else:
                engine.activate(record_id, version_number=args.activate_version)
                summary["versionActivation"] = {
                    "versionNumber": args.activate_version, "activated": True}
        except (DecisionTableClientError, LifecycleError) as exc:
            eprint(f"  WARNING: version activation failed: {exc}")
            exit_code = 1

    if args.json:
        print(json.dumps(summary, indent=2, default=str))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

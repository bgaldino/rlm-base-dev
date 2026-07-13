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
  row** before inserting. Destructive; use it only on a scratch org. **⚠ WARNING
  (live-verified 262 / v67.0): ``deleteAllRows:true`` currently FAILS reproducibly**
  — the import returns ``uploadStatus = Failed`` and loads 0 rows (any pre-existing
  rows are left intact — safe-fail, nothing is lost). The reliable "replace all
  rows" path on this release is to **create a fresh version/table and append**.

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
alias. Destructive verbs (``--overwrite``) run on **scratch orgs only**, never the
shared ``beta``. Pinned to Release 262 / v67.0.

Usage
-----
    # preview (validates CSV headers vs columns; no write), then confirm
    python scripts/decision_tables/upload_decision_table_data.py \
        --target-org rlm-base__scratch --developer-name RLM_MyCsvTable --csv rows.csv
    python scripts/decision_tables/upload_decision_table_data.py \
        --target-org rlm-base__scratch --developer-name RLM_MyCsvTable --csv rows.csv --confirm

    # overwrite all rows, target version 1, then activate it (scratch only)
    python scripts/decision_tables/upload_decision_table_data.py \
        --target-org rlm-base__scratch --developer-name RLM_MyCsvTable --csv rows.csv \
        --overwrite --version-number 1 --activate-version 1 --confirm
"""

import argparse
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.decision_tables._client import (  # noqa: E402
    DEFINITIONS_PATH,
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


def _check_headers(header, defn):
    """Compare CSV headers to the definition's column fieldNames → list of notes.

    Non-blocking: a header/column mismatch is the most common upload failure, so
    it is surfaced up front, but the upload is not refused (a valid superset or a
    differently-ordered header is legal)."""
    notes = []
    columns = {p.get("FieldName") for p in defn.get("parameters", []) if p.get("FieldName")}
    if not columns:
        return notes
    header_set = {h for h in header if h}
    missing = sorted(columns - header_set)
    extra = sorted(header_set - columns)
    if missing:
        notes.append(f"CSV is missing a header for these columns: {missing}.")
    if extra:
        notes.append(f"CSV has headers with no matching column: {extra}.")
    return notes


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
                             "first (destructive; scratch orgs only). Default: append. "
                             "⚠ WARNING: deleteAllRows:true FAILS on 262/v67.0 "
                             "(uploadStatus=Failed, 0 rows loaded; existing rows kept). "
                             "To replace rows, use a fresh version/table + append.")
    parser.add_argument("--version-number", type=int,
                        help="Optional versionNumber to upload into (default: current version).")
    parser.add_argument("--activate-version", type=int, metavar="N",
                        help="After upload, activate version N (Connect versions PATCH).")
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
        eprint(f"Warning: '{args.developer_name}' dataSourceType is {source_type!r}, not "
               f"'CsvUpload'. The /file upload only applies to CSV Based Decision Tables.")

    mode = "OVERWRITE (deleteAllRows)" if args.overwrite else "append"
    eprint(f"\nUpload CSV into DecisionTable '{args.developer_name}' ({record_id}), "
           f"mode={mode}, version={args.version_number or 'current'}, "
           f"{'PREVIEW' if preview else 'CONFIRM'}")
    for note in _check_headers(header, defn):
        eprint(f"  note: {note}")
    eprint("Note: the import is async — poll the data GET (dump_decision_table_data.py) "
           "for the rows; uploadStatus lags the data landing.")

    summary = {"action": "upload", "developerName": args.developer_name,
               "id": record_id, "mode": "overwrite" if args.overwrite else "append",
               "versionNumber": args.version_number, "dryRun": preview}

    if args.overwrite:
        eprint("  WARNING: --overwrite (deleteAllRows:true) FAILS reproducibly on "
               "262/v67.0 (uploadStatus=Failed, 0 rows loaded; existing rows kept). "
               "To replace all rows, create a fresh version/table and append.")

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

    try:
        # Phase 1 — ContentVersion insert (base64 CSV) → 068… id.
        title = f"DecisionTable {args.developer_name} rows"
        path_on_client = Path(args.csv).name if args.csv != "-" else "decision_table_rows.csv"
        cv = transport.content_version_insert(title, csv_text, path_on_client=path_on_client)
        file_id = cv.get("id") if isinstance(cv, dict) else None
        if not file_id:
            eprint(f"\nFAILED: ContentVersion insert returned no id (response: {cv!r}).")
            return 1
        summary["fileId"] = file_id

        # Phase 2 — POST the file id to the /file sub-resource (async import).
        upload = transport.upload_decision_table_csv(
            record_id, file_id, delete_all_rows=args.overwrite,
            version_number=args.version_number,
        )
        summary["upload"] = upload

        # Optional — activate the uploaded version (live-verified PATCH shape).
        if args.activate_version is not None:
            vpath = f"{DEFINITIONS_PATH}/{record_id}/versions/{int(args.activate_version)}"
            vresp = transport.connect("PATCH", vpath, {"versionStatus": "Active"})
            summary["versionActivation"] = vresp
    except DecisionTableClientError as exc:
        eprint(f"\nFAILED: {exc}")
        return 1

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
                   "(bad rows drop silently; --overwrite fails on this release). "
                   "Inspect what landed with dump_decision_table_data.py.")
            exit_code = 1

    if args.json:
        print(json.dumps(summary, indent=2, default=str))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

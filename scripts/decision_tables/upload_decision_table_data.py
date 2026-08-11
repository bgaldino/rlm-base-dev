#!/usr/bin/env python3
"""Upload CSV rows into a CSV Based (``CsvUpload``) Decision Table (MUTATING).

A Decision Table has **two layers**: the DEFINITION (columns/source binding) and
the DATA (the rows the engine evaluates). For a ``CsvUpload`` table the rows do
NOT live on a queryable SObject — they are loaded from an uploaded CSV. This tool
performs the **two-phase** load (live-verified 262 / v67.0):

1. Insert a ``ContentVersion`` holding the CSV (its first row must be the column
   headers, matching the table's INPUT/OUTPUT ``fieldName``s) → a ``068…`` id.
2. POST that id to the table's Connect ``/file`` sub-resource
   (``connect/business-rules/decision-table/{0lD…}/file``).

The rows are **appended** to any existing rows. Rows whose values don't match a
column's ``dataType`` are **dropped silently** and the import finishes
``CompletedWithErrors`` — the async POST response does not surface that. Type
encodings are strict — notably a ``DateTime`` column requires the full
``YYYY-MM-DDTHH:MM:SS.sssZ`` form (milliseconds + ``Z``) and a ``Boolean`` accepts
only case-insensitive ``true``/``false`` (``1``/``0`` are rejected).

The import is **asynchronous** — the POST returns *"We are uploading and
processing the CSV file."*; the rows become queryable via the data GET within
seconds. **This tool does one thing — load the rows — and returns.** Read back
what landed with ``dump_decision_table_data.py`` (that is also how you catch
silently-dropped rows). To activate the table's version afterward, run
``activate_decision_table.py`` (a single-version CsvUpload table has one version;
the lifecycle engine resolves and activates it).

**Preview by default.** Without ``--confirm`` the tool validates the CSV against
the definition's columns and logs the planned two-phase upload but performs no
write. Re-run with ``--confirm`` to upload.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled here.
``--target-org`` is the *SF CLI* alias (e.g. ``rlm-base__beta``), never the CCI
alias. Pinned to Release 262 / v67.0.

Usage
-----
    # preview (validates CSV headers vs columns; no write), then confirm
    python scripts/decision_tables/upload_decision_table_data.py \
        --target-org rlm-base__scratch --developer-name RLM_MyCsvTable --csv rows.csv
    python scripts/decision_tables/upload_decision_table_data.py \
        --target-org rlm-base__scratch --developer-name RLM_MyCsvTable --csv rows.csv --confirm
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
    fail_json,
)
from scripts.decision_tables._resolve import ResolveError, load_definition  # noqa: E402


def _read_csv(path):
    """Read the CSV (or stdin for '-') and return (text, header_list).

    Open files as ``utf-8-sig`` so a UTF-8 BOM (Excel writes one by default) is
    consumed rather than left on the first header as U+FEFF. For stdin the bytes
    are already decoded, so strip a leading BOM from the text. Without this the
    first header parses as ``\ufeffFieldName`` and header validation reports the
    real column missing plus a phantom extra one, refusing a valid file."""
    if path == "-":
        text = sys.stdin.read().lstrip("\ufeff")
    else:
        with open(path, encoding="utf-8-sig") as fh:
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
        description="Append CSV rows to a CsvUpload Decision Table (two-phase: "
                    "ContentVersion → Connect /file). MUTATING (preview by default; "
                    "--confirm to upload). Activate afterward with "
                    "activate_decision_table.py.",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--csv", required=True,
                        help="Path to the CSV file ('-' for stdin). First row = column headers.")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually upload. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    try:
        csv_text, header = _read_csv(args.csv)
    except (OSError, ValueError) as exc:
        return fail_json(args.json, f"Error: could not read CSV '{args.csv}': {exc}",
                         {"action": "upload", "developerName": args.developer_name})

    preview = not args.confirm
    transport = Transport(args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)

    try:
        defn = load_definition(transport, args.developer_name)
    except (DecisionTableClientError, ResolveError) as exc:
        return fail_json(args.json, f"Error: {exc}",
                         {"action": "upload", "developerName": args.developer_name})

    table_row = defn["table"]
    record_id = table_row["Id"]
    source_type = (defn.get("metadata") or {}).get("dataSourceType") or table_row.get("SourceObject")
    if source_type not in ("CsvUpload", "CSV"):
        return fail_json(
            args.json,
            f"Error: '{args.developer_name}' dataSourceType is {source_type!r}, not "
            f"'CsvUpload'. The /file upload only applies to CSV Based Decision Tables.",
            {"action": "upload", "developerName": args.developer_name, "id": record_id})

    eprint(f"\nUpload CSV into DecisionTable '{args.developer_name}' ({record_id}), "
           f"mode=append, {'PREVIEW' if preview else 'CONFIRM'}")
    missing_headers, extra_headers = _check_headers(header, defn)
    if missing_headers:
        return fail_json(
            args.json,
            "Error: CSV is missing a header for these definition columns: "
            f"{missing_headers}. The platform rejects this file; no upload submitted.",
            {"action": "upload", "developerName": args.developer_name, "id": record_id})
    if extra_headers:
        eprint(f"  note: CSV has headers with no matching column: {extra_headers}.")

    summary = {"action": "upload", "developerName": args.developer_name,
               "id": record_id, "mode": "append", "dryRun": preview}

    if preview:
        eprint("\n[preview] Would (1) insert a ContentVersion with the CSV, then "
               "(2) POST its id to the /file sub-resource. No mutation performed. "
               "Re-run with --confirm to upload.")
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
        upload = transport.upload_decision_table_csv(record_id, file_id)
        summary["upload"] = upload
    except DecisionTableClientError as exc:
        return _emit_failure(
            "file-upload" if summary.get("fileId") else "content-version", str(exc))

    eprint("\nUpload submitted (async). Confirm the rows landed — and catch any "
           "silently-dropped rows — with dump_decision_table_data.py --developer-name "
           f"{args.developer_name} --limit 5. Activate the version with "
           "activate_decision_table.py.")

    if args.json:
        print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

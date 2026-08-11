#!/usr/bin/env python3
"""Replace an existing BRE Decision Table definition through Tooling API.

The command sends the complete Metadata value in one request and returns
platform errors directly. Active tables must be deactivated explicitly first.
Writing requires ``--confirm``.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.decision_tables import _payload  # noqa: E402
from scripts.decision_tables._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    DecisionTableClientError,
    Transport,
    eprint,
    fail_json,
)
from scripts.decision_tables._resolve import ResolveError, resolve_decision_table  # noqa: E402
from scripts.decision_tables._schema import validate_spec  # noqa: E402


def _load_spec(path):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Update an existing BRE Decision Table from a canonical spec. "
                    "MUTATING (preview by default; --confirm to apply).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias or username; not a CCI org alias.",
    )
    parser.add_argument("--spec", required=True,
                        help="Path to the canonical spec JSON ('-' for stdin).")
    parser.add_argument("--developer-name",
                        help="DecisionTable DeveloperName (default: the spec's fullName).")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually apply. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    try:
        spec = _load_spec(args.spec)
    except (OSError, ValueError) as exc:
        return fail_json(args.json, f"Error: could not read spec '{args.spec}': {exc}")

    result = validate_spec(spec)
    eprint(result.format_report())
    if not result.passed:
        return fail_json(args.json, "Spec has errors; not updating. Fix them and retry.",
                         {"action": "update"})

    dev_name = args.developer_name or spec.get("fullName")
    if not dev_name:
        return fail_json(
            args.json,
            "Error: no DeveloperName — pass --developer-name or set fullName in the spec.")

    preview = not args.confirm
    transport = Transport(args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    summary = {"action": "update", "path": "tooling", "developerName": dev_name,
               "dryRun": preview}

    try:
        table_row = resolve_decision_table(transport, dev_name)
    except (DecisionTableClientError, ResolveError) as exc:
        return fail_json(args.json, f"Error: {exc}", summary)

    record_id = table_row["Id"]
    summary["id"] = record_id
    eprint(f"\nUpdate DecisionTable '{dev_name}' ({record_id}) via Tooling, "
           f"status={table_row.get('Status')}, "
           f"{'PREVIEW' if preview else 'CONFIRM'}")

    # Tooling Metadata PATCH requires status. Reuse the status returned by the
    # resolve query and let Salesforce enforce lifecycle state and payload validity.
    live_status = table_row.get("Status")
    if not live_status:
        return fail_json(
            args.json,
            f"Error: DecisionTable/{record_id} returned no Status; cannot build the "
            "required Metadata payload.",
            summary,
        )
    body = _payload.tooling_metadata_only(spec, live_status=live_status)
    try:
        transport.tooling_sobject("PATCH", "DecisionTable", record_id, body=body)
    except DecisionTableClientError as exc:
        return fail_json(args.json, str(exc), summary)

    if preview:
        eprint("\n[preview] No mutation performed. Re-run with --confirm to apply.")
    else:
        eprint("\nUpdate complete. Verify with describe_decision_table.py "
               "(parameters are a full replace; GET-back to confirm).")
    if args.json:
        print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

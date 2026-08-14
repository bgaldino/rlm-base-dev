#!/usr/bin/env python3
"""Delete a BRE Decision Table through Tooling API.

The command previews by default and requires ``--confirm``. It sends one delete
request and returns platform lifecycle or dependency errors to the caller.
"""

import argparse
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
from scripts.decision_tables._resolve import ResolveError, resolve_decision_table  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Delete a BRE Decision Table. DESTRUCTIVE (preview by default; "
                    "--confirm REQUIRED to delete).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias or username; not a CCI org alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--confirm", action="store_true",
                        help="REQUIRED to actually delete. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    preview = not args.confirm
    transport = Transport(args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    try:
        table_row = resolve_decision_table(transport, args.developer_name)
    except (DecisionTableClientError, ResolveError) as exc:
        return fail_json(args.json, f"Error: {exc}",
                         {"action": "delete", "developerName": args.developer_name,
                          "deleted": False})

    record_id = table_row["Id"]
    current = table_row.get("Status")
    eprint(f"\nDelete DecisionTable '{args.developer_name}' ({record_id}), "
           f"currently Status={current}, "
           f"{'PREVIEW' if preview else 'CONFIRM'}")

    try:
        transport.tooling_sobject("DELETE", "DecisionTable", record_id)
    except DecisionTableClientError as exc:
        return fail_json(
            args.json, str(exc),
            {"action": "delete", "developerName": args.developer_name,
             "id": record_id, "deleted": False})

    if preview:
        eprint("\n[preview] No deletion performed. Re-run with --confirm to delete.")
    else:
        eprint("\nDeletion complete. Verify with list_decision_tables.py "
               "(the table should no longer appear).")
    if args.json:
        print(json.dumps({"action": "delete", "path": "tooling",
                          "developerName": args.developer_name, "id": record_id,
                          "deleted": not preview, "dryRun": preview},
                         indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

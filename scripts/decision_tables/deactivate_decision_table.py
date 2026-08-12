#!/usr/bin/env python3
"""Deactivate a BRE Decision Table (mutating, preview by default).

SObject-backed tables use Tooling status. CSV-backed tables deactivate their
unambiguous file-import version through Connect. Platform dependency errors are
returned to the caller. Writing requires ``--confirm``.
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
from scripts.decision_tables._lifecycle import LifecycleEngine, LifecycleError  # noqa: E402
from scripts.decision_tables._resolve import ResolveError, resolve_decision_table  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Deactivate a BRE Decision Table (Status → Inactive, synchronous). "
                    "MUTATING (preview by default; --confirm to apply).",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias or username; not a CCI org alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--confirm", action="store_true",
                        help="Actually deactivate. Without it, only PREVIEWS.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit a result summary as JSON.")
    args = parser.parse_args(argv)

    preview = not args.confirm
    transport = Transport(args.target_org, api_version=args.api_version,
                          dry_run=preview, logger=eprint)
    engine = LifecycleEngine(transport, logger=eprint)

    try:
        table_row = resolve_decision_table(transport, args.developer_name)
    except (DecisionTableClientError, ResolveError) as exc:
        return fail_json(args.json, f"Error: {exc}",
                         {"action": "deactivate", "developerName": args.developer_name})

    record_id = table_row["Id"]
    current = table_row.get("Status")
    eprint(f"\nDeactivate DecisionTable '{args.developer_name}' ({record_id}), "
           f"currently Status={current}, {'PREVIEW' if preview else 'CONFIRM'}")

    if current in ("Inactive", "Draft"):
        eprint(f"Table already Status={current}; nothing to do.")
    else:
        try:
            engine.deactivate(record_id)
        except (DecisionTableClientError, LifecycleError) as exc:
            return fail_json(args.json, f"FAILED: {exc}",
                             {"action": "deactivate", "developerName": args.developer_name,
                              "id": record_id})

    if preview:
        eprint("\n[preview] No mutation performed. Re-run with --confirm to apply.")
    if args.json:
        print(json.dumps({"action": "deactivate", "developerName": args.developer_name,
                          "id": record_id, "dryRun": preview}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

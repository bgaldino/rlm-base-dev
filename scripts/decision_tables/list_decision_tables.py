#!/usr/bin/env python3
"""List BRE Decision Tables through Tooling API (read-only)."""

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
)
from scripts.decision_tables._resolve import list_decision_tables  # noqa: E402


def _print_grouped(rows):
    if not rows:
        print("(no decision tables found)")
        return
    by_usage = {}
    for r in rows:
        by_usage.setdefault(r.get("UsageType") or "(none)", []).append(r)
    print(f"{len(rows)} decision table(s), {len(by_usage)} usageType(s):\n")
    for usage in sorted(by_usage):
        group = by_usage[usage]
        print(f"  {usage}  ({len(group)})")
        for r in sorted(group, key=lambda x: x.get("DeveloperName") or ""):
            status = r.get("Status") or "-"
            src = r.get("SourceObject") or "-"
            synced = r.get("LastSyncDate") or "never"
            print(f"    - {r.get('DeveloperName')}   status={status}   "
                  f"source={src}   lastSync={synced}   id={r.get('Id')}")
        print()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="List BRE Decision Tables grouped by usageType. Read-only.",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias or username; not a CCI org alias.",
    )
    parser.add_argument("--status", help="Filter by Status (Active / Inactive / Draft).")
    parser.add_argument("--usage-type", help="Filter by UsageType (e.g. DefaultPricing).")
    parser.add_argument(
        "--developer-name",
        help="Filter to one or more DecisionTable DeveloperNames (comma-separated).",
    )
    parser.add_argument("--limit", type=int, help="Cap the number of rows returned.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit rows as JSON.")
    args = parser.parse_args(argv)

    transport = Transport(args.target_org, api_version=args.api_version)
    try:
        rows = list_decision_tables(
            transport,
            status=args.status,
            usage_type=args.usage_type,
            developer_name=args.developer_name,
            limit=args.limit,
        )
    except DecisionTableClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    if args.json:
        print(json.dumps(rows, indent=2))
        return 0

    _print_grouped(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

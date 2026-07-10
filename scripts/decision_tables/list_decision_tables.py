#!/usr/bin/env python3
"""List BRE Decision Tables in an org, grouped by usageType (read-only).

Surfaces every ``DecisionTable`` (Tooling API) with its ``UsageType``
(DefaultPricing / DefaultRating / RatingDiscovery / PricingDiscovery /
RevenueStandardTax / …), ``Status``, ``SourceObject``, and ``LastSyncDate`` —
the "what tables exist, of what kind, and when were they last synced?" view.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens are handled
here. ``--target-org`` is the *SF CLI* alias (e.g. ``rlm-base__beta``), never the
CCI alias. Read-only: never mutates. Pinned to Release 262 / v67.0.

Usage
-----
    # every decision table, grouped by usageType
    python scripts/decision_tables/list_decision_tables.py \
        --target-org rlm-base__beta

    # only active pricing tables
    python scripts/decision_tables/list_decision_tables.py \
        --target-org rlm-base__beta --usage-type DefaultPricing --status Active

    # specific tables as JSON
    python scripts/decision_tables/list_decision_tables.py \
        --target-org rlm-base__beta \
        --developer-name RLM_CostBookEntries,RLM_ProductQualification --json
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
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
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

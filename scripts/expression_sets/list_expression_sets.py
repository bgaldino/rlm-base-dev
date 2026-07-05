#!/usr/bin/env python3
"""List BRE Expression Sets in an org, one row per set (read-only).

Surfaces the Revenue Cloud **type taxonomy** for every expression set: the
``interfaceSourceType`` (PricingProcedure / DiscoveryProcedure / RatingProcedure
/ RatingDiscoveryProcedure / QualificationProcedure / Constraint / …) and
``usageType`` live on the runtime ``ExpressionSet`` record — NOT the tooling
``ExpressionSetDefinition`` — so this is the query that answers "what kind of
procedure is this, and which version is live?".

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens are handled
here. ``--target-org`` is the *SF CLI* alias (e.g. ``rlm-base__july4_ctxPilot``),
never the CCI alias. Read-only: never mutates. Pinned to Release 262 / v67.0.

Usage
-----
    # every expression set, grouped by interfaceSourceType
    python scripts/expression_sets/list_expression_sets.py \
        --target-org rlm-base__july4_ctxPilot

    # one set, with its full version list (active first)
    python scripts/expression_sets/list_expression_sets.py \
        --target-org rlm-base__july4_ctxPilot \
        --developer-name RLM_DefaultPricingProcedure --versions

    # only pricing procedures, as JSON
    python scripts/expression_sets/list_expression_sets.py \
        --target-org rlm-base__july4_ctxPilot \
        --type PricingProcedure --json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.expression_sets._client import (  # noqa: E402
    DEFAULT_API_VERSION,
    ExpressionSetClientError,
    eprint,
)
from scripts.expression_sets._resolve import (  # noqa: E402
    list_expression_sets,
    list_versions,
)


def _print_grouped(rows, show_versions, target_org, api_version):
    if not rows:
        print("(no expression sets found)")
        return
    by_type = {}
    for r in rows:
        by_type.setdefault(r.get("interfaceSourceType") or "(none)", []).append(r)
    total = len(rows)
    print(f"{total} expression set(s), {len(by_type)} type(s):\n")
    for itype in sorted(by_type):
        group = by_type[itype]
        print(f"  {itype}  ({len(group)})")
        for r in sorted(group, key=lambda x: x.get("developerName") or ""):
            usage = r.get("usageType") or "-"
            sub = f"/{r['usageSubtype']}" if r.get("usageSubtype") else ""
            print(f"    - {r.get('developerName')}   usage={usage}{sub}   id={r.get('id')}")
            if show_versions:
                try:
                    versions = list_versions(
                        r["id"], target_org=target_org, api_version=api_version
                    )
                except ExpressionSetClientError as exc:
                    eprint(f"      (could not list versions: {exc})")
                    versions = []
                for v in versions:
                    active = " [ACTIVE]" if v.get("IsActive") else ""
                    print(f"        v{v.get('VersionNumber')}: {v.get('ApiName')}{active}")
        print()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="List BRE Expression Sets with their Revenue Cloud type "
                    "(interfaceSourceType) and active version. Read-only.",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__july4_ctxPilot) — NOT the CCI alias.",
    )
    parser.add_argument(
        "--developer-name",
        help="Filter to one expression set by ExpressionSetDefinition DeveloperName.",
    )
    parser.add_argument(
        "--type", dest="interface_type",
        help="Filter to one interfaceSourceType (e.g. PricingProcedure).",
    )
    parser.add_argument(
        "--versions", action="store_true",
        help="Also list every ExpressionSetVersion (active first) per set.",
    )
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit rows as JSON.")
    args = parser.parse_args(argv)

    try:
        rows = list_expression_sets(
            target_org=args.target_org, api_version=args.api_version,
            developer_name=args.developer_name,
        )
    except ExpressionSetClientError as exc:
        eprint(f"Error: {exc}")
        return 1

    if args.interface_type:
        want = args.interface_type.lower()
        rows = [r for r in rows if (r.get("interfaceSourceType") or "").lower() == want]

    if args.versions:
        for r in rows:
            try:
                r["versions"] = list_versions(
                    r["id"], target_org=args.target_org, api_version=args.api_version
                )
            except ExpressionSetClientError:
                r["versions"] = []

    if args.json:
        print(json.dumps(rows, indent=2))
        return 0

    _print_grouped(rows, args.versions, args.target_org, args.api_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

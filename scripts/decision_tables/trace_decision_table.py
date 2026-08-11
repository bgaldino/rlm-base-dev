#!/usr/bin/env python3
"""Trace pricing recipes that reference a BRE Decision Table (read-only).

The command resolves definitions through Tooling, queries
``PricingRecipeTableMapping`` through REST, and correlates on ``LookupTableId``
or ``FileBasedDecisionTableName``.
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
    soql_literal,
)
from scripts.decision_tables._resolve import (  # noqa: E402
    ResolveError,
    resolve_decision_table,
)

_MAPPING_COLUMNS = (
    "Id", "PricingRecipeId", "PricingComponentType", "LookupTableId",
    "IsInternal", "FileBasedDecisionTableName",
)


def trace_recipe_mappings(transport, table):
    """Return the PricingRecipeTableMapping rows referencing ``table`` (a summary row).

    Matches on ``LookupTableId`` (== DecisionTable.Id, SObject-backed) OR
    ``FileBasedDecisionTableName`` (== DeveloperName, file/CSV-backed).
    """
    dt_id = table["Id"]
    dev_name = table["DeveloperName"]
    # The mapping's LookupTableId holds the 15- or 18-char DecisionTable Id;
    # match on the 15-char prefix so either form resolves.
    dt_id_15 = dt_id[:15]
    soql = (
        f"SELECT {', '.join(_MAPPING_COLUMNS)} FROM PricingRecipeTableMapping "
        f"WHERE LookupTableId = '{soql_literal(dt_id)}' "
        f"OR LookupTableId = '{soql_literal(dt_id_15)}' "
        f"OR FileBasedDecisionTableName = '{soql_literal(dev_name)}'"
    )
    return transport.soql(soql)


def _print_trace(table, mappings):
    print(f"Decision Table: {table.get('DeveloperName')}  ({table.get('Id')})")
    print(f"  usageType : {table.get('UsageType')}   status: {table.get('Status')}")
    if not mappings:
        print("\n  No pricing-recipe table mappings reference this table.")
        return
    by_recipe = {}
    for m in mappings:
        by_recipe.setdefault(m.get("PricingRecipeId") or "(none)", []).append(m)
    print(f"\n  Referenced by {len(mappings)} mapping(s) across {len(by_recipe)} recipe(s):")
    for recipe_id in sorted(by_recipe):
        print(f"    recipe {recipe_id}:")
        for m in by_recipe[recipe_id]:
            via = ("LookupTableId" if m.get("LookupTableId")
                   else "FileBasedDecisionTableName")
            internal = " [internal]" if m.get("IsInternal") else ""
            print(f"      - {m.get('PricingComponentType')}  (via {via}){internal}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Trace which pricing recipes reference a Decision Table. Read-only.",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias or username; not a CCI org alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit the trace as JSON.")
    args = parser.parse_args(argv)

    transport = Transport(args.target_org, api_version=args.api_version)
    try:
        table = resolve_decision_table(transport, args.developer_name)
        mappings = trace_recipe_mappings(transport, table)
    except (DecisionTableClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    if args.json:
        print(json.dumps({"table": table, "mappings": mappings}, indent=2, default=str))
        return 0

    _print_trace(table, mappings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Print one Decision Table's Tooling definition (read-only)."""

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
from scripts.decision_tables._resolve import (  # noqa: E402
    ResolveError,
    load_definition,
    tristate_bool,
)


def _print_definition(defn):
    table = defn["table"]
    meta_early = defn.get("metadata") or {}
    # The per-table label is SetupName (also metadata.setupName). MasterLabel is the
    # constant object label "Decision Tables" on every row — never identify a table
    # by it.
    label = table.get("SetupName") or meta_early.get("setupName") or "-"
    print(f"Decision Table: {table.get('DeveloperName')}   ({table.get('Id')})")
    print(f"  label        : {label}")
    print(f"  status       : {table.get('Status')}")
    print(f"  usageType    : {table.get('UsageType')}")
    print(f"  sourceObject : {table.get('SourceObject') or '-'}")
    print(f"  lastSync     : {table.get('LastSyncDate') or 'never'}")
    print(f"  lastIncrSync : {table.get('LastIncrementalSyncDate') or 'never'}")

    meta = defn.get("metadata") or {}
    if meta:
        # The precondition for refresh_decision_table.py --incremental: with this
        # false the action accepts an incremental request and syncs nothing.
        incremental = tristate_bool(meta.get("isIncrementalSyncEnabled"))
        print("  incrSync     : " + {True: "enabled", False: "disabled",
                                     None: "unknown"}[incremental])
        print(f"  dataSource   : {meta.get('dataSourceType')}")
        print(f"  execution    : {meta.get('executionType')}")
        print(f"  hitPolicy    : {meta.get('filterResultBy')}")
        print(f"  type         : {meta.get('type')}")
        print(f"  conditionCrit: {meta.get('conditionCriteria')} "
              f"({meta.get('conditionType')})")

    params = defn["parameters"]
    print(f"\n  Columns ({len(params)}):")
    by_usage = {}
    for p in params:
        by_usage.setdefault(p.get("Usage") or "(none)", []).append(p)
    for usage in ("INPUT", "OUTPUT", "ROWCRITERIA"):
        group = by_usage.get(usage, [])
        if not group:
            continue
        print(f"    {usage}:")
        for p in sorted(group, key=lambda x: (x.get("Sequence") is None, x.get("Sequence") or 0)):
            seq = f"seq={p.get('Sequence')} " if p.get("Sequence") is not None else ""
            op = f"op={p.get('Operator')} " if p.get("Operator") else ""
            req = " *required" if p.get("IsRequired") else ""
            print(f"      - {p.get('FieldName')}  ({p.get('DataType')})  "
                  f"{seq}{op}path={p.get('FieldPath') or '-'}{req}")
    # Any usage value not in the canonical trio
    for usage in sorted(set(by_usage) - {"INPUT", "OUTPUT", "ROWCRITERIA"}):
        print(f"    {usage}:")
        for p in by_usage[usage]:
            print(f"      - {p.get('FieldName')}  ({p.get('DataType')})")

    links = defn["datasetLinks"]
    if links:
        print(f"\n  Dataset links ({len(links)}):")
        for lk in links:
            default = " [default]" if lk.get("IsDefault") else ""
            print(f"    - {lk.get('SetupName') or lk.get('DeveloperName')}: "
                  f"{lk.get('SourceObject')}{default}   id={lk.get('Id')}")
        dsp = defn["datasetParameters"]
        if dsp:
            print(f"    Dataset params ({len(dsp)}):")
            for d in dsp:
                print(f"      - {d.get('DatasetFieldName')} @ {d.get('DatasetSourceObject')}")

    criteria = defn["sourceCriteria"]
    if criteria:
        print(f"\n  Source criteria ({len(criteria)}):")
        for c in sorted(criteria, key=lambda x: (x.get("SequenceNumber") is None,
                                                 x.get("SequenceNumber") or 0)):
            print(f"    - {c.get('SourceFieldName')} {c.get('Operator')} "
                  f"{c.get('Value')!r}  ({c.get('ValueType')})")

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Pretty-print one Decision Table's full definition. Read-only.",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias or username; not a CCI org alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true",
                        help="Emit the assembled definition as JSON.")
    args = parser.parse_args(argv)

    transport = Transport(args.target_org, api_version=args.api_version)
    try:
        defn = load_definition(transport, args.developer_name)
    except (DecisionTableClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    if args.json:
        print(json.dumps(defn, indent=2, default=str))
        return 0

    _print_definition(defn)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

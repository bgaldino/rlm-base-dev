#!/usr/bin/env python3
"""Pretty-print one BRE Decision Table's full definition (read-only).

Assembles the definition across the 5 Tooling setup objects — columns
(``DecisionTableParameter``, grouped INPUT / OUTPUT / ROWCRITERIA), dataset links
(``DecisionTableDatasetLink``) and their join params
(``DecisionTblDatasetParameter``), and row-filter criteria
(``DecisionTableSourceCriteria``) — plus the ``DecisionTable`` summary (source
object, hit policy, status, usageType, lastSync).

``--connect`` additionally reads the table through the **Connect Decision Table
Definitions** GET (by-id) and prints its divergent field vocabulary
(``sourceType`` / ``decisionResultPolicy`` / title-case ``usage``), so the two
representations can be compared side by side.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled.
``--target-org`` is the *SF CLI* alias. Read-only. Pinned to Release 262 / v67.0.

Usage
-----
    python scripts/decision_tables/describe_decision_table.py \
        --target-org rlm-base__beta --developer-name RLM_CostBookEntries

    # include the Connect Definitions representation, or emit JSON
    python scripts/decision_tables/describe_decision_table.py \
        --target-org rlm-base__beta --developer-name RLM_CostBookEntries --connect
    python scripts/decision_tables/describe_decision_table.py \
        --target-org rlm-base__beta --developer-name RLM_CostBookEntries --json
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
from scripts.decision_tables._resolve import (  # noqa: E402
    ResolveError,
    get_connect_definition,
    load_definition,
)


def _print_definition(defn, show_connect, transport):
    table = defn["table"]
    print(f"Decision Table: {table.get('DeveloperName')}   ({table.get('Id')})")
    print(f"  label        : {table.get('MasterLabel')}")
    print(f"  status       : {table.get('Status')}")
    print(f"  usageType    : {table.get('UsageType')}")
    print(f"  sourceObject : {table.get('SourceObject') or '-'}")
    print(f"  lastSync     : {table.get('LastSyncDate') or 'never'}")

    meta = defn.get("metadata") or {}
    if meta:
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

    if show_connect:
        print("\n  Connect Definitions representation (divergent vocabulary):")
        try:
            cdef = get_connect_definition(transport, table["Id"])
        except (DecisionTableClientError, ResolveError) as exc:
            print(f"    (could not read Connect definition: {exc})")
        else:
            print(f"    id            : {cdef.get('id')}  (15-char)")
            print(f"    sourceType    : {cdef.get('sourceType')}")
            print(f"    decisionResultPolicy: {cdef.get('decisionResultPolicy')}")
            print(f"    parameters    : {len(cdef.get('parameters') or [])}")
            print(f"    sourceCriteria: {len(cdef.get('sourceCriteria') or [])}")
            print(f"    rowLevelOverrideType: {cdef.get('rowLevelOverrideType')}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Pretty-print one Decision Table's full definition. Read-only.",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--connect", action="store_true",
                        help="Also read + show the Connect Definitions representation.")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true",
                        help="Emit the assembled definition as JSON.")
    args = parser.parse_args(argv)

    transport = Transport(args.target_org, api_version=args.api_version)
    try:
        defn = load_definition(transport, args.developer_name)
        if args.connect:
            defn["connect"] = get_connect_definition(transport, defn["table"]["Id"])
    except (DecisionTableClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    if args.json:
        print(json.dumps(defn, indent=2, default=str))
        return 0

    _print_definition(defn, args.connect, transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

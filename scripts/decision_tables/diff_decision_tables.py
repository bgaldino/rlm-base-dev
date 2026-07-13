#!/usr/bin/env python3
"""Structurally diff two BRE Decision Tables (read-only).

Compares two definitions — either two tables in one org, or the *same* table
across two orgs (``--other-org``, e.g. a scratch clone vs beta). Reports
differences in the table-level attributes (dataSource / hitPolicy / status /
usageType / sourceObject / executionType) and the column set (added / removed /
changed columns keyed by ``usage:fieldName``), dataset links, and source
criteria. Useful before a Phase-2 update, or to confirm a deploy landed.

The comparison core (:func:`diff_definitions`) is a **pure function** over two
loaded definition dicts, so it is unit-testable with no org.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled.
``--target-org`` is the *SF CLI* alias. Read-only. Pinned to Release 262 / v67.0.

Usage
-----
    # two tables in one org
    python scripts/decision_tables/diff_decision_tables.py \
        --target-org rlm-base__beta \
        --developer-name RLM_CostBookEntries --other RLM_ContractPricingEntries

    # the same table across two orgs
    python scripts/decision_tables/diff_decision_tables.py \
        --target-org rlm-base__scratch \
        --developer-name RLM_CostBookEntries \
        --other RLM_CostBookEntries --other-org rlm-base__beta
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
    load_definition,
)

# Table-level attributes worth diffing. `table` summary + `metadata` complexvalue.
_TABLE_ATTRS = ("Status", "UsageType", "SourceObject")
_META_ATTRS = ("dataSourceType", "executionType", "filterResultBy", "type",
               "conditionType", "conditionCriteria", "dtRowLevelOverrideType")


def _column_key(param):
    return f"{param.get('Usage')}:{param.get('FieldName')}"


def _column_signature(param):
    """The comparable fields of a column (ignores record Id / table Id)."""
    return {
        "dataType": param.get("DataType"),
        "operator": param.get("Operator"),
        "sequence": param.get("Sequence"),
        "fieldPath": param.get("FieldPath"),
        "isRequired": param.get("IsRequired"),
        "isGroupByField": param.get("IsGroupByField"),
        "sortType": param.get("SortType"),
    }


def _criteria_key(crit):
    return f"{crit.get('SourceFieldName')}:{crit.get('Operator')}:{crit.get('Value')}"


def diff_definitions(a, b):
    """Pure structural diff of two loaded definitions. Returns a dict of deltas."""
    delta = {"attributes": {}, "columns": {"added": [], "removed": [], "changed": []},
             "datasetLinks": {"added": [], "removed": []},
             "sourceCriteria": {"added": [], "removed": []}}

    # Table-level + metadata attributes.
    for attr in _TABLE_ATTRS:
        av, bv = a["table"].get(attr), b["table"].get(attr)
        if av != bv:
            delta["attributes"][attr] = {"a": av, "b": bv}
    meta_a = a.get("metadata") or {}
    meta_b = b.get("metadata") or {}
    for attr in _META_ATTRS:
        av, bv = meta_a.get(attr), meta_b.get(attr)
        if av != bv:
            delta["attributes"][attr] = {"a": av, "b": bv}

    # Columns keyed by usage:fieldName.
    cols_a = {_column_key(p): p for p in a["parameters"]}
    cols_b = {_column_key(p): p for p in b["parameters"]}
    for key in sorted(set(cols_a) - set(cols_b)):
        delta["columns"]["removed"].append(key)
    for key in sorted(set(cols_b) - set(cols_a)):
        delta["columns"]["added"].append(key)
    for key in sorted(set(cols_a) & set(cols_b)):
        sig_a, sig_b = _column_signature(cols_a[key]), _column_signature(cols_b[key])
        if sig_a != sig_b:
            fields = {k: {"a": sig_a[k], "b": sig_b[k]}
                      for k in sig_a if sig_a[k] != sig_b[k]}
            delta["columns"]["changed"].append({"column": key, "fields": fields})

    # Dataset links keyed by SourceObject.
    links_a = {lk.get("SourceObject") for lk in a["datasetLinks"]}
    links_b = {lk.get("SourceObject") for lk in b["datasetLinks"]}
    delta["datasetLinks"]["removed"] = sorted(links_a - links_b)
    delta["datasetLinks"]["added"] = sorted(links_b - links_a)

    # Source criteria keyed by field:op:value.
    crit_a = {_criteria_key(c) for c in a["sourceCriteria"]}
    crit_b = {_criteria_key(c) for c in b["sourceCriteria"]}
    delta["sourceCriteria"]["removed"] = sorted(crit_a - crit_b)
    delta["sourceCriteria"]["added"] = sorted(crit_b - crit_a)

    return delta


def _is_empty(delta):
    return (not delta["attributes"]
            and not any(delta["columns"].values())
            and not any(delta["datasetLinks"].values())
            and not any(delta["sourceCriteria"].values()))


def _print_delta(name_a, name_b, delta):
    print(f"Diff: A={name_a}  vs  B={name_b}\n")
    if _is_empty(delta):
        print("  (structurally identical)")
        return
    if delta["attributes"]:
        print("  Attributes:")
        for attr, pair in delta["attributes"].items():
            print(f"    {attr}: A={pair['a']!r}  B={pair['b']!r}")
    cols = delta["columns"]
    if any(cols.values()):
        print("  Columns:")
        for key in cols["removed"]:
            print(f"    - only in A: {key}")
        for key in cols["added"]:
            print(f"    + only in B: {key}")
        for ch in cols["changed"]:
            print(f"    ~ {ch['column']}: " +
                  ", ".join(f"{k} A={v['a']!r}/B={v['b']!r}" for k, v in ch["fields"].items()))
    if any(delta["datasetLinks"].values()):
        print("  Dataset links:")
        for s in delta["datasetLinks"]["removed"]:
            print(f"    - only in A: {s}")
        for s in delta["datasetLinks"]["added"]:
            print(f"    + only in B: {s}")
    if any(delta["sourceCriteria"].values()):
        print("  Source criteria:")
        for s in delta["sourceCriteria"]["removed"]:
            print(f"    - only in A: {s}")
        for s in delta["sourceCriteria"]["added"]:
            print(f"    + only in B: {s}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Structurally diff two Decision Tables (or one across two orgs). Read-only.",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias for table A — NOT the CCI alias.",
    )
    parser.add_argument("--developer-name", required=True, help="DeveloperName of table A.")
    parser.add_argument("--other", required=True, help="DeveloperName of table B.")
    parser.add_argument("--other-org",
                        help="SF CLI alias for table B (default: same as --target-org).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit the delta as JSON.")
    args = parser.parse_args(argv)

    org_a = args.target_org
    org_b = args.other_org or args.target_org
    transport_a = Transport(org_a, api_version=args.api_version)
    transport_b = Transport(org_b, api_version=args.api_version)
    try:
        defn_a = load_definition(transport_a, args.developer_name)
        defn_b = load_definition(transport_b, args.other)
    except (DecisionTableClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    delta = diff_definitions(defn_a, defn_b)
    name_a = f"{args.developer_name}@{org_a}"
    name_b = f"{args.other}@{org_b}"

    if args.json:
        print(json.dumps({"a": name_a, "b": name_b, "delta": delta}, indent=2, default=str))
        return 0

    _print_delta(name_a, name_b, delta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

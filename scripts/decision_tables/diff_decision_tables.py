#!/usr/bin/env python3
"""Structurally diff two BRE Decision Table definitions (read-only)."""

import argparse
import json
import sys
from collections import Counter
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

# Table-level attributes worth diffing. `table` summary + the author-controlled,
# structural fields from the `Metadata` complexvalue. Runtime observations such
# as lastSyncDate / refreshStatus / uploadStatus are intentionally excluded: a
# definition diff should not report drift merely because one org refreshed later.
_TABLE_ATTRS = ("Status", "UsageType", "SourceObject")
_META_ATTRS = (
    "setupName", "dataSourceType", "sourceObject", "executionType",
    "filterResultBy", "conditionType", "conditionCriteria",
    "sourceConditionLogic", "type", "usageType", "status", "description",
    "collectOperator", "dtRowLevelOverrideType", "doesConsiderNullValue",
    "isIncrementalSyncEnabled", "isVersioned",
)

_DATASET_LINK_FIELDS = (
    "DeveloperName", "MasterLabel", "SetupName", "SourceObject", "IsDefault",
    "Description",
)
_SOURCE_CRITERIA_FIELDS = (
    "SourceFieldName", "Operator", "Value", "ValueType", "SequenceNumber",
)
_COLUMN_FIELDS = (
    "dataType", "decimalScale", "domainObject", "fieldPath",
    "isGroupByField", "isPriorityField", "isRequired", "length", "operator",
    "sequence", "sortType",
)


def _column_key(param):
    usage = param.get("usage") if "usage" in param else param.get("Usage")
    field_name = param.get("fieldName") if "fieldName" in param else param.get("FieldName")
    return f"{usage}:{field_name}"


def _column_signature(param):
    """The comparable fields of a column (ignores record Id / table Id)."""
    return {field: param.get(field) for field in _COLUMN_FIELDS}


def _record_signature(record, fields):
    """Return only material fields, retaining explicit nulls for stable equality."""
    return {field: record.get(field) for field in fields}


def _signature_delta(signatures_a, signatures_b):
    """Multiset difference for JSON-compatible signatures.

    A Counter preserves duplicate structural records, while canonical JSON gives
    dictionaries a deterministic, sortable identity. The returned values remain
    dictionaries (rather than opaque strings) for useful ``--json`` output.
    """
    encoded_a = [json.dumps(s, sort_keys=True, default=str) for s in signatures_a]
    encoded_b = [json.dumps(s, sort_keys=True, default=str) for s in signatures_b]
    counts_a, counts_b = Counter(encoded_a), Counter(encoded_b)
    by_key = {json.dumps(s, sort_keys=True, default=str): s
              for s in [*signatures_a, *signatures_b]}

    removed = []
    added = []
    for key in sorted(counts_a.keys() | counts_b.keys()):
        removed.extend([by_key[key]] * max(0, counts_a[key] - counts_b[key]))
        added.extend([by_key[key]] * max(0, counts_b[key] - counts_a[key]))
    return {"added": added, "removed": removed}


def _dataset_link_identity(link):
    """Stable logical identity for resolving dataset-parameter foreign keys."""
    return (link.get("DeveloperName") or link.get("SetupName")
            or link.get("SourceObject"))


def _dataset_parameter_signatures(defn):
    """Replace org-specific ids with their logical link/column identities."""
    links_by_id = {link.get("Id"): _dataset_link_identity(link)
                   for link in defn.get("datasetLinks", []) if link.get("Id")}
    params_by_id = {param.get("Id"): _column_key(param)
                    for param in defn.get("parameters", []) if param.get("Id")}
    signatures = []
    for row in defn.get("datasetParameters", []):
        link_id = row.get("DecisionTableDatasetLinkId")
        param_id = row.get("DecisionTableParameterId")
        signatures.append({
            "datasetLink": links_by_id.get(link_id, link_id),
            "decisionTableParameter": params_by_id.get(param_id, param_id),
            "datasetFieldName": row.get("DatasetFieldName"),
            "datasetSourceObject": row.get("DatasetSourceObject"),
        })
    return signatures


def diff_definitions(a, b):
    """Pure structural diff of two loaded definitions. Returns a dict of deltas."""
    delta = {"attributes": {}, "columns": {"added": [], "removed": [], "changed": []},
             "datasetLinks": {"added": [], "removed": []},
             "datasetParameters": {"added": [], "removed": []},
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

    # The parent Metadata complexvalue is the canonical column view. It includes
    # decimalScale/isPriorityField/length, which are not queryable columns on the
    # DecisionTableParameter Tooling object in API v67.0.
    params_a = (a.get("metadata") or {}).get("decisionTableParameters") or []
    params_b = (b.get("metadata") or {}).get("decisionTableParameters") or []
    cols_a = {_column_key(p): p for p in params_a}
    cols_b = {_column_key(p): p for p in params_b}
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

    # Full material signatures. Org-specific setup ids are deliberately ignored;
    # dataset-parameter foreign keys are resolved to logical link/column names.
    delta["datasetLinks"] = _signature_delta(
        [_record_signature(link, _DATASET_LINK_FIELDS) for link in a.get("datasetLinks", [])],
        [_record_signature(link, _DATASET_LINK_FIELDS) for link in b.get("datasetLinks", [])],
    )
    delta["datasetParameters"] = _signature_delta(
        _dataset_parameter_signatures(a), _dataset_parameter_signatures(b)
    )
    delta["sourceCriteria"] = _signature_delta(
        [_record_signature(criterion, _SOURCE_CRITERIA_FIELDS)
         for criterion in a.get("sourceCriteria", [])],
        [_record_signature(criterion, _SOURCE_CRITERIA_FIELDS)
         for criterion in b.get("sourceCriteria", [])],
    )

    return delta


def _is_empty(delta):
    return (not delta["attributes"]
            and not any(delta["columns"].values())
            and not any(delta["datasetLinks"].values())
            and not any(delta["datasetParameters"].values())
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
            print(f"    - only in A: {json.dumps(s, sort_keys=True, default=str)}")
        for s in delta["datasetLinks"]["added"]:
            print(f"    + only in B: {json.dumps(s, sort_keys=True, default=str)}")
    if any(delta["datasetParameters"].values()):
        print("  Dataset parameters:")
        for s in delta["datasetParameters"]["removed"]:
            print(f"    - only in A: {json.dumps(s, sort_keys=True, default=str)}")
        for s in delta["datasetParameters"]["added"]:
            print(f"    + only in B: {json.dumps(s, sort_keys=True, default=str)}")
    if any(delta["sourceCriteria"].values()):
        print("  Source criteria:")
        for s in delta["sourceCriteria"]["removed"]:
            print(f"    - only in A: {json.dumps(s, sort_keys=True, default=str)}")
        for s in delta["sourceCriteria"]["added"]:
            print(f"    + only in B: {json.dumps(s, sort_keys=True, default=str)}")


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

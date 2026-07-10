#!/usr/bin/env python3
"""Sample the *data layer* of a BRE Decision Table (read-only).

The definition (columns / criteria) is one layer; the **rows the engine
evaluates** are another. This dumps a sample of those rows, branching on the
table's ``dataSourceType`` (live-verified):

- **SingleSobject** — SOQL a sample of the ``sourceObject`` (normal REST),
  projecting the columns' ``fieldName``/``fieldPath`` when resolvable, else ``*``
  via a bounded ``FIELDS(...)`` fallback is avoided — we project the definition's
  fields plus ``Id``.
- **MultipleSobjects** — one sample per ``DecisionTableDatasetLink.SourceObject``.
- **CsvUpload** — the rows live in an uploaded CSV, read via the Connect **CSV
  Based Decision Table** data GET (``.../{id}/data``, v62+). ⚠ Marked **"not
  applicable"** and skipped when no CsvUpload table is present (doc-grounded /
  unverified — no such table existed on the probed orgs).
- **ContextDefinition** — rows are hydrated by a Context Definition at runtime;
  there is no static source table to sample, so this is reported and skipped.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled.
``--target-org`` is the *SF CLI* alias. Read-only. Pinned to Release 262 / v67.0.

Usage
-----
    python scripts/decision_tables/dump_decision_table_data.py \
        --target-org rlm-base__beta --developer-name RLM_CostBookEntries --limit 5
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

_SOBJECT_TYPES = {"SingleSobject", "MultipleSobjects"}


def _projection_fields(defn):
    """Distinct source field names from the definition's columns (+ Id)."""
    fields = ["Id"]
    for p in defn["parameters"]:
        name = p.get("FieldPath") or p.get("FieldName")
        # Skip traversal paths (contain '.') — SOQL them only if simple.
        if name and "." not in name and name not in fields:
            fields.append(name)
    return fields


def _sample_sobject(transport, sobject, fields, limit):
    field_list = ", ".join(fields) if fields else "Id"
    soql = f"SELECT {field_list} FROM {sobject} LIMIT {int(limit)}"
    try:
        return transport.soql(soql)
    except DecisionTableClientError as exc:
        # A column may not be directly queryable (formula/traversal). Fall back to Id-only.
        eprint(f"  (projection query failed, falling back to Id-only: {exc})")
        return transport.soql(f"SELECT Id FROM {sobject} LIMIT {int(limit)}")


def dump_data(transport, defn, limit):
    """Return a dict describing the data-layer sample for a loaded definition."""
    table = defn["table"]
    meta = defn.get("metadata") or {}
    source_type = meta.get("dataSourceType")
    source_object = table.get("SourceObject") or meta.get("sourceObject")
    out = {"developerName": table.get("DeveloperName"),
           "dataSourceType": source_type, "samples": {}, "notes": []}

    if source_type == "SingleSobject" or (source_type is None and source_object):
        if not source_object:
            out["notes"].append("No sourceObject on a SingleSobject table — nothing to sample.")
            return out
        fields = _projection_fields(defn)
        rows = _sample_sobject(transport, source_object, fields, limit)
        out["samples"][source_object] = rows
        if not rows:
            out["notes"].append(f"{source_object} has 0 rows (definition present, data empty).")
    elif source_type == "MultipleSobjects":
        links = defn["datasetLinks"]
        if not links:
            out["notes"].append("MultipleSobjects table has no dataset links to sample.")
        for lk in links:
            so = lk.get("SourceObject")
            if not so:
                continue
            rows = _sample_sobject(transport, so, ["Id"], limit)
            out["samples"][so] = rows
    elif source_type == "CsvUpload":
        out["notes"].append(
            "CsvUpload data layer read via Connect '.../{id}/data' (v62+) is "
            "doc-grounded / unverified — no CsvUpload table was available on the "
            "probed orgs. Marked NOT APPLICABLE; skipped."
        )
    elif source_type == "ContextDefinition":
        out["notes"].append(
            "ContextDefinition-backed table: rows are hydrated by a Context "
            "Definition at runtime; there is no static source table to sample."
        )
    else:
        out["notes"].append(f"Unrecognized dataSourceType {source_type!r}; nothing sampled.")
    return out


def _print_dump(dump, limit):
    print(f"Data layer: {dump['developerName']}   dataSourceType={dump['dataSourceType']}")
    for note in dump["notes"]:
        print(f"  note: {note}")
    for sobject, rows in dump["samples"].items():
        print(f"\n  {sobject}  (sample up to {limit}, got {len(rows)}):")
        for r in rows:
            clean = {k: v for k, v in r.items() if k != "attributes"}
            print(f"    {json.dumps(clean, default=str)}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Sample the data layer of a Decision Table (branches on dataSourceType). Read-only.",
    )
    parser.add_argument(
        "--target-org", required=True,
        help="SF CLI alias/username (e.g. rlm-base__beta) — NOT the CCI alias.",
    )
    parser.add_argument("--developer-name", required=True,
                        help="DecisionTable DeveloperName (case-sensitive).")
    parser.add_argument("--limit", type=int, default=5, help="Max rows per source object (default 5).")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit the dump as JSON.")
    args = parser.parse_args(argv)

    transport = Transport(args.target_org, api_version=args.api_version)
    try:
        defn = load_definition(transport, args.developer_name)
        dump = dump_data(transport, defn, args.limit)
    except (DecisionTableClientError, ResolveError) as exc:
        eprint(f"Error: {exc}")
        return 1

    if args.json:
        print(json.dumps(dump, indent=2, default=str))
        return 0

    _print_dump(dump, args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

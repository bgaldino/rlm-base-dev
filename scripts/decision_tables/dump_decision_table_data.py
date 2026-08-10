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
- **CsvUpload** — the rows live in an uploaded CSV, not on a queryable SObject;
  they are read via the Connect **CSV Based Decision Table** data GET
  (``.../{id}/data``, v62+), which returns ``rowData`` per row. Read once with an
  optional ``--limit`` (the endpoint's ``totalRows`` counts returned rows, not a
  grand total, and ``offset`` is unreliable — see ``_client``). Two CsvUpload-only
  reads narrow the GET (both live-verified 262 / v67.0):
    * ``--filter FIELD:VALUE`` — server-side **exact, case-sensitive** equality on
      one column (``Region:North`` ≠ ``Region:north``; no substring/prefix match).
      An unknown field silently returns 0 rows (no error).
    * ``--version-number N`` — reads a specific historical import version. Omitting
      it reads the current/active version; explicitly passing the current version
      returns an empty ``rowData`` array on 262/v67.0. A non-existent version
      errors ``INVALID_API_INPUT``.
  ⚠ ``--filter`` and ``--limit`` **cannot be combined** when the limit would
  truncate the matched set — the platform throws ``UNKNOWN_EXCEPTION`` unless the
  limit strictly exceeds the match count. This tool therefore **drops ``--limit``
  (with a note) when ``--filter`` is also given** and reads the full matched set.
- **ContextDefinition** — rows are hydrated by a Context Definition at runtime;
  there is no static source table to sample, so this is reported and skipped.

``--filter`` / ``--version-number`` apply **only** to CsvUpload tables; on any
other ``dataSourceType`` they are ignored with a note.

Auth is delegated to the ``sf`` CLI (see ``_client.py``) — no tokens handled.
``--target-org`` is the *SF CLI* alias. Read-only. Pinned to Release 262 / v67.0.

Usage
-----
    python scripts/decision_tables/dump_decision_table_data.py \
        --target-org rlm-base__beta --developer-name RLM_CostBookEntries --limit 5

    # CsvUpload table — a version-scoped, column-filtered read
    python scripts/decision_tables/dump_decision_table_data.py \
        --target-org rlm-base__scratch --developer-name RLM_MyCsvTable \
        --version-number 1 --filter Region:North
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
    """Query source rows; returns (rows, fallback_note_or_None)."""
    field_list = ", ".join(fields) if fields else "Id"
    soql = f"SELECT {field_list} FROM {sobject} LIMIT {int(limit)}"
    try:
        return transport.soql(soql), None
    except DecisionTableClientError as exc:
        eprint(f"  (projection query failed, falling back to Id-only: {exc})")
        rows = transport.soql(f"SELECT Id FROM {sobject} LIMIT {int(limit)}")
        return rows, (f"Projection query on {sobject} failed ({exc}); "
                      f"fell back to Id-only.")


def _dump_csv_upload(transport, table, out, limit, row_filter=None, version_number=None):
    """Populate ``out`` from a CsvUpload table's Connect ``.../{id}/data`` GET.

    The rows live in an uploaded CSV, not on a queryable SObject, so this reads the
    Connect data sub-resource once with an optional ``limit`` (the endpoint's
    ``totalRows`` counts *returned* rows and ``offset`` is unreliable — no paging).
    ``row_filter`` (``"Field:Value"``, exact + case-sensitive) narrows server-side;
    ``version_number`` targets a specific import version (defaults to the
    current/active version). The row envelope's ``rowData`` maps are surfaced under
    a synthetic ``"CSV (uploaded rows)"`` sample key so ``_print_dump`` renders them
    like any other sample. A disabled/pilot-gated endpoint degrades to a note rather
    than an error (mirroring the SObject-branch fallbacks).

    ⚠ ``filter`` + ``limit`` together throw ``UNKNOWN_EXCEPTION`` on the platform
    unless the limit strictly exceeds the matched-row count (live-verified). When a
    ``row_filter`` is present the ``limit`` is therefore **dropped** (with a note) so
    the filtered read can't hit that trap — the caller gets the full matched set."""
    record_id = table.get("Id")
    if not record_id:
        out["notes"].append("CsvUpload table has no id; cannot read its data layer.")
        return
    effective_limit = limit
    if row_filter and limit is not None:
        out["notes"].append(
            f"--filter is set, so --limit ({limit}) is ignored: the platform throws "
            "UNKNOWN_EXCEPTION when a filter's limit would truncate the match; "
            "returning the full matched set instead."
        )
        effective_limit = None
    # The header renderer reflects the limit actually sent (None = full matched set).
    out["effectiveLimit"] = effective_limit
    try:
        resp = transport.get_decision_table_data(
            record_id, limit=effective_limit, row_filter=row_filter,
            version_number=version_number,
        )
    except DecisionTableClientError as exc:
        _DEGRADABLE_CODES = {"NOT_FOUND", "INSUFFICIENT_ACCESS", "FUNCTIONALITY_NOT_ENABLED",
                             "INVALID_INPUT", "UNKNOWN_EXCEPTION"}
        # Degrade only when the parsed error carries one of the known-benign codes.
        # A transport failure (timeout, non-JSON CLI error) parses no codes at all —
        # that must propagate, not be swallowed into a "may be disabled" note.
        if not _DEGRADABLE_CODES.intersection(exc.error_codes):
            raise
        out["notes"].append(
            f"CsvUpload data GET (.../{{id}}/data) failed — the endpoint may be "
            f"disabled on this org, or no version has been uploaded yet: {exc}"
        )
        return
    rows = resp.get("rows") if isinstance(resp, dict) else None
    if not rows:
        if row_filter:
            out["notes"].append(
                f"CsvUpload data GET matched 0 rows for filter {row_filter!r} "
                "(exact + case-sensitive equality; an unknown field silently "
                "returns 0 rows — confirm the column name and value case)."
            )
        else:
            out["notes"].append(
                "CsvUpload table has 0 uploaded rows (definition present, CSV data "
                "empty — upload rows with upload_decision_table_data.py)."
            )
        return
    # Surface each row's typed rowData; ignore the row id + envelope wrapper.
    samples = []
    for r in rows:
        if isinstance(r, dict) and isinstance(r.get("rowData"), dict):
            samples.append(r["rowData"])
        elif isinstance(r, dict):
            samples.append({k: v for k, v in r.items() if k != "id"})
    out["samples"]["CSV (uploaded rows)"] = samples


def dump_data(transport, defn, limit, row_filter=None, version_number=None):
    """Return a dict describing the data-layer sample for a loaded definition.

    ``row_filter`` / ``version_number`` apply **only** to the CsvUpload branch; on
    any other ``dataSourceType`` they are ignored (a note records that they were
    dropped) so passing them against, say, a SingleSobject table is harmless."""
    table = defn["table"]
    meta = defn.get("metadata") or {}
    source_type = meta.get("dataSourceType")
    source_object = table.get("SourceObject") or meta.get("sourceObject")
    out = {"developerName": table.get("DeveloperName"),
           "dataSourceType": source_type, "samples": {}, "notes": []}

    if (row_filter or version_number is not None) and source_type != "CsvUpload":
        out["notes"].append(
            "--filter/--version-number apply only to CsvUpload tables; ignored for "
            f"dataSourceType {source_type!r}."
        )

    if source_type == "SingleSobject" or (source_type is None and source_object):
        if not source_object:
            out["notes"].append("No sourceObject on a SingleSobject table — nothing to sample.")
            return out
        fields = _projection_fields(defn)
        rows, fallback_note = _sample_sobject(transport, source_object, fields, limit)
        out["samples"][source_object] = rows
        if fallback_note:
            out["notes"].append(fallback_note)
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
            rows, fallback_note = _sample_sobject(transport, so, ["Id"], limit)
            out["samples"][so] = rows
            if fallback_note:
                out["notes"].append(fallback_note)
    elif source_type == "CsvUpload":
        _dump_csv_upload(transport, table, out, limit,
                         row_filter=row_filter, version_number=version_number)
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
    # When a filter dropped the limit (effectiveLimit=None) the sample is the full
    # matched set, not a capped peek — reflect that in the header.
    effective = dump.get("effectiveLimit", limit) if "effectiveLimit" in dump else limit
    for sobject, rows in dump["samples"].items():
        cap = "all matched" if effective is None else f"up to {effective}"
        print(f"\n  {sobject}  (sample {cap}, got {len(rows)}):")
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
    parser.add_argument(
        "--filter", dest="row_filter", metavar="FIELD:VALUE",
        help="CsvUpload only — server-side EXACT, CASE-SENSITIVE equality on one "
             "column (e.g. Region:North). Unknown field → 0 rows (no error). When "
             "set, --limit is dropped (filter+limit can throw UNKNOWN_EXCEPTION).",
    )
    parser.add_argument(
        "--version-number", type=int, metavar="N",
        help="CsvUpload only — read a specific import version (default: current).",
    )
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit the dump as JSON.")
    args = parser.parse_args(argv)

    transport = Transport(args.target_org, api_version=args.api_version)
    try:
        defn = load_definition(transport, args.developer_name)
        dump = dump_data(transport, defn, args.limit,
                         row_filter=args.row_filter,
                         version_number=args.version_number)
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

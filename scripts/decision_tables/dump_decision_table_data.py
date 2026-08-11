#!/usr/bin/env python3
"""Sample a Decision Table's materialized data layer (read-only).

SObject-backed tables are queried through REST, CSV tables through Connect, and
runtime-hydrated ContextDefinition tables are reported without a static sample.
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

# The CsvUpload data GET is degraded to a note (rather than raised) only for the
# two error codes that genuinely mean "no rows to read here", not a real failure:
#   * FUNCTIONALITY_NOT_ENABLED — the /data endpoint is disabled/pilot-gated on the org.
#   * NOT_FOUND — no uploaded version exists yet.
# Everything else — authorization (INSUFFICIENT_ACCESS), bad request (INVALID_INPUT),
# server/unknown (UNKNOWN_EXCEPTION), or a transport error that parses no code at all —
# is a real failure the caller must see, so it propagates.
_CSV_DATA_BENIGN_CODES = frozenset({"NOT_FOUND", "FUNCTIONALITY_NOT_ENABLED"})


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


def _dump_csv_upload(transport, table, out, limit, row_filter=None):
    """Populate ``out`` from a CsvUpload table's Connect ``.../{id}/data`` GET.

    The rows live in an uploaded CSV, not on a queryable SObject, so this reads the
    Connect data sub-resource once with an optional ``limit`` (the endpoint's
    ``totalRows`` counts *returned* rows and ``offset`` is unreliable — no paging).
    ``row_filter`` (``"Field:Value"``, exact + case-sensitive) narrows server-side.
    The row envelope's ``rowData`` maps are surfaced under
    a synthetic ``"CSV (uploaded rows)"`` sample key so ``_print_dump`` renders them
    like any other sample. A disabled/pilot-gated endpoint degrades to a note rather
    than an error (mirroring the SObject-branch fallbacks).

    The platform can reject ``filter`` with a truncating ``limit``. When a filter
    is present, the limit is omitted and the full matched set is returned."""
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
        )
    except DecisionTableClientError as exc:
        # Degrade only when the parsed error carries one of the known-benign codes
        # (endpoint disabled / no version uploaded). Authorization, invalid-input,
        # generic/unknown, and transport failures (which parse no code at all) must
        # propagate — swallowing them into a "may be disabled" note would report a
        # real error as an empty-but-successful read.
        if not _CSV_DATA_BENIGN_CODES.intersection(exc.error_codes):
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


def dump_data(transport, defn, limit, row_filter=None):
    """Return a dict describing the data-layer sample for a loaded definition.

    ``row_filter`` applies only to the CsvUpload branch; other source types ignore
    it with a note."""
    table = defn["table"]
    meta = defn.get("metadata") or {}
    source_type = meta.get("dataSourceType")
    source_object = table.get("SourceObject") or meta.get("sourceObject")
    out = {"developerName": table.get("DeveloperName"),
           "dataSourceType": source_type, "samples": {}, "notes": []}

    if row_filter and source_type != "CsvUpload":
        out["notes"].append(
            "--filter applies only to CsvUpload tables; ignored for "
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
        _dump_csv_upload(transport, table, out, limit, row_filter=row_filter)
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
        help="SF CLI alias or username; not a CCI org alias.",
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
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION,
                        help=f"API version (default {DEFAULT_API_VERSION}).")
    parser.add_argument("--json", action="store_true", help="Emit the dump as JSON.")
    args = parser.parse_args(argv)

    transport = Transport(args.target_org, api_version=args.api_version)
    try:
        defn = load_definition(transport, args.developer_name)
        dump = dump_data(transport, defn, args.limit, row_filter=args.row_filter)
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

#!/usr/bin/env python3
"""Resolve a plan's parent lookups to target-org record Ids before an SFDMU load.

Some child objects can only be matched on a direct lookup field (`ProductUsageResourceId`)
because SFDMU 5.8.0 cannot build the child's target query from the parent's composite
traversal key (upstream issue #1218: `ProductUsageResource.Product.StockKeepingUnit`
loses its `ProductUsageResource.` prefix, "Didn't understand relationship 'Product'").
The tracked CSVs stay portable: they carry the parent's natural key as traversal columns,
and a load writes the matching target Ids into a TEMP COPY of the plan, never the tracked
files.

A plan opts in with a `parent_id_lookups.json` next to its `export.json`:

    {
      "lookups": [{
        "object": "ProductUsageResource",
        "keyFields": ["Product.StockKeepingUnit", "UsageResource.Code"],
        "prefer": {"Status": ["Active", "Draft"]},
        "children": [{
          "objects": ["ProductUsageResourcePolicy", "ProductUsageGrant"],
          "idColumn": "ProductUsageResourceId",
          "keyColumns": ["ProductUsageResource.Product.StockKeepingUnit",
                         "ProductUsageResource.UsageResource.Code"]
        }]
      }]
    }

For each lookup the parent is queried on the target org, and:

* the parent's own CSV (`<object>.csv`) is written with the fields of its `Readonly`
  declaration (`SELECT Id, Status FROM ProductUsageResource`), at the plan root and in
  `objectset_source/object-set-N/` for every later pass that declares it, so SFDMU can map
  each child's Id column to a source record;
* each child CSV (root and per-pass) gains `idColumn`, filled from `keyColumns`.

`prefer` restricts and ranks the candidates: a parent whose value is not listed (an Inactive
PUR) is never chosen, and when a key matches more than one listed parent (a Draft copy next to
the Active one) the earliest listed value wins. A tie at the best rank, or a key with no
candidate, fails the load instead of guessing.

Dependency-free (no cumulusci): the caller supplies `query`, a function that runs SOQL on
the target org and returns the records, so the task and the tests share this code.
"""

import csv
import json
import os
import re
from typing import Callable, Dict, List, Optional, Tuple

import sfdmu_export

LOOKUPS_FILENAME = "parent_id_lookups.json"
_SALESFORCE_ID = re.compile(r"[A-Za-z0-9]{15}(?:[A-Za-z0-9]{3})?", re.ASCII)
EXPORT_JSON_FILENAME = "export.json"


class IdLookupError(Exception):
    """A lookup could not be resolved; the message says which keys and why."""


def load_lookups(plan_dir: str) -> List[dict]:
    """The plan's lookups, or [] when the plan has no `parent_id_lookups.json`."""
    path = os.path.join(plan_dir, LOOKUPS_FILENAME)
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as handle:
        spec = json.load(handle)
    lookups = spec.get("lookups") if isinstance(spec, dict) else None
    if not isinstance(lookups, list) or not lookups:
        raise IdLookupError(f"{path}: expected a non-empty 'lookups' list")
    for item in lookups:
        for key in ("object", "keyFields", "children"):
            if not item.get(key):
                raise IdLookupError(f"{path}: lookup is missing '{key}': {item!r}")
        for child in item["children"]:
            for key in ("objects", "idColumn", "keyColumns"):
                if not child.get(key):
                    raise IdLookupError(f"{path}: child is missing '{key}': {child!r}")
            if len(child["keyColumns"]) != len(item["keyFields"]):
                raise IdLookupError(f"{path}: keyColumns {child['keyColumns']} must pair "
                                    f"one-to-one with keyFields {item['keyFields']}")
    return lookups


def _record_value(record: dict, path: str):
    """`record['Product']['StockKeepingUnit']` for `Product.StockKeepingUnit`."""
    value = record
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _as_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _declared_fields(export_data: dict, object_name: str) -> Tuple[List[str], List[int]]:
    """The parent's Readonly field list (Id first) and every pass index that declares it."""
    fields: Optional[List[str]] = None
    passes: List[int] = []
    for index, object_set in enumerate(sfdmu_export.normalize_object_sets(export_data)):
        for obj in object_set.get("objects", []):
            if sfdmu_export.is_js_truthy(obj.get("excluded")):
                continue
            if sfdmu_export.extract_object_name(obj.get("query", "")) != object_name:
                continue
            if sfdmu_export.resolve_operation(obj.get("operation")) != "readonly":
                raise IdLookupError(f"{object_name} must be declared Readonly in every pass "
                                    "that names it: its CSV is generated from the target org")
            passes.append(index)
            if fields is None:
                fields = sfdmu_export.parse_select_fields(obj["query"])
    if fields is None:
        raise IdLookupError(f"{object_name} is not declared in {EXPORT_JSON_FILENAME}")
    rest = [f for f in fields if f.lower() != "id"]
    return ["Id"] + rest, passes


def _rank(record: dict, prefer: Dict[str, List[str]]) -> Optional[Tuple[int, ...]]:
    """Rank by the `prefer` lists, or None when a value is not listed (never a candidate)."""
    ranks = []
    for field, order in prefer.items():
        value = _as_text(_record_value(record, field))
        if value not in order:
            return None
        ranks.append(order.index(value))
    return tuple(ranks)


def build_id_map(records: List[dict], key_fields: List[str],
                 prefer: Optional[Dict[str, List[str]]] = None) -> Tuple[Dict[tuple, dict], Dict[tuple, int]]:
    """`({key: chosen record}, {key: tied count})` -- a key with a tie at its best rank is
    left out of the map and reported in the second dict."""
    prefer = prefer or {}
    grouped: Dict[tuple, List[dict]] = {}
    for record in records:
        if _rank(record, prefer) is None:
            continue
        key = tuple(_as_text(_record_value(record, f)) for f in key_fields)
        grouped.setdefault(key, []).append(record)
    chosen, ambiguous = {}, {}
    for key, candidates in grouped.items():
        best = min(_rank(r, prefer) for r in candidates)
        top = [r for r in candidates if _rank(r, prefer) == best]
        if len(top) == 1:
            chosen[key] = top[0]
        else:
            ambiguous[key] = len(top)
    return chosen, ambiguous


def lookup_soql(object_name: str, key_fields: List[str], declared: List[str],
                prefer: Optional[Dict[str, List[str]]] = None) -> str:
    fields: List[str] = []
    for field in declared + list(key_fields) + list((prefer or {}).keys()):
        if field.lower() not in {f.lower() for f in fields}:
            fields.append(field)
    return f"SELECT {', '.join(fields)} FROM {object_name}"


def _read_csv(path: str) -> Tuple[List[str], List[dict]]:
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _write_csv(path: str, header: List[str], rows: List[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n",
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _csv_paths(plan_dir: str, object_name: str, passes: Optional[List[int]] = None,
               separated: bool = True) -> List[str]:
    """Root CSV plus each existing (or, with `passes`, each declaring) per-pass CSV."""
    paths = [os.path.join(plan_dir, f"{object_name}.csv")]
    source_root = os.path.join(plan_dir, "objectset_source")
    if passes is not None:
        if separated:
            for index in passes:
                if index > 0:
                    paths.append(os.path.join(source_root, f"object-set-{index + 1}",
                                              f"{object_name}.csv"))
        return paths
    if os.path.isdir(source_root):
        for name in sorted(os.listdir(source_root)):
            if sfdmu_export.object_set_dir_number(name):
                candidate = os.path.join(source_root, name, f"{object_name}.csv")
                if os.path.isfile(candidate):
                    paths.append(candidate)
    return paths


def apply_lookups(plan_dir: str, query: Callable[[str], List[dict]],
                  log: Callable[[str], None] = print) -> int:
    """Resolve every lookup in `plan_dir` IN PLACE (call it on a temp copy). Returns the
    number of child rows that received an Id; raises `IdLookupError` on any gap."""
    lookups = load_lookups(plan_dir)
    if not lookups:
        return 0
    with open(os.path.join(plan_dir, EXPORT_JSON_FILENAME), encoding="utf-8") as handle:
        export_data = json.load(handle)
    separated = sfdmu_export.is_js_truthy(export_data.get("useSeparatedCSVFiles"))
    filled = 0
    for lookup in lookups:
        object_name = lookup["object"]
        key_fields = lookup["keyFields"]
        prefer = lookup.get("prefer") or {}
        declared, passes = _declared_fields(export_data, object_name)
        records = query(lookup_soql(object_name, key_fields, declared, prefer))
        id_map, ambiguous = build_id_map(records, key_fields, prefer)
        log(f"{object_name}: {len(records)} target record(s), {len(id_map)} unique key(s)")

        parent_rows = [{f: _as_text(_record_value(r, f)) for f in declared}
                       for r in id_map.values()]
        for path in _csv_paths(plan_dir, object_name, passes, separated):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            _write_csv(path, declared, parent_rows)

        missing: Dict[tuple, List[str]] = {}
        tied: Dict[tuple, List[str]] = {}
        for child in lookup["children"]:
            id_column, key_columns = child["idColumn"], child["keyColumns"]
            for child_object in child["objects"]:
                for path in _csv_paths(plan_dir, child_object):
                    if not os.path.isfile(path):
                        continue
                    header, rows = _read_csv(path)
                    absent = [c for c in key_columns if c not in header]
                    if absent:
                        raise IdLookupError(f"{os.path.relpath(path, plan_dir)}: missing key "
                                            f"column(s) {absent}")
                    where = f"{child_object} ({os.path.relpath(path, plan_dir)})"
                    for row in rows:
                        key = tuple(row.get(c, "") for c in key_columns)
                        if key in ambiguous:
                            tied.setdefault(key, []).append(where)
                        elif key not in id_map:
                            missing.setdefault(key, []).append(where)
                        else:
                            row[id_column] = id_map[key]["Id"]
                            filled += 1
                    if id_column not in header:
                        header = [id_column] + header
                    _write_csv(path, header, rows)
        if missing or tied:
            lines = []
            for key, where in sorted(missing.items()):
                lines.append(f"  no {object_name} for {';'.join(key)} (used by {', '.join(sorted(set(where)))})")
            for key, where in sorted(tied.items()):
                lines.append(f"  {ambiguous[key]} {object_name} records tie for {';'.join(key)} "
                             f"(used by {', '.join(sorted(set(where)))})")
            ranked = f" with {', '.join(f'{k} in {v}' for k, v in prefer.items())}" if prefer else ""
            raise IdLookupError(
                f"Cannot resolve {object_name} Ids on the target org "
                f"(keyed on {';'.join(key_fields)}{ranked}):\n" + "\n".join(lines)
                + f"\nA missing key: load the plan that creates {object_name} first. A tie: "
                "remove the extra copy on the org (two copies with the same status for one key).")
    return filled


def prepare_extraction_export(export_data: dict, lookups: List[dict]) -> dict:
    """The export.json an EXTRACT of a lookup plan needs: Ids kept in the CSVs.

    SFDMU drops a child's 2-hop traversal columns (`ProductUsageResource.Product.StockKeepingUnit`)
    on extract, so the portable key cannot come back directly; the child's Id column can, and
    `restore_parent_keys` turns it back into the key. A boolean is set because SFDMU reads this
    flag with JS truthiness: the string "false" plans carry is truthy and drops every Id.
    """
    if lookups:
        export_data = dict(export_data)
        export_data["excludeIdsFromCSVFiles"] = False
    return export_data


def restore_parent_keys(extraction_dir: str, lookups: List[dict],
                        query: Callable[[str], List[dict]],
                        log: Callable[[str], None] = print, chunk: int = 200) -> int:
    """Fill each extracted child's `keyColumns` from its `idColumn` (IN PLACE), the reverse of
    `apply_lookups`, so post-processing writes portable keys. Returns rows filled; raises
    `IdLookupError` for an Id with no parent (the extract would otherwise lose the row's key)."""
    filled = 0
    for lookup in lookups:
        object_name, key_fields = lookup["object"], lookup["keyFields"]
        for child in lookup["children"]:
            id_column, key_columns = child["idColumn"], child["keyColumns"]
            for child_object in child["objects"]:
                path = os.path.join(extraction_dir, f"{child_object}.csv")
                if not os.path.isfile(path):
                    continue
                header, rows = _read_csv(path)
                if id_column not in header:
                    raise IdLookupError(f"{child_object}.csv was extracted without {id_column}; "
                                        "extract with excludeIdsFromCSVFiles false")
                blank = sum(1 for r in rows if r.get(id_column) in ("", "#N/A", None))
                if blank:
                    raise IdLookupError(f"{child_object}.csv: {blank} extracted row(s) have no "
                                        f"{id_column}, so their {object_name} key can't be restored")
                ids = sorted({r[id_column] for r in rows})
                bad = [i for i in ids if not _SALESFORCE_ID.fullmatch(i)]
                if bad:
                    raise IdLookupError(f"{child_object}.csv: {id_column} {bad[0]!r} is not a record Id")
                keys: Dict[str, tuple] = {}
                for start in range(0, len(ids), chunk):
                    in_list = ", ".join(f"'{i}'" for i in ids[start:start + chunk])
                    soql = f"SELECT Id, {', '.join(key_fields)} FROM {object_name} WHERE Id IN ({in_list})"
                    for record in query(soql):
                        keys[record["Id"]] = tuple(_as_text(_record_value(record, f)) for f in key_fields)
                unknown = [i for i in ids if i not in keys]
                if unknown:
                    raise IdLookupError(f"{child_object}: {len(unknown)} {id_column} value(s) match no "
                                        f"{object_name} on the org (e.g. {unknown[0]})")
                for row in rows:
                    key = keys.get(row.get(id_column))
                    if key is None:
                        continue
                    for column, value in zip(key_columns, key):
                        row[column] = value
                    filled += 1
                for column in key_columns:
                    if column not in header:
                        header.append(column)
                _write_csv(path, header, rows)
                log(f"{child_object}: restored {';'.join(key_columns)} on {len(rows)} row(s) from {id_column}")
    return filled


def strip_extraction_ids(extraction_dir: str, export_data: dict,
                         log: Callable[[str], None] = print) -> None:
    """Make an Id-keeping extract (`prepare_extraction_export`) portable again, IN PLACE.

    Run after `restore_parent_keys`. Deletes the CSV of every object the plan only reads
    (Readonly in every pass that declares it, e.g. the generated parent), and drops the `Id`
    column and every direct lookup column (`...Id`, no dot) from the rest; the traversal
    columns carry the portable values. Without this, post-processing keeps the extracted
    headers for objects with no tracked CSV, and `copy_to_plan` would write org Ids into the
    plan.
    """
    written: Dict[str, bool] = {}
    for object_set in sfdmu_export.normalize_object_sets(export_data):
        for obj in object_set.get("objects", []):
            if sfdmu_export.is_js_truthy(obj.get("excluded")):
                continue
            name = sfdmu_export.extract_object_name(obj.get("query", ""))
            if name:
                writable = sfdmu_export.resolve_operation(obj.get("operation")) != "readonly"
                written[name] = written.get(name, False) or writable
    for name in sorted(os.listdir(extraction_dir)):
        if not name.endswith(".csv"):
            continue
        object_name = name[:-4]
        path = os.path.join(extraction_dir, name)
        if object_name in written and not written[object_name]:
            os.remove(path)
            log(f"{name}: removed (read-only in this plan; it holds target-org Ids)")
            continue
        if object_name not in written:
            continue
        header, rows = _read_csv(path)
        keep = [c for c in header if c != "Id" and not (c.endswith("Id") and "." not in c)]
        if keep != header:
            _write_csv(path, keep, rows)
            log(f"{name}: dropped Id columns {[c for c in header if c not in keep]}")

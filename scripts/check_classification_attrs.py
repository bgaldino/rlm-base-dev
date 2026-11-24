#!/usr/bin/env python3
"""Compare ProductClassificationAttr values in an org against a PCM plan's CSV (read-only).

Measures PCM load fact (a) in `product-catalog-modeling/catalogs-and-loading.md`: after a
one-pass insert on a fresh org, classification attributes held the attribute definition's
`AttributeNameOverride` and `IsRequired` instead of the plan's. A second pass applied the plan's
values. This reads the org with one SOQL query (`sf data query`, no writes) and reports every
row whose value differs from the plan CSV, so you can see whether a build needs a second load.

  python scripts/check_classification_attrs.py --target-org <sf alias or username> \
      [--plan datasets/sfdmu/qb/en-US/qb-pcm] [--json out.json]

Exit 0 when every CSV row exists in the org and `AttributeNameOverride`, `IsRequired`,
`DefaultValue`, `Description` and `HelpText` (the fields an insert copies from the attribute
definition, per the trace in attributes-and-classifications.md, and an update does not) match the CSV. Exit 1 on a missing row or a difference in
those fields. Exit 2 when the comparison can't be trusted: a query or `sf` error or unexpected
payload, an unreadable CSV or unwritable --json file, a duplicate key in the CSV, or an org key
held by more than one row (another plan's rows would make the match ambiguous). Rows are keyed
on classification code, attribute definition code and attribute category code (blank when the
row has none).

A difference in any other field is printed as INFO and does not fail the run: a field the CSV
leaves blank (DisplayType, StepValue, Sequence) may be filled by the platform from the attribute
definition, which says nothing about a second load. Comparison is by value, not by
Id: a blank CSV cell equals a null org value, Is* fields compare as true/false, and only the
numeric fields compare numerically; text fields compare exactly after strip(). Org rows with no
CSV row are counted in the summary line (org-only) and not listed.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from pathlib import Path

FIELDS = [
    "AttributeNameOverride", "DefaultValue", "Description", "DisplayType", "HelpText",
    "IsHidden", "IsPriceImpacting", "IsReadOnly", "IsRequired", "MaximumCharacterCount",
    "MaximumValue", "MinimumCharacterCount", "MinimumValue", "Name", "Sequence", "Status",
    "StepValue", "ValueDescription",
]
# Fields an insert copies from the attribute definition and an update does not (fact a, traced in
# attributes-and-classifications.md); a difference here is what a second load would correct.
KEY_FIELDS = ("AttributeNameOverride", "IsRequired", "DefaultValue", "Description", "HelpText")
# Integer-typed fields (sobject describe: int); the org returns 1.0 where the CSV holds 1.
# MinimumValue, MaximumValue, StepValue and DefaultValue are strings, so they compare exactly.
NUMERIC_FIELDS = frozenset({"Sequence", "MaximumCharacterCount", "MinimumCharacterCount"})
SELECT = (
    "SELECT ProductClassification.Code, AttributeDefinition.Code, AttributeCategory.Code, "
    "UnitOfMeasure.UnitCode, " + ", ".join(FIELDS) + " FROM ProductClassificationAttr"
)
DEFAULT_PLAN = Path(__file__).resolve().parents[1] / "datasets/sfdmu/qb/en-US/qb-pcm"


class Untrusted(Exception):
    """The comparison can't be trusted (exit 2), as opposed to a real difference (exit 1)."""


def soql_literal(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def norm(value, field: str = "") -> str:
    """Normalize a CSV or org value for comparison. Blank equals null (a blank Is* cell is the false default). Only NUMERIC_FIELDS compare
    numerically ("007" == "7", "1e3" == "1000"), and only Is* fields compare as true/false; every
    other field compares exactly after strip(), so text such as "1.0" and "1" differs."""
    if value is None:
        return "false" if field.startswith("Is") else ""
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value).strip()
    if field.startswith("Is") and text.lower() in ("", "true", "false"):
        return text.lower() or "false"
    if field not in NUMERIC_FIELDS:
        return text
    try:
        number = float(text)
    except ValueError:
        return text
    if not math.isfinite(number):  # "nan" / "inf" are text, not numbers
        return text
    return str(int(number)) if number == int(number) else str(number)


def row_key(cls: str, attr: str, cat: str) -> tuple[str, str, str]:
    return (cls or "", attr or "", cat or "")


def read_csv(plan: Path) -> dict:
    path = plan / "ProductClassificationAttr.csv"
    rows = {}
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            for rec in csv.DictReader(fh):
                key = row_key(rec["ProductClassification.Code"], rec["AttributeDefinition.Code"],
                              rec.get("AttributeCategory.Code", ""))
                if key in rows:
                    raise Untrusted(f"duplicate CSV key {key}")
                rows[key] = rec
    except (OSError, KeyError) as exc:
        raise Untrusted(f"can't read {path}: {exc!r}") from exc
    return rows


def build_query(classification_codes) -> str:
    codes = sorted({c for c in classification_codes if c})
    literals = ", ".join(soql_literal(c) for c in codes)
    where = f" WHERE ProductClassification.Code IN ({literals})" if codes else ""
    return SELECT + where


def index_org(records) -> tuple[dict, dict]:
    """Return (rows by key, keys held by more than one row -> row count)."""
    rows, counts = {}, {}
    for rec in records:
        def code(rel):
            return (rec.get(rel) or {}).get("Code") or ""
        key = row_key(code("ProductClassification"), code("AttributeDefinition"),
                      code("AttributeCategory"))
        counts[key] = counts.get(key, 0) + 1
        rows[key] = rec
    return rows, {k: n for k, n in counts.items() if n > 1}


def read_org(target: str, query: str) -> list:
    try:
        proc = subprocess.run(
            ["sf", "data", "query", "--query", query, "--target-org", target, "--json"],
            capture_output=True, text=True)
    except OSError as exc:
        raise Untrusted(f"can't run sf: {exc!r}") from exc
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise Untrusted((proc.stdout + proc.stderr)[:2000]) from exc
    if not isinstance(payload, dict):
        raise Untrusted(f"unexpected sf output: {proc.stdout[:500]}")
    if payload.get("status") != 0:
        raise Untrusted(json.dumps(payload.get("message") or payload)[:2000])
    try:
        return payload["result"]["records"]
    except (KeyError, TypeError) as exc:
        raise Untrusted(f"unexpected sf payload: {json.dumps(payload)[:500]}") from exc


def compare(expected: dict, actual: dict) -> tuple[list, list, list]:
    diffs, missing = [], []
    for key, rec in sorted(expected.items()):
        org = actual.get(key)
        if org is None:
            missing.append(key)
            continue
        for field in FIELDS:
            want, got = norm(rec.get(field), field), norm(org.get(field), field)
            if want != got:
                diffs.append({"key": list(key), "field": field, "csv": want, "org": got})
        want_uom = norm(rec.get("UnitOfMeasure.UnitCode"))
        got_uom = norm((org.get("UnitOfMeasure") or {}).get("UnitCode"))
        if want_uom != got_uom:
            diffs.append({"key": list(key), "field": "UnitOfMeasure.UnitCode",
                          "csv": want_uom, "org": got_uom})
    return diffs, missing, sorted(set(actual) - set(expected))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--target-org", required=True)
    ap.add_argument("--plan", default=str(DEFAULT_PLAN))
    ap.add_argument("--json", help="write the differences to this file")
    args = ap.parse_args(argv)
    try:
        expected = read_csv(Path(args.plan))
        query = build_query(k[0] for k in expected)
        actual, dupes = index_org(read_org(args.target_org, query))
    except Untrusted as exc:
        sys.stderr.write(f"cannot compare: {exc}\n")
        return 2
    ambiguous = sorted(k for k in dupes if k in expected)
    if ambiguous:
        for key in ambiguous:
            sys.stderr.write(
                f"AMBIGUOUS  {' | '.join(key)}: {dupes[key]} org rows share this key\n")
        sys.stderr.write("cannot compare: org keys held by more than one row\n")
        return 2
    diffs, missing, extra = compare(expected, actual)
    key_diffs = [d for d in diffs if d["field"] in KEY_FIELDS]

    print(f"CSV rows: {len(expected)}  org rows: {len(actual)}  "
          f"missing in org: {len(missing)}  differences: {len(diffs)} ({len(key_diffs)} key)  "
          f"org-only (Info): {len(extra)}")
    for key in missing:
        print(f"MISSING  {' | '.join(key)}")
    for d in diffs:
        flag = "DIFF KEY " if d["field"] in KEY_FIELDS else "INFO     "
        print(f"{flag}{' | '.join(d['key'])}  {d['field']}: csv={d['csv']!r} org={d['org']!r}")
    by_field: dict[str, int] = {}
    for d in diffs:
        by_field[d["field"]] = by_field.get(d["field"], 0) + 1
    if by_field:
        print("Differences by field: " + ", ".join(f"{k}={v}" for k, v in sorted(by_field.items())))
    if args.json:
        try:
            Path(args.json).write_text(json.dumps(
                {"missing": [list(k) for k in missing], "differences": diffs,
                 "org_only": [list(k) for k in extra]}, indent=2))
        except OSError as exc:
            sys.stderr.write(f"cannot write {args.json}: {exc}\n")
            return 2
    return 1 if (key_diffs or missing) else 0


if __name__ == "__main__":
    sys.exit(main())

"""
Compare two OmniDataTransforms item-by-item to find differences.

Useful for debugging cloned ODTs or verifying a new ODT matches
its source after modifications.

Usage:
  python scripts/ai/docgen/compare_odts.py <source_name_or_id> <target_name_or_id> --org <sf_alias>
  python scripts/ai/docgen/compare_odts.py BillingDocumentGenerationGetInvoiceDetails RLMInvoiceGetDetails --org gartnerCollect
"""
import argparse
import json
import subprocess
import sys
from collections import defaultdict


COMPARE_FIELDS = [
    "InputFieldName",
    "OutputFieldName",
    "InputObjectName",
    "OutputObjectName",
    "InputObjectQuerySequence",
    "OutputCreationSequence",
    "FilterOperator",
    "FilterValue",
    "FilterGroup",
    "FormulaExpression",
    "OutputFieldFormat",
]


def sf_query(query, org):
    result = subprocess.run(
        ["sf", "data", "query", "-q", query, "--target-org", org, "--json"],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(result.stdout)
        if data.get("status") != 0:
            print(f"ERROR: {data.get('message', '')}", file=sys.stderr)
            return None
        return data["result"]["records"]
    except (json.JSONDecodeError, KeyError):
        print(f"ERROR: Failed to parse query result", file=sys.stderr)
        return None


def resolve_odt(name_or_id, org):
    if name_or_id.startswith("0jI"):
        records = sf_query(
            f"SELECT Id, Name, Type, IsActive, InputType, OutputType "
            f"FROM OmniDataTransform WHERE Id = '{name_or_id}'",
            org,
        )
    else:
        records = sf_query(
            f"SELECT Id, Name, Type, IsActive, InputType, OutputType "
            f"FROM OmniDataTransform WHERE Name = '{name_or_id}'",
            org,
        )
    if not records:
        print(f"ERROR: ODT '{name_or_id}' not found", file=sys.stderr)
        sys.exit(1)
    return records[0]


def get_items(odt_id, org):
    fields = ", ".join(["Id", "Name"] + COMPARE_FIELDS)
    return sf_query(
        f"SELECT {fields} "
        f"FROM OmniDataTransformItem WHERE OmniDataTransformationId = '{odt_id}' "
        f"ORDER BY InputObjectQuerySequence, OutputCreationSequence, OutputFieldName",
        org,
    )


def item_key(item):
    return (
        item.get("InputObjectQuerySequence"),
        item.get("OutputCreationSequence"),
        item.get("OutputFieldName") or "",
        item.get("InputObjectName") or "",
        item.get("InputFieldName") or "",
        item.get("FilterValue") or "",
        item.get("FilterGroup"),
    )


def compare_odt_headers(source, target):
    diffs = []
    for field in ["Type", "InputType", "OutputType", "IsActive"]:
        sv = source.get(field)
        tv = target.get(field)
        if sv != tv:
            diffs.append((field, sv, tv))
    return diffs


def detect_duplicates(items, label):
    """Report items that share the same key (potential duplicate queries)."""
    by_key = defaultdict(list)
    for item in items:
        k = item_key(item)
        by_key[k].append(item)

    duplicates = []
    for k, group in by_key.items():
        if len(group) > 1:
            duplicates.append({
                "key": k,
                "count": len(group),
                "ids": [item["Id"] for item in group],
                "side": label,
            })

    return by_key, duplicates


def compare_items(source_items, target_items):
    source_by_key, source_dupes = detect_duplicates(source_items, "source")
    target_by_key, target_dupes = detect_duplicates(target_items, "target")

    only_in_source = []
    only_in_target = []
    field_diffs = []

    for k, s_group in source_by_key.items():
        s_item = s_group[0]
        if k not in target_by_key:
            only_in_source.append(s_item)
        else:
            t_item = target_by_key[k][0]
            for field in COMPARE_FIELDS:
                sv = s_item.get(field)
                tv = t_item.get(field)
                if sv != tv:
                    field_diffs.append({
                        "key": k,
                        "field": field,
                        "source_value": sv,
                        "target_value": tv,
                        "source_id": s_item["Id"],
                        "target_id": t_item["Id"],
                    })

    for k, t_group in target_by_key.items():
        if k not in source_by_key:
            only_in_target.append(t_group[0])

    return only_in_source, only_in_target, field_diffs, source_dupes + target_dupes


def format_item(item):
    parts = []
    if item.get("InputObjectName"):
        parts.append(f"ObjQuery: {item['InputObjectName']}")
    if item.get("InputFieldName"):
        parts.append(f"In={item['InputFieldName']}")
    if item.get("OutputFieldName"):
        parts.append(f"Out={item['OutputFieldName']}")
    if item.get("FilterValue"):
        parts.append(f"Filter={item['FilterValue']}")
    return " | ".join(parts) if parts else item.get("Id", "?")


def main():
    parser = argparse.ArgumentParser(description="Compare two ODTs")
    parser.add_argument("source", help="Source ODT Name or Id")
    parser.add_argument("target", help="Target ODT Name or Id")
    parser.add_argument("--org", required=True, help="SF CLI target org alias")
    args = parser.parse_args()

    source = resolve_odt(args.source, args.org)
    target = resolve_odt(args.target, args.org)

    print(f"Source: {source['Name']} ({source['Id']})")
    print(f"Target: {target['Name']} ({target['Id']})")

    header_diffs = compare_odt_headers(source, target)
    if header_diffs:
        print(f"\n--- ODT Header Differences ---")
        for field, sv, tv in header_diffs:
            print(f"  {field}: source={sv} → target={tv}")

    source_items = get_items(source["Id"], args.org)
    target_items = get_items(target["Id"], args.org)

    if source_items is None or target_items is None:
        sys.exit(1)

    print(f"\nSource items: {len(source_items)}")
    print(f"Target items: {len(target_items)}")

    only_source, only_target, diffs, duplicates = compare_items(source_items, target_items)

    if duplicates:
        print(f"\n--- Duplicate Items ({len(duplicates)}) ---")
        for d in duplicates:
            print(f"  ⚠ {d['side']}: {d['count']} items share the same key — IDs: {d['ids']}")

    if only_source:
        print(f"\n--- Only in Source ({len(only_source)}) ---")
        for item in only_source:
            print(f"  {item['Id']}: {format_item(item)}")

    if only_target:
        print(f"\n--- Only in Target ({len(only_target)}) ---")
        for item in only_target:
            print(f"  {item['Id']}: {format_item(item)}")

    if diffs:
        print(f"\n--- Field Differences ({len(diffs)}) ---")
        for d in diffs:
            print(
                f"  [{d['field']}] source={d['source_value']!r} → "
                f"target={d['target_value']!r}"
            )
            print(f"    Source ID: {d['source_id']}  Target ID: {d['target_id']}")

    total_issues = (
        len(only_source) + len(only_target) + len(diffs)
        + len(header_diffs) + len(duplicates)
    )
    if total_issues == 0:
        print("\n✓ ODTs are equivalent")
    else:
        print(f"\n✗ {total_issues} difference(s) found")
        sys.exit(1)


if __name__ == "__main__":
    main()

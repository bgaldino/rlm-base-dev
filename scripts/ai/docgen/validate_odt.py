"""
Validate an OmniDataTransform and its items for common issues.

Checks for:
  - Null OutputObjectName (causes NPE at runtime)
  - Missing InputFieldName on object query items
  - Missing FilterGroup on object query items
  - Dot notation in InputFieldName (should be colons)
  - Duplicate object query items
  - Items with empty required fields

Usage:
  python scripts/ai/docgen/validate_odt.py <odt_name_or_id> --org <sf_alias>
  python scripts/ai/docgen/validate_odt.py RLMInvoiceGetDetails --org gartnerCollect
  python scripts/ai/docgen/validate_odt.py 0jIbm000000CKXdEAO --org gartnerCollect
"""
import argparse
import json
import subprocess
import sys
from collections import defaultdict


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
            f"SELECT Id, Name, Type, IsActive FROM OmniDataTransform WHERE Id = '{name_or_id}'",
            org,
        )
    else:
        records = sf_query(
            f"SELECT Id, Name, Type, IsActive FROM OmniDataTransform WHERE Name = '{name_or_id}'",
            org,
        )
    if not records:
        print(f"ERROR: ODT '{name_or_id}' not found", file=sys.stderr)
        sys.exit(1)
    return records[0]


def get_items(odt_id, org):
    return sf_query(
        f"SELECT Id, Name, InputFieldName, OutputFieldName, InputObjectName, "
        f"OutputObjectName, InputObjectQuerySequence, FilterOperator, FilterValue, "
        f"FilterGroup, OutputCreationSequence, FormulaExpression, FormulaConverted, "
        f"FormulaResultPath, OutputFieldFormat "
        f"FROM OmniDataTransformItem WHERE OmniDataTransformationId = '{odt_id}' "
        f"ORDER BY InputObjectQuerySequence, OutputCreationSequence, OutputFieldName",
        org,
    )


def validate(odt, items):
    errors = []
    warnings = []

    # Check ODT-level
    if not odt.get("IsActive"):
        warnings.append(f"ODT is not Active")

    # Separate object queries from field mappings
    obj_queries = [i for i in items if i.get("InputObjectName")]
    field_maps = [i for i in items if not i.get("InputObjectName")]

    # Check 1: Null OutputObjectName
    for item in items:
        if item.get("OutputObjectName") is None:
            errors.append(
                f"NULL OutputObjectName: {item['Id']} "
                f"(Output={item.get('OutputFieldName', '?')})"
            )

    # Check 2: Object queries missing InputFieldName
    for item in obj_queries:
        if not item.get("InputFieldName"):
            errors.append(
                f"Missing InputFieldName on object query: {item['Id']} "
                f"({item['InputObjectName']} -> {item.get('OutputFieldName', '?')})"
            )

    # Check 3: Object queries missing FilterGroup
    for item in obj_queries:
        if item.get("FilterGroup") is None:
            errors.append(
                f"Missing FilterGroup on object query: {item['Id']} "
                f"({item['InputObjectName']} -> {item.get('OutputFieldName', '?')})"
            )

    # Check 4: Dot notation in InputFieldName
    for item in field_maps:
        inp = item.get("InputFieldName", "") or ""
        if "." in inp and not inp.startswith("$"):
            errors.append(
                f"Dot notation in InputFieldName: {item['Id']} "
                f"('{inp}' -> {item.get('OutputFieldName', '?')}) — use colons"
            )

    # Check 5: Duplicate object queries
    seen = defaultdict(list)
    for item in obj_queries:
        key = (
            item.get("InputObjectQuerySequence"),
            item.get("InputObjectName"),
            item.get("OutputFieldName"),
            item.get("FilterValue"),
        )
        seen[key].append(item["Id"])

    for key, ids in seen.items():
        if len(ids) > 1:
            errors.append(
                f"Duplicate object query (Seq={key[0]}, {key[1]} -> {key[2]}, "
                f"Filter={key[3]}): {len(ids)} copies — IDs: {ids}"
            )

    # Check 6: Field mappings missing OutputFieldName
    for item in items:
        if not item.get("OutputFieldName"):
            if not item.get("FormulaExpression"):
                warnings.append(
                    f"Empty OutputFieldName: {item['Id']} "
                    f"(Input={item.get('InputFieldName', '?')})"
                )

    # Check 7: Formula items with null FormulaConverted (unsupported function)
    for item in items:
        if item.get("FormulaExpression") and not item.get("FormulaConverted"):
            errors.append(
                f"Unsupported formula (null FormulaConverted): {item['Id']} "
                f"(ResultPath={item.get('FormulaResultPath', '?')}, "
                f"Expr={item.get('FormulaExpression', '?')[:60]})"
            )

    # Check 8: Field mappings with OutputCreationSequence != 1 (silently produces no output)
    for item in field_maps:
        ocs = item.get("OutputCreationSequence")
        if ocs is not None and ocs != 1:
            if not item.get("FormulaExpression"):
                errors.append(
                    f"OutputCreationSequence={ocs} on field mapping: {item['Id']} "
                    f"('{item.get('InputFieldName', '?')}' -> "
                    f"'{item.get('OutputFieldName', '?')}') — must be 1 to produce output"
                )

    # Check 9: Bare literal FilterValue (silently ignored — no WHERE condition generated)
    for item in obj_queries:
        fv = item.get("FilterValue") or ""
        if fv and ":" not in fv and not fv.startswith("'") and fv != "Id":
            warnings.append(
                f"Bare literal FilterValue '{fv}' on: {item['Id']} "
                f"({item.get('InputObjectName', '?')}) — unquoted literals are "
                f"silently ignored. Use single quotes: \"'{fv}'\" "
            )

    # Check 10: IMG_ token contract (Transform ODTs) — require src, width, height items
    img_outputs = defaultdict(set)
    for item in items:
        out = item.get("OutputFieldName") or ""
        obj = item.get("OutputObjectName") or ""
        if obj.startswith("IMG_"):
            img_outputs[obj].add(out)
        elif out.startswith("IMG_") and ":" in out:
            token = out.split(":")[0]
            field = out.split(":", 1)[1]
            img_outputs[token].add(field)

    for token, fields in img_outputs.items():
        required = {"src", "width", "height"}
        missing = required - fields
        if missing:
            errors.append(
                f"{token} missing required fields: {sorted(missing)} "
                f"— image will silently fail to render"
            )
        if "src" in fields:
            src_items = [
                i for i in items
                if (i.get("OutputFieldName") or "").endswith(":src")
                or (i.get("OutputObjectName") or "") == token
                and (i.get("OutputFieldName") or "") == "src"
            ]
            for si in src_items:
                inp = si.get("InputFieldName") or ""
                if inp and inp.startswith("'") and not inp.strip("'").startswith("069"):
                    warnings.append(
                        f"{token}:src literal '{inp}' does not start with '069' "
                        f"(ContentDocument prefix) — may crash the engine"
                    )

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate an OmniDataTransform")
    parser.add_argument("odt", help="ODT Name or Id")
    parser.add_argument("--org", required=True, help="SF CLI target org alias")
    args = parser.parse_args()

    odt = resolve_odt(args.odt, args.org)
    print(f"Validating: {odt['Name']} ({odt['Id']})")
    print(f"  Type: {odt['Type']}  Active: {odt['IsActive']}")

    items = get_items(odt["Id"], args.org)
    if items is None:
        sys.exit(1)

    print(f"  Items: {len(items)}")

    obj_queries = [i for i in items if i.get("InputObjectName")]
    field_maps = [i for i in items if not i.get("InputObjectName")]
    print(f"    Object queries: {len(obj_queries)}")
    print(f"    Field mappings: {len(field_maps)}")

    errors, warnings = validate(odt, items)

    if warnings:
        print(f"\n⚠ {len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\n✗ {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"\n✓ No errors found")


if __name__ == "__main__":
    main()

"""
Create an OmniDataTransform (Extract or Transform) from a JSON spec file.

Supports creating ODTs from scratch — no source ODT required.
Handles all item types: object queries, field mappings, pass-throughs,
formulas, and array builders.

Usage:
  python scripts/ai/docgen/docgen_create_odt.py spec.json --org <sf_alias>
  python scripts/ai/docgen/docgen_create_odt.py spec.json --org gartnerCollect --dry-run

Spec file format (see --example for a full template):
  python scripts/ai/docgen/docgen_create_odt.py --example extract > my_extract_spec.json
  python scripts/ai/docgen/docgen_create_odt.py --example transform > my_transform_spec.json
"""
import argparse
import json
import subprocess
import sys
import tempfile
import time


EXTRACT_EXAMPLE = {
    "_comment": "Extract ODT spec — queries org data for a document template",
    "odt": {
        "Name": "MyDocGenExtract",
        "Type": "Extract",
        "InputType": "JSON",
        "OutputType": "JSON",
        "IsActive": True,
        "IsFieldLevelSecurityEnabled": True,
        "IsNullInputsIncludedInOutput": False,
        "IsManagedUsingStdDesigner": False,
        "VersionNumber": 1,
    },
    "items": [
        {
            "_comment": "Object query — joins Invoice to its parent Account",
            "type": "object_query",
            "InputObjectName": "Invoice",
            "InputFieldName": "Id",
            "OutputFieldName": "Invoice",
            "OutputObjectName": "json",
            "InputObjectQuerySequence": 1,
            "FilterOperator": "=",
            "FilterValue": "Id",
            "FilterGroup": "0",
        },
        {
            "_comment": "Object query — join Account from Invoice",
            "type": "object_query",
            "InputObjectName": "Account",
            "InputFieldName": "Id",
            "OutputFieldName": "Invoice:Account",
            "OutputObjectName": "json",
            "InputObjectQuerySequence": 2,
            "FilterOperator": "=",
            "FilterValue": "Invoice:BillingAccountId",
            "FilterGroup": "0",
        },
        {
            "_comment": "Field mapping — extracts a field from the queried data",
            "type": "field_mapping",
            "InputFieldName": "Invoice:DocumentNumber",
            "OutputFieldName": "InvoiceNumber",
            "OutputObjectName": "json",
            "OutputCreationSequence": 1,
        },
        {
            "_comment": "Field mapping — traversal path uses colons, not dots",
            "type": "field_mapping",
            "InputFieldName": "Invoice:Account:Name",
            "OutputFieldName": "AccountName",
            "OutputObjectName": "json",
            "OutputCreationSequence": 1,
        },
    ],
}

TRANSFORM_EXAMPLE = {
    "_comment": "Transform ODT spec — reshapes Extract output for template tokens",
    "odt": {
        "Name": "MyDocGenTransform",
        "Type": "Transform",
        "InputType": "JSON",
        "OutputType": "JSON",
        "IsActive": True,
        "IsFieldLevelSecurityEnabled": True,
        "IsNullInputsIncludedInOutput": False,
        "IsManagedUsingStdDesigner": False,
        "VersionNumber": 1,
    },
    "items": [
        {
            "_comment": "Pass-through — maps Extract output directly to template token",
            "type": "passthrough",
            "InputFieldName": "InvoiceNumber",
            "OutputFieldName": "InvoiceNumber",
            "OutputObjectName": "json",
            "OutputCreationSequence": 1,
        },
        {
            "_comment": "Formula — builds an array for repeating sections",
            "type": "formula",
            "OutputFieldName": "Formula",
            "OutputObjectName": "Formula",
            "FormulaExpression": "LIST(InvoiceLines, 'InvoiceLineNumber', InvoiceLineNumber, 'Description', Description, 'TotalAmount', TotalAmount)",
            "FormulaResultPath": "InvoiceLines",
            "FormulaSequence": 1,
            "OutputCreationSequence": 0,
        },
        {
            "_comment": "Object output — passes a formula array to template",
            "type": "object_output",
            "InputFieldName": "InvoiceLines",
            "OutputFieldName": "InvoiceLines",
            "OutputObjectName": "json",
            "OutputFieldFormat": "Object",
            "OutputCreationSequence": 2,
        },
    ],
}


def sf_api(method, path, body, org, dry_run=False):
    if dry_run:
        print(f"  [DRY RUN] {method} {path}")
        print(f"    Body: {json.dumps(body, indent=2)[:200]}...")
        return {"id": "DRY_RUN_ID", "success": True}

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(body, f)
        tmp_path = f.name

    result = subprocess.run(
        ["sf", "api", "request", "rest", "--method", method,
         "--body", f"@{tmp_path}", path, "--target-org", org],
        capture_output=True, text=True,
    )

    try:
        data = json.loads(result.stdout)
        return data
    except json.JSONDecodeError:
        if result.returncode == 0 and not result.stdout.strip():
            return {"success": True}
        print(f"ERROR: {result.stderr or result.stdout}", file=sys.stderr)
        return None


def build_item_body(item_spec, odt_id, odt_name):
    body = {
        "Name": odt_name,
        "OmniDataTransformationId": odt_id,
        "OutputObjectName": item_spec.get("OutputObjectName", "json"),
    }

    skip_keys = {"_comment", "type"}
    for k, v in item_spec.items():
        if k not in skip_keys and v is not None:
            body[k] = v

    item_type = item_spec.get("type", "")
    if item_type in ("field_mapping", "passthrough", "object_output"):
        ocs = body.get("OutputCreationSequence")
        if ocs is not None and ocs != 1 and ocs != 0:
            print(f"  ⚠ WARNING: OutputCreationSequence={ocs} on field mapping "
                  f"'{body.get('OutputFieldName', '?')}' — must be 1 (or 0 for "
                  f"formulas) to produce output. Forcing to 1.",
                  file=sys.stderr)
            body["OutputCreationSequence"] = 1

    if item_type == "object_query":
        fv = body.get("FilterValue", "")
        if fv and ":" not in fv and not fv.startswith("'"):
            print(f"  ⚠ WARNING: FilterValue '{fv}' on '{body.get('OutputFieldName', '?')}' "
                  f"is a bare literal — must be single-quoted (e.g., \"'{fv}'\") "
                  f"to generate a WHERE condition. Unquoted literals are silently ignored.",
                  file=sys.stderr)

    return body


def create_odt(spec, org, dry_run=False):
    odt_body = dict(spec["odt"])
    odt_name = odt_body["Name"]

    if odt_body.get("Type") == "Transform":
        if not odt_body.get("InputType"):
            print(f"  ⚠ WARNING: Transform missing InputType — adding 'JSON' "
                  f"(Designer blocks without it).", file=sys.stderr)
            odt_body["InputType"] = "JSON"
        if not odt_body.get("TargetOutputFileName"):
            target = f"{odt_name}(Version 1)"
            print(f"  ⚠ WARNING: Transform missing TargetOutputFileName — "
                  f"adding '{target}' (Designer blocks without it).",
                  file=sys.stderr)
            odt_body["TargetOutputFileName"] = target

    print(f"Creating ODT: {odt_name} (Type={odt_body['Type']})")
    result = sf_api(
        "POST", "/services/data/v67.0/sobjects/OmniDataTransform", odt_body, org, dry_run
    )

    if not result:
        print("ERROR: Failed to create ODT", file=sys.stderr)
        sys.exit(1)

    if isinstance(result, list):
        print(f"ERROR: {result}", file=sys.stderr)
        sys.exit(1)
    if not result.get("success") and not result.get("id"):
        errors = result.get("errors") or result
        print(f"ERROR: {errors}", file=sys.stderr)
        sys.exit(1)

    odt_id = result.get("id", "DRY_RUN_ID")
    print(f"  Created: {odt_id}")

    items = spec.get("items", [])
    print(f"\nCreating {len(items)} items...")

    success_count = 0
    error_count = 0

    for i, item_spec in enumerate(items, 1):
        item_type = item_spec.get("type", "unknown")
        out_field = item_spec.get("OutputFieldName", "?")
        body = build_item_body(item_spec, odt_id, odt_name)

        result = sf_api(
            "POST",
            "/services/data/v67.0/sobjects/OmniDataTransformItem",
            body,
            org,
            dry_run,
        )

        if result and (result.get("success") or result.get("id")):
            item_id = result.get("id", "?")
            print(f"  [{i}/{len(items)}] ✓ {item_type}: {out_field} ({item_id})")
            success_count += 1
        else:
            errors = result.get("errors") if result else "No response"
            print(f"  [{i}/{len(items)}] ✗ {item_type}: {out_field} — {errors}")
            error_count += 1

    print(f"\nDone: {success_count} created, {error_count} failed")
    if odt_id != "DRY_RUN_ID":
        print(f"ODT Id: {odt_id}")
        formula_items = [i for i in items if i.get("type") == "formula"]
        if formula_items and not dry_run:
            _check_formula_converted(odt_id, org)
        print(f"\nNext steps:")
        print(f"  1. Validate: python scripts/ai/docgen/validate_odt.py {odt_name} --org {org}")
        print(f"  2. Re-toggle if editing items later:")
        print(f"     sf api request rest --method PATCH --body @/tmp/p.json ...")

    return odt_id


def _check_formula_converted(odt_id, org):
    """Warn if any formula items have null FormulaConverted (unsupported function)."""
    query = (
        f"SELECT FormulaExpression, FormulaConverted, FormulaResultPath "
        f"FROM OmniDataTransformItem "
        f"WHERE OmniDataTransformationId = '{odt_id}' "
        f"AND FormulaExpression != null"
    )
    result = subprocess.run(
        ["sf", "data", "query", "-q", query, "--target-org", org, "--json"],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(result.stdout)
        records = data.get("result", {}).get("records", [])
        bad = [r for r in records if not r.get("FormulaConverted")]
        if bad:
            print(f"\n⚠ WARNING: {len(bad)} formula(s) have null FormulaConverted "
                  f"(unsupported function — will silently produce no output):")
            for r in bad:
                print(f"    {r.get('FormulaResultPath','?')}: {r.get('FormulaExpression','?')}")
    except (json.JSONDecodeError, KeyError):
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Create an OmniDataTransform from a JSON spec"
    )
    parser.add_argument("spec", nargs="?", help="Path to spec JSON file")
    parser.add_argument("--org", help="SF CLI target org alias")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print API calls without executing",
    )
    parser.add_argument(
        "--example",
        choices=["extract", "transform"],
        help="Print an example spec file and exit",
    )
    args = parser.parse_args()

    if args.example:
        example = EXTRACT_EXAMPLE if args.example == "extract" else TRANSFORM_EXAMPLE
        print(json.dumps(example, indent=2))
        return

    if not args.spec:
        parser.error("spec file required (or use --example)")

    if not args.org and not args.dry_run:
        parser.error("--org required (or use --dry-run)")

    try:
        with open(args.spec) as f:
            spec = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Spec file not found: {args.spec}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in spec: {e}", file=sys.stderr)
        sys.exit(1)

    if "odt" not in spec:
        print("ERROR: Spec must have an 'odt' key with ODT fields", file=sys.stderr)
        sys.exit(1)

    create_odt(spec, args.org, args.dry_run)


if __name__ == "__main__":
    main()

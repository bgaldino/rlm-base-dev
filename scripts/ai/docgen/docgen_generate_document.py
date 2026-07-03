"""
Trigger full document generation (DGP) via REST API and poll for completion.

Creates a DocumentGenerationProcess record, polls until completion, and
returns the generated ContentDocument ID(s). Supports both ODT-based and
ContextService-based templates.

This enables end-to-end template testing from the CLI: verify that an
Extract + Transform + .docx template produces a valid document, without
needing to click through the UI.

Usage:
  python scripts/ai/docgen/docgen_generate_document.py --record-id <id> --template-id <id> --org <alias>
  python scripts/ai/docgen/docgen_generate_document.py --record-id 0Q0O4000004gZiD --template-id 0TR... --org rlm-base__beta
  python scripts/ai/docgen/docgen_generate_document.py --record-id 0Q0O4000004gZiD --template-id 0TR... --org rlm-base__beta --title "Test Quote Proposal"
  python scripts/ai/docgen/docgen_generate_document.py --record-id 0Q0O4000004gZiD --template-id 0TR... --org rlm-base__beta --json

Options:
  --title       Custom document filename (default: auto-generated)
  --json        Output full DGP record as JSON on completion
  --timeout     Max seconds to wait for generation (default: 120)
  --no-convert  Generate .docx only (skip PDF conversion)
"""
import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _soql import soql_escape


def sf_api_post(path, body, org):
    """POST to Salesforce REST API, return parsed JSON."""
    import os
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(body, f)
            tmp_path = f.name

        result = subprocess.run(
            ["sf", "api", "request", "rest", "--method", "POST",
             "--body", f"@{tmp_path}", path, "--target-org", org],
            capture_output=True, text=True,
        )
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        if result.returncode != 0:
            print(f"ERROR: {result.stderr or result.stdout}", file=sys.stderr)
        return None


def sf_query(query, org):
    """Run SOQL query, return records list."""
    result = subprocess.run(
        ["sf", "data", "query", "-q", query, "--target-org", org, "--json"],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(result.stdout)
        if data.get("status") != 0:
            print(f"QUERY ERROR: {data.get('message', '')}", file=sys.stderr)
            return None
        return data["result"]["records"]
    except (json.JSONDecodeError, KeyError):
        print(f"ERROR: Failed to parse query result", file=sys.stderr)
        return None


def resolve_template(template_id, org):
    """Look up DocumentTemplate to determine mapping method."""
    escaped = soql_escape(template_id)
    records = sf_query(
        f"SELECT Id, Name, TokenMappingMethodType FROM DocumentTemplate "
        f"WHERE Id = '{escaped}'", org
    )
    if not records:
        print(f"ERROR: DocumentTemplate '{template_id}' not found", file=sys.stderr)
        sys.exit(1)
    return records[0]


def create_dgp(record_id, template_id, org, title=None, generate_only=False,
               mapping_method=None):
    """Create a DocumentGenerationProcess record to trigger generation."""
    dgp_type = "Generate" if generate_only else "GenerateAndConvert"

    body = {
        "Type": dgp_type,
        "ReferenceObject": record_id,
        "DocumentTemplateId": template_id,
        "DocGenApiVersionType": "Advanced",
        "DocumentInputType": "DocumentTemplate",
    }

    request_text = {"keepIntermediate": True}
    if title:
        request_text["title"] = title
    body["RequestText"] = json.dumps(request_text)

    if mapping_method == "ContextService":
        body["DocGenAdditionalInputType"] = "ContextService"
        body["DocGenAdditionalInput"] = json.dumps({
            "inputData": {"Quote": {"id": record_id}}
        })
    else:
        body["DataRaptorInput"] = json.dumps({"Id": record_id})

    result = sf_api_post(
        "/services/data/v67.0/sobjects/DocumentGenerationProcess",
        body, org
    )

    if not result:
        print("ERROR: Failed to create DocumentGenerationProcess", file=sys.stderr)
        sys.exit(1)

    if isinstance(result, list):
        print(f"ERROR: {result}", file=sys.stderr)
        sys.exit(1)

    if not result.get("success") and not result.get("id"):
        print(f"ERROR: {result.get('errors', result)}", file=sys.stderr)
        sys.exit(1)

    return result.get("id")


def poll_dgp(dgp_id, org, timeout=120):
    """Poll DGP status until completion or timeout."""
    start = time.time()
    last_status = None
    escaped_id = soql_escape(dgp_id)
    consecutive_errors = 0

    while time.time() - start < timeout:
        records = sf_query(
            f"SELECT Id, Status, ResponseText, ReferenceObject "
            f"FROM DocumentGenerationProcess WHERE Id = '{escaped_id}'", org
        )
        if not records:
            consecutive_errors += 1
            if consecutive_errors >= 5:
                print(f"ERROR: Query failed {consecutive_errors} times in a row",
                      file=sys.stderr)
                return None
            time.sleep(3)
            continue
        consecutive_errors = 0

        dgp = records[0]
        status = dgp.get("Status")

        if status != last_status:
            elapsed = int(time.time() - start)
            print(f"  [{elapsed}s] Status: {status}")
            last_status = status

        if status in ("Completed", "Success"):
            return dgp
        elif status in ("Failed", "Error"):
            return dgp

        time.sleep(3)

    print(f"ERROR: Timed out after {timeout}s (last status: {last_status})",
          file=sys.stderr)
    return None


def extract_content_ids(response_text):
    """Parse ResponseText to extract ContentVersion IDs.

    ResponseText format is comma-separated ContentVersion IDs (068 prefix):
      "068xx000001ABC,068xx000001DEF"
    First ID is typically the .docx (intermediate), second is the .pdf (final).
    """
    if not response_text:
        return []
    try:
        data = json.loads(response_text)
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
    except (json.JSONDecodeError, ValueError):
        pass
    return [s.strip() for s in response_text.split(",") if s.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Trigger document generation (DGP) and poll for result"
    )
    parser.add_argument("--record-id", required=True,
                        help="Source record Id (e.g., Quote Id)")
    parser.add_argument("--template-id", required=True,
                        help="DocumentTemplate Id (0TR prefix)")
    parser.add_argument("--org", required=True, help="SF CLI target org alias")
    parser.add_argument("--title", help="Custom document filename")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output full DGP result as JSON")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Max seconds to poll (default: 120)")
    parser.add_argument("--no-convert", action="store_true",
                        help="Generate .docx only, skip PDF conversion")

    args = parser.parse_args()

    template = resolve_template(args.template_id, args.org)
    mapping_method = template.get("TokenMappingMethodType")

    print(f"Template: {template['Name']} (Method: {mapping_method})")
    print(f"Record: {args.record_id}")
    print(f"Type: {'Generate' if args.no_convert else 'GenerateAndConvert'}")

    dgp_id = create_dgp(
        args.record_id, args.template_id, args.org,
        title=args.title,
        generate_only=args.no_convert,
        mapping_method=mapping_method,
    )
    print(f"DGP Id: {dgp_id}")
    print(f"Polling (timeout: {args.timeout}s)...")

    dgp = poll_dgp(dgp_id, args.org, timeout=args.timeout)

    if not dgp:
        sys.exit(1)

    status = dgp.get("Status")
    if status in ("Completed", "Success"):
        print(f"\nDocument generated successfully.")
        content_ids = extract_content_ids(dgp.get("ResponseText"))
        if content_ids:
            print(f"Output files ({len(content_ids)}):")
            for cid in content_ids:
                if isinstance(cid, dict):
                    cv = cid.get("contentVersionId", "?")
                    cd = cid.get("contentDocumentId", "?")
                    print(f"  ContentVersion: {cv}")
                    print(f"  ContentDocument: {cd}")
                else:
                    print(f"  ContentVersion: {cid}")
        if args.json_output:
            print(json.dumps(dgp, indent=2))
    else:
        print(f"\nGeneration FAILED (Status: {status})")
        response = dgp.get("ResponseText")
        if response:
            print(f"ResponseText: {response}")
        sys.exit(1)


if __name__ == "__main__":
    main()

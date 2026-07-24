"""
Execute an ODT (Extract or Transform) via the OmniStudio REST API.

Uses the public OmniStudio REST endpoint:
  POST /services/data/v67.0/omnistudio/dataraptor/<ODTName>

This endpoint accepts standard OAuth (no Lightning session required),
making it suitable for CLI-based testing, CI validation, and agent
automation. Works for both Extract and Transform ODTs.

Usage (Extract — queries org data):
  python scripts/docgen/docgen_odt_execute.py <odt_name> --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch
  python scripts/docgen/docgen_odt_execute.py RLMQuoteProposalExtract --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch --json

Usage (Transform — reshapes JSON input):
  python scripts/docgen/docgen_odt_execute.py <odt_name> --input extract_output.json --org dev-scratch
  python scripts/docgen/docgen_odt_execute.py RLMQuoteProposalTransform --input /tmp/extract.json --org dev-scratch

Pipeline (Extract → Transform):
  python scripts/docgen/docgen_odt_execute.py MyExtract --record-id 0Q0XXXXXXXXXXXXAAA --org dev-scratch --json > /tmp/e.json
  python scripts/docgen/docgen_odt_execute.py MyTransform --input /tmp/e.json --org dev-scratch

Options:
  --json      Output raw JSON response (for piping to jq or other tools)
  --count     Show only record counts per output array (quick validation)
  --field     Filter output to show only specific output fields
  --input     JSON file to use as request body (for Transform testing)
"""
import argparse
import json
import subprocess
import sys
import tempfile


def execute_odt(odt_name, record_id, org, api_version="v67.0", input_file=None):
    """Execute an ODT (Extract or Transform) via REST API.

    For Extracts: pass record_id (sends {"Id": "0Q0XXXXXXXXXXXXAAA"}).
    For Transforms: pass input_file (sends the file contents as the body).

    Returns the parsed JSON response or None on failure.
    """
    endpoint = f"/services/data/{api_version}/omnistudio/dataraptor/{odt_name}"

    if input_file:
        try:
            with open(input_file) as f:
                body = json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Input file not found: {input_file}", file=sys.stderr)
            return None
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in input file: {e}", file=sys.stderr)
            return None
    else:
        body = {"Id": record_id}

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(body, f)
            tmp_path = f.name

        result = subprocess.run(
            [
                "sf", "api", "request", "rest",
                "--method", "POST",
                "--body", f"@{tmp_path}",
                endpoint,
                "--target-org", org,
            ],
            capture_output=True, text=True,
        )
    finally:
        if tmp_path:
            import os
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    if result.returncode != 0:
        print(f"ERROR: sf api request failed (exit {result.returncode})", file=sys.stderr)
        print(result.stderr or result.stdout, file=sys.stderr)
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse response as JSON", file=sys.stderr)
        print(result.stdout[:500], file=sys.stderr)
        return None


def count_arrays(data):
    """Count entries in each array-like structure in the response."""
    counts = {}
    if isinstance(data, list):
        counts["(root)"] = len(data)
        if data and isinstance(data[0], dict):
            for key, val in data[0].items():
                if isinstance(val, list):
                    lengths = [len(item.get(key, [])) for item in data
                               if isinstance(item, dict) and isinstance(item.get(key), list)]
                    counts[key] = f"{sum(lengths)} total across {len(lengths)} parents"
    elif isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, list):
                counts[key] = len(val)
    return counts


def filter_fields(data, fields):
    """Filter response to show only specified output fields."""
    if isinstance(data, list):
        return [{k: v for k, v in item.items() if k in fields}
                for item in data if isinstance(item, dict)]
    elif isinstance(data, dict):
        return {k: v for k, v in data.items() if k in fields}
    return data


def print_summary(data, odt_name, record_id):
    """Print a human-readable summary of the ODT execution result."""
    print(f"ODT: {odt_name}")
    print(f"Record: {record_id}")
    print(f"Status: OK")

    if isinstance(data, list):
        print(f"Result: {len(data)} entries")
        if data and isinstance(data[0], dict):
            fields = sorted(data[0].keys())
            print(f"Fields ({len(fields)}): {', '.join(fields)}")

            for key in fields:
                val = data[0].get(key)
                if isinstance(val, list) and val:
                    sub_fields = sorted(val[0].keys()) if isinstance(val[0], dict) else []
                    total = sum(len(item.get(key, [])) for item in data
                                if isinstance(item, dict) and isinstance(item.get(key), list))
                    print(f"  {key}: {total} nested entries")
                    if sub_fields:
                        print(f"    Sub-fields: {', '.join(sub_fields)}")

            print(f"\nSample (first entry):")
            sample = data[0]
            for k, v in sorted(sample.items()):
                if isinstance(v, list):
                    print(f"  {k}: [{len(v)} items]")
                elif isinstance(v, str) and len(v) > 80:
                    print(f"  {k}: {v[:77]}...")
                else:
                    print(f"  {k}: {v}")
        elif data:
            print(f"  (non-object entries: {type(data[0]).__name__})")

    elif isinstance(data, dict):
        print(f"Result: single object with {len(data)} keys")
        for k, v in sorted(data.items()):
            if isinstance(v, list):
                print(f"  {k}: [{len(v)} items]")
            else:
                print(f"  {k}: {v}")


def main():
    parser = argparse.ArgumentParser(
        description="Execute an ODT (Extract or Transform) via OmniStudio REST API"
    )
    parser.add_argument("odt_name", help="ODT Name (not Id)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--record-id", help="Record Id to extract (e.g., Quote Id)")
    group.add_argument("--input", dest="input_file",
                       help="JSON file to use as request body (for Transform testing)")
    parser.add_argument("--org", required=True, help="SF CLI target org alias")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output raw JSON response")
    parser.add_argument("--count", action="store_true",
                        help="Show only record counts per array")
    parser.add_argument("--field", action="append", dest="fields",
                        help="Filter output to specific fields (repeatable)")
    parser.add_argument("--api-version", default="v67.0",
                        help="Salesforce API version (default: v67.0)")
    args = parser.parse_args()

    data = execute_odt(args.odt_name, args.record_id, args.org, args.api_version,
                       input_file=args.input_file)
    if data is None:
        sys.exit(1)

    if args.fields:
        data = filter_fields(data, set(args.fields))

    source = args.record_id or args.input_file
    if args.json_output:
        print(json.dumps(data, indent=2))
    elif args.count:
        counts = count_arrays(data)
        print(f"ODT: {args.odt_name}  Source: {source}")
        if not counts:
            print(f"  Result: empty or scalar")
        for key, count in counts.items():
            print(f"  {key}: {count}")
    else:
        print_summary(data, args.odt_name, source)

    sys.exit(0)


if __name__ == "__main__":
    main()

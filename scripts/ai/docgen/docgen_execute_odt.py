"""
Execute an Extract ODT via the OmniStudio REST API and display results.

Uses the public OmniStudio REST endpoint:
  POST /services/data/v67.0/omnistudio/dataraptor/<ODTName>

This endpoint accepts standard OAuth (no Lightning session required),
making it suitable for CLI-based testing, CI validation, and agent
automation.

Usage:
  python scripts/ai/docgen/docgen_execute_odt.py <odt_name> --record-id <id> --org <sf_alias>
  python scripts/ai/docgen/docgen_execute_odt.py RLMQuoteProposalExtract --record-id 0Q0O4000004gZiD --org rlm-base__beta
  python scripts/ai/docgen/docgen_execute_odt.py RLMQuoteProposalExtract --record-id 0Q0O4000004gZiD --org rlm-base__beta --json
  python scripts/ai/docgen/docgen_execute_odt.py RLMQuoteProposalExtract --record-id 0Q0O4000004gZiD --org rlm-base__beta --count

Options:
  --json      Output raw JSON response (for piping to jq or other tools)
  --count     Show only record counts per output array (quick validation)
  --field     Filter output to show only specific output fields
"""
import argparse
import json
import subprocess
import sys
import tempfile


def execute_odt(odt_name, record_id, org, api_version="v67.0"):
    """Execute an Extract ODT via REST API.

    Returns the parsed JSON response or None on failure.
    """
    endpoint = f"/services/data/{api_version}/omnistudio/dataraptor/{odt_name}"
    body = {"Id": record_id}

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
        if data:
            for key, val in data[0].items():
                if isinstance(val, list):
                    lengths = [len(item.get(key, [])) for item in data if isinstance(item.get(key), list)]
                    counts[key] = f"{sum(lengths)} total across {len(lengths)} parents"
    elif isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, list):
                counts[key] = len(val)
    return counts


def filter_fields(data, fields):
    """Filter response to show only specified output fields."""
    if isinstance(data, list):
        return [{k: v for k, v in item.items() if k in fields} for item in data]
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
        if data:
            fields = sorted(data[0].keys())
            print(f"Fields ({len(fields)}): {', '.join(fields)}")

            for key in fields:
                val = data[0].get(key)
                if isinstance(val, list) and val:
                    sub_fields = sorted(val[0].keys()) if isinstance(val[0], dict) else []
                    total = sum(len(item.get(key, [])) for item in data if isinstance(item.get(key), list))
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

            null_fields = [k for k, v in sample.items() if v is None]
            if null_fields:
                print(f"\nNull fields in first entry: {', '.join(null_fields)}")
                null_count = sum(1 for item in data if any(item.get(k) is None for k in null_fields))
                if null_count > 1:
                    print(f"  ({null_count}/{len(data)} entries have null values — possible phantom entries)")

    elif isinstance(data, dict):
        print(f"Result: single object with {len(data)} keys")
        for k, v in sorted(data.items()):
            if isinstance(v, list):
                print(f"  {k}: [{len(v)} items]")
            else:
                print(f"  {k}: {v}")


def main():
    parser = argparse.ArgumentParser(
        description="Execute an Extract ODT via OmniStudio REST API"
    )
    parser.add_argument("odt_name", help="ODT Name (not Id)")
    parser.add_argument("--record-id", required=True, help="Record Id to extract (e.g., Quote Id)")
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

    data = execute_odt(args.odt_name, args.record_id, args.org, args.api_version)
    if data is None:
        sys.exit(1)

    if args.fields:
        data = filter_fields(data, set(args.fields))

    if args.json_output:
        print(json.dumps(data, indent=2))
    elif args.count:
        counts = count_arrays(data)
        print(f"ODT: {args.odt_name}  Record: {args.record_id}")
        if not counts:
            print(f"  Result: empty or scalar")
        for key, count in counts.items():
            print(f"  {key}: {count}")
    else:
        print_summary(data, args.odt_name, args.record_id)

    sys.exit(0)


if __name__ == "__main__":
    main()

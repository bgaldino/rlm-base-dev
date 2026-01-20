#!/usr/bin/env python3
"""
Validate Postman Collection Structure
Tests the v260 endpoint implementation without calling live APIs
"""

import json
import sys
from pathlib import Path
from collections import defaultdict


def validate_collection(collection_path):
    """Validate collection structure and v260 endpoints"""

    print("=" * 80)
    print(f"Validating: {collection_path.name}")
    print("=" * 80)
    print()

    with open(collection_path, 'r') as f:
        collection = json.load(f)

    issues = []
    warnings = []
    stats = {
        'total_folders': 0,
        'total_endpoints': 0,
        'v260_folders': 0,
        'v260_endpoints': 0,
        'endpoints_with_hardcoded_version': [],
        'endpoints_missing_dynamic_version': [],
        'endpoints_with_body': 0,
        'endpoints_without_body': 0
    }

    # Check collection metadata
    if 'info' not in collection:
        issues.append("Missing 'info' section in collection")
    else:
        print(f"Collection: {collection['info'].get('name', 'Unknown')}")
        print(f"Description: {collection['info'].get('description', 'N/A')[:100]}...")
        print()

    # Validate folders and endpoints
    print("Analyzing folders and endpoints...")
    print()

    for folder in collection.get('item', []):
        folder_name = folder.get('name', 'Unnamed Folder')
        stats['total_folders'] += 1

        if '(v260)' in folder_name:
            stats['v260_folders'] += 1

        folder_endpoints = folder.get('item', [])
        folder_endpoint_count = len(folder_endpoints)
        stats['total_endpoints'] += folder_endpoint_count

        if '(v260)' in folder_name:
            stats['v260_endpoints'] += folder_endpoint_count
            print(f"✓ {folder_name}: {folder_endpoint_count} endpoints")

        # Validate each endpoint
        for endpoint in folder_endpoints:
            endpoint_name = endpoint.get('name', 'Unnamed Endpoint')
            request = endpoint.get('request', {})

            # Check for hardcoded versions
            url_data = request.get('url', {})
            if isinstance(url_data, dict):
                raw_url = url_data.get('raw', '')
            elif isinstance(url_data, str):
                raw_url = url_data
            else:
                raw_url = ''

            # Check for v62.0, v63.0, v64.0, v65.0 (not v66.0 which might be intentional)
            for old_version in ['v62.0', 'v63.0', 'v64.0', 'v65.0']:
                if old_version in raw_url:
                    stats['endpoints_with_hardcoded_version'].append(
                        f"{folder_name} > {endpoint_name} (contains {old_version})"
                    )

            # Check for dynamic version variable
            # Exception: "Get Latest Release Version" endpoint is used to SET the version variable
            if '{{version}}' not in raw_url and 'v{{version}}' not in raw_url:
                if '/services/data/' in raw_url and 'Get Latest Release Version' not in endpoint_name:
                    stats['endpoints_missing_dynamic_version'].append(
                        f"{folder_name} > {endpoint_name}"
                    )

            # Check request body for POST/PATCH/PUT
            method = request.get('method', 'GET')
            if method in ['POST', 'PATCH', 'PUT']:
                if 'body' in request and request['body'].get('raw'):
                    stats['endpoints_with_body'] += 1
                else:
                    warnings.append(
                        f"{folder_name} > {endpoint_name}: {method} request without body"
                    )
                    stats['endpoints_without_body'] += 1

    print()
    print("=" * 80)
    print("Validation Results")
    print("=" * 80)
    print()

    # Print statistics
    print("📊 Collection Statistics:")
    print(f"   Total Folders: {stats['total_folders']}")
    print(f"   Total Endpoints: {stats['total_endpoints']}")
    print(f"   v260 Folders: {stats['v260_folders']}")
    print(f"   v260 Endpoints: {stats['v260_endpoints']}")
    print()

    # Check for issues
    if stats['endpoints_with_hardcoded_version']:
        issues.append(
            f"Found {len(stats['endpoints_with_hardcoded_version'])} endpoints with hardcoded versions"
        )
        print("❌ Hardcoded Version Issues:")
        for ep in stats['endpoints_with_hardcoded_version'][:5]:
            print(f"   • {ep}")
        if len(stats['endpoints_with_hardcoded_version']) > 5:
            print(f"   ... and {len(stats['endpoints_with_hardcoded_version']) - 5} more")
        print()

    if stats['endpoints_missing_dynamic_version']:
        issues.append(
            f"Found {len(stats['endpoints_missing_dynamic_version'])} endpoints without dynamic version"
        )
        print("⚠️  Missing Dynamic Version:")
        for ep in stats['endpoints_missing_dynamic_version'][:5]:
            print(f"   • {ep}")
        if len(stats['endpoints_missing_dynamic_version']) > 5:
            print(f"   ... and {len(stats['endpoints_missing_dynamic_version']) - 5} more")
        print()

    # Print warnings
    if warnings:
        print(f"⚠️  Warnings ({len(warnings)}):")
        for warning in warnings[:5]:
            print(f"   • {warning}")
        if len(warnings) > 5:
            print(f"   ... and {len(warnings) - 5} more")
        print()

    # Final verdict
    print("=" * 80)
    if issues:
        print(f"❌ VALIDATION FAILED - {len(issues)} issue(s) found")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        print("✅ VALIDATION PASSED - Collection structure is correct!")
        print()
        print("Next Steps:")
        print("   1. Import collection into Postman")
        print("   2. Configure environment variables (_endpoint, clientId, clientSecret)")
        print("   3. Test authentication flow")
        print("   4. Test v260 endpoints with live API")
        print("   5. Review TESTING_GUIDE.md for detailed test procedures")
        return True


def compare_collections():
    """Compare RLM and RCA collections"""
    script_dir = Path(__file__).parent

    rlm_path = script_dir / "RLM.postman_collection.json"
    rca_path = script_dir / "RCA APIs - Winter'25 (258) Latest.postman_collection.json"

    print()
    print("=" * 80)
    print("Collection Comparison Summary")
    print("=" * 80)
    print()

    if rlm_path.exists():
        with open(rlm_path, 'r') as f:
            rlm = json.load(f)
            rlm_count = sum(len(folder.get('item', [])) for folder in rlm.get('item', []))
            print(f"RLM Collection: {rlm_count} endpoints")

    if rca_path.exists():
        with open(rca_path, 'r') as f:
            rca = json.load(f)
            rca_count = sum(len(folder.get('item', [])) for folder in rca.get('item', []))
            rca_v260 = sum(
                len(folder.get('item', []))
                for folder in rca.get('item', [])
                if '(v260)' in folder.get('name', '')
            )
            print(f"RCA Collection: {rca_count} endpoints ({rca_v260} are v260)")

    print()
    print(f"Combined Total: {rlm_count + rca_count} endpoints")
    print()


def main():
    script_dir = Path(__file__).parent

    print()
    print("🔍 Postman Collection Validator")
    print()

    # Validate RCA collection (has v260 endpoints)
    rca_collection = script_dir / "RCA APIs - Winter'25 (258) Latest.postman_collection.json"

    if not rca_collection.exists():
        print(f"❌ Collection not found: {rca_collection}")
        return 1

    rca_valid = validate_collection(rca_collection)
    print()

    # Validate RLM collection
    print("=" * 80)
    print()
    rlm_collection = script_dir / "RLM.postman_collection.json"

    if rlm_collection.exists():
        rlm_valid = validate_collection(rlm_collection)
    else:
        print(f"⚠️  RLM collection not found: {rlm_collection}")
        rlm_valid = True  # Don't fail if optional collection missing

    # Summary
    compare_collections()

    print("=" * 80)
    print()

    if rca_valid and rlm_valid:
        print("✅ ALL COLLECTIONS VALIDATED SUCCESSFULLY")
        print()
        print("📋 See TESTING_GUIDE.md for next steps")
        return 0
    else:
        print("❌ VALIDATION FAILED - Please fix issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

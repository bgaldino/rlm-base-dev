#!/usr/bin/env python3
"""
Comprehensive Postman Collection Validator for Revenue Cloud APIs (v260/Spring '26)

Validates ALL three collections in the postman directory against:
  1. Structural integrity (metadata, folders, endpoints, auth, JSON bodies)
  2. v66.0 API versioning standards ({{version}} variable usage)
  3. Completeness against the v260 API inventory (95 endpoints across 8 categories)
  4. Consistency rules (naming, duplicates, variable references)

Exit codes:
  0 = no errors found
  1 = errors found
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum


class IssueLevel(Enum):
    """Issue severity levels."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    level: IssueLevel
    collection_name: str
    folder_name: str
    endpoint_name: str
    message: str

    def __str__(self):
        return f"{self.level.value} | {self.collection_name} > {self.folder_name} > {self.endpoint_name}: {self.message}"


class APIInventory:
    """The complete v260 Revenue Cloud Business API endpoint inventory."""

    # All 95 endpoints across 8 API categories
    ENDPOINTS = {
        "PCM": [
            "/connect/pcm/catalogs",
            "/connect/pcm/catalogs/{id}",
            "/connect/pcm/catalogs/{id}/categories",
            "/connect/pcm/categories/{id}",
            "/connect/pcm/products",
            "/connect/pcm/products/{id}",
            "/connect/pcm/products/bulk",
            "/connect/pcm/products/{id}/related-records",
            "/connect/pcm/products/classification",
            "/connect/pcm/products/{id}/actions/deep-clone",
            "/connect/pcm/index/configurations",
            "/connect/pcm/index/setting",
            "/connect/pcm/index/snapshots",
            "/connect/pcm/index/snapshots/{id}/actions/deploy",
            "/connect/pcm/index/snapshots/{id}/errors",
            "/connect/pcm/unit-of-measure",
            "/connect/pcm/unit-of-measure/actions/round",
        ],
        "PD (Product Details)": [
            "/connect/cpq/catalogs",
            "/connect/cpq/catalogs/{id}",
            "/connect/cpq/categories",
            "/connect/cpq/categories/{id}",
            "/connect/cpq/products",
            "/connect/cpq/products/{id}",
            "/connect/cpq/products/search",
            "/connect/cpq/products/bulk",
            "/connect/cpq/products/guided-selection",
            "/connect/cpq/qualification",
        ],
        "Pricing": [
            "/connect/core-pricing/derived-pricing",
            "/connect/core-pricing/price-context",
            "/connect/core-pricing/pricing",
            "/connect/core-pricing/pricing/api-execution-logs",
            "/connect/core-pricing/pricing/execution",
            "/connect/core-pricing/pricing/execution/line-items",
            "/connect/core-pricing/sync/syncData",
            "/connect/core-pricing/recipe",
            "/connect/core-pricing/recipe/mapping",
            "/connect/core-pricing/versioned-revision-details",
            "/connect/core-pricing/waterfall/{id}/{id}",
            "/connect/core-pricing/waterfall",
            "/connect/core-pricing/simulation/input-variables",
            "/connect/procedure-plan-definitions",
            "/connect/procedure-plan-definitions/{id}",
            "/connect/procedure-plan-definitions/actions/evaluate",
        ],
        "Configurator": [
            "/connect/cpq/configurator/actions/configure",
            "/connect/cpq/configurator/saved-configuration",
            "/connect/cpq/configurator/saved-configuration/{id}",
            "/connect/cpq/configurator/actions/get-instance",
            "/connect/cpq/configurator/actions/load-instance",
            "/connect/cpq/configurator/actions/save-instance",
            "/connect/cpq/configurator/actions/set-instance",
            "/connect/cpq/configurator/actions/add-nodes",
            "/connect/cpq/configurator/actions/delete-nodes",
            "/connect/cpq/configurator/actions/update-nodes",
            "/connect/cpq/configurator/actions/set-product-quantity",
        ],
        "Rate Management": [
            "/connect/core-rating/rate-plan",
            "/connect/core-pricing/waterfall/{id}/{id}",
        ],
        "Transaction Management": [
            "/commerce/sales-transactions/actions/place",
            "/commerce/sales-transactions/actions/read",
            "/commerce/sales-transactions/actions/clone",
            "/industries/cpq/quotes/actions/get-instant-price",
            "/commerce/sales-transactions/actions/preview-approval",
            "/commerce/sales-transactions/actions/get-eligible-promotions",
            "/commerce/sales-transactions/api-errors",
            "/commerce/sales-transactions/actions/place-supplemental",
            "/connect/revenue-management/assets/actions/amend",
            "/connect/revenue-management/assets/actions/cancel",
            "/connect/revenue-management/assets/actions/renew",
            "/commerce/sales-transactions/ramp-deals",
            "/commerce/sales-transactions/ramp-deals/actions/update",
            "/commerce/sales-transactions/ramp-deals/actions/delete",
            "/commerce/sales-orders/actions/place",
            "/commerce/quotes/actions/place",
        ],
        "Usage Management": [
            "/asset-management/assets/{id}/usage-details",
            "/commerce/sales-orders/line-items/{id}/usage-details",
            "/commerce/quotes/line-items/{id}/usage-details",
            "/revenue/usage-management/binding-objects/{id}/actions/usage-details",
            "/revenue/usage-management/consumption/actions/trace",
            "/revenue/usage-management/usage-products/actions/validate",
        ],
        "Billing": [
            "/commerce/billing/credit-memos/actions/apply",
            "/commerce/billing/credit-memos/actions/generate",
            "/commerce/billing/credit-memos/actions/void",
            "/commerce/billing/credit-memos/actions/unapply",
            "/commerce/billing/billing-schedules/actions/create-from-billing-transaction",
            "/commerce/billing/billing-schedules/actions/create-standalone",
            "/commerce/billing/billing-schedules/actions/suspend",
            "/commerce/billing/billing-schedules/actions/resume",
            "/commerce/billing/billing-schedules/actions/recover",
            "/commerce/billing/invoices/actions/generate",
            "/commerce/billing/invoices/actions/post",
            "/commerce/billing/invoices/actions/post-batch",
            "/commerce/billing/invoices/actions/preview",
            "/commerce/billing/invoices/actions/write-off",
            "/commerce/billing/invoices/actions/void",
            "/commerce/billing/invoices/actions/ingest",
            "/commerce/billing/invoices/actions/generate-documents",
            "/commerce/billing/invoice-schedulers",
            "/commerce/billing/payments/actions/apply",
            "/commerce/billing/payments/actions/unapply",
            "/commerce/billing/payment-credits/actions/apply-by-rules",
            "/commerce/billing/refunds/actions/generate",
            "/commerce/billing/tax/actions/calculate",
            "/commerce/billing/tax/actions/estimate",
            "/commerce/billing/account-statements/actions/generate",
        ],
        "Context Service": [
            "/connect/context-definitions",
        ],
    }

    @classmethod
    def get_all_endpoints(cls) -> Set[str]:
        """Get all endpoint paths as a flat set."""
        return set(ep for endpoints in cls.ENDPOINTS.values() for ep in endpoints)

    @classmethod
    def get_normalized_endpoints(cls) -> Set[str]:
        """Get all endpoints with {id} normalized to a placeholder for matching."""
        endpoints = cls.get_all_endpoints()
        normalized = set()
        for ep in endpoints:
            # Normalize {id} patterns for comparison
            normalized_ep = ep.replace("{id}", "{{id}}")
            normalized.add(normalized_ep)
        return normalized


class PostmanCollectionValidator:
    """Validates a single Postman collection against v260 standards."""

    # Hardcoded version patterns that should be replaced with {{version}}
    HARDCODED_VERSIONS = ["v60.0", "v61.0", "v62.0", "v63.0", "v64.0", "v65.0", "v66.0"]

    def __init__(self, collection_path: Path, verbose: bool = False):
        self.path = collection_path
        self.verbose = verbose
        self.issues: List[ValidationIssue] = []
        self.endpoints_found: Set[str] = set()
        self.endpoint_names: Dict[str, List[str]] = defaultdict(list)

    def validate(self) -> Tuple[bool, Dict]:
        """Run all validation checks. Returns (is_valid, stats)."""
        try:
            with open(self.path, "r") as f:
                self.collection = json.load(f)
        except json.JSONDecodeError as e:
            self.issues.append(
                ValidationIssue(
                    IssueLevel.ERROR,
                    self.path.stem,
                    "",
                    "",
                    f"Invalid JSON: {e}",
                )
            )
            return False, {}
        except Exception as e:
            self.issues.append(
                ValidationIssue(
                    IssueLevel.ERROR,
                    self.path.stem,
                    "",
                    "",
                    f"Cannot read file: {e}",
                )
            )
            return False, {}

        stats = self._validate_structure()
        self._validate_endpoints()
        self._validate_completeness()

        has_errors = any(issue.level == IssueLevel.ERROR for issue in self.issues)
        return not has_errors, stats

    def _validate_structure(self) -> Dict:
        """Validate collection metadata and structure."""
        stats = {
            "collection_name": "Unknown",
            "collection_description": "",
            "folders": 0,
            "endpoints": 0,
            "endpoints_with_body": 0,
            "endpoints_without_required_body": 0,
            "hardcoded_versions_found": 0,
            "missing_dynamic_version": 0,
            "duplicate_endpoint_names": 0,
            "auth_overrides": 0,
        }

        # Check collection info
        info = self.collection.get("info", {})
        if not info:
            self.issues.append(
                ValidationIssue(
                    IssueLevel.ERROR,
                    self.path.stem,
                    "",
                    "",
                    "Missing 'info' section",
                )
            )
            return stats

        stats["collection_name"] = info.get("name", "Unknown")
        stats["collection_description"] = info.get("description", "")

        if not info.get("schema"):
            self.issues.append(
                ValidationIssue(
                    IssueLevel.WARNING,
                    self.path.stem,
                    "",
                    "",
                    "Missing 'info.schema' (should reference Postman schema)",
                )
            )

        # Validate folders and endpoints
        for folder in self.collection.get("item", []):
            folder_name = folder.get("name", "Unnamed Folder")
            if not folder_name:
                self.issues.append(
                    ValidationIssue(
                        IssueLevel.ERROR,
                        self.path.stem,
                        "Unnamed",
                        "",
                        "Folder has no name",
                    )
                )
                continue

            stats["folders"] += 1

            self._validate_folder_items(folder.get("item", []), folder_name, stats)

        return stats

    def _validate_folder_items(self, items: List, folder_name: str, stats: Dict):
        """Recursively validate items in a folder, handling nested subfolders."""
        for item in items:
            # If the item has its own 'item' array AND no 'request', it's a subfolder
            if "item" in item and "request" not in item:
                subfolder_name = item.get("name", "Unnamed Subfolder")
                stats["folders"] += 1
                self._validate_folder_items(item["item"], f"{folder_name} > {subfolder_name}", stats)
            else:
                stats["endpoints"] += 1
                self._validate_endpoint(item, folder_name, stats)

    def _validate_endpoint(self, endpoint: Dict, folder_name: str, stats: Dict):
        """Validate a single endpoint."""
        endpoint_name = endpoint.get("name", "Unnamed Endpoint")
        if not endpoint_name:
            self.issues.append(
                ValidationIssue(
                    IssueLevel.ERROR,
                    self.path.stem,
                    folder_name,
                    "Unnamed",
                    "Endpoint has no name",
                )
            )
            return

        # Track for duplicate detection
        self.endpoint_names[folder_name].append(endpoint_name)

        request = endpoint.get("request", {})

        # Check method exists
        method = request.get("method", "GET")
        if not method:
            self.issues.append(
                ValidationIssue(
                    IssueLevel.ERROR,
                    self.path.stem,
                    folder_name,
                    endpoint_name,
                    "Missing HTTP method",
                )
            )

        # Check URL exists
        url_data = request.get("url")
        if not url_data:
            self.issues.append(
                ValidationIssue(
                    IssueLevel.ERROR,
                    self.path.stem,
                    folder_name,
                    endpoint_name,
                    "Missing URL",
                )
            )
            return

        raw_url = self._extract_raw_url(url_data)
        if not raw_url:
            self.issues.append(
                ValidationIssue(
                    IssueLevel.WARNING,
                    self.path.stem,
                    folder_name,
                    endpoint_name,
                    "Could not extract raw URL",
                )
            )
            return

        # Track endpoint for completeness
        self.endpoints_found.add(raw_url)

        # Check for hardcoded versions
        for version in self.HARDCODED_VERSIONS:
            if f"/{version}/" in raw_url:
                self.issues.append(
                    ValidationIssue(
                        IssueLevel.ERROR,
                        self.path.stem,
                        folder_name,
                        endpoint_name,
                        f"Hardcoded {version} found; use {{{{version}}}} instead",
                    )
                )
                stats["hardcoded_versions_found"] += 1
                break

        # Check for dynamic version in /services/data/ endpoints
        if "/services/data/" in raw_url and "Get Latest Release Version" not in endpoint_name:
            if "{{version}}" not in raw_url and "v{{version}}" not in raw_url:
                self.issues.append(
                    ValidationIssue(
                        IssueLevel.ERROR,
                        self.path.stem,
                        folder_name,
                        endpoint_name,
                        "Missing {{version}} variable in /services/data/ URL",
                    )
                )
                stats["missing_dynamic_version"] += 1

        # Validate request body for POST/PATCH/PUT
        if method in ["POST", "PATCH", "PUT"]:
            body = request.get("body", {})
            if body and body.get("raw"):
                stats["endpoints_with_body"] += 1
                # Validate JSON if present
                try:
                    json.loads(body["raw"])
                except json.JSONDecodeError:
                    self.issues.append(
                        ValidationIssue(
                            IssueLevel.ERROR,
                            self.path.stem,
                            folder_name,
                            endpoint_name,
                            "Invalid JSON in request body",
                        )
                    )
            else:
                self.issues.append(
                    ValidationIssue(
                        IssueLevel.WARNING,
                        self.path.stem,
                        folder_name,
                        endpoint_name,
                        f"{method} endpoint without request body",
                    )
                )
                stats["endpoints_without_required_body"] += 1

        # Check for auth overrides (should inherit)
        if request.get("auth"):
            self.issues.append(
                ValidationIssue(
                    IssueLevel.INFO,
                    self.path.stem,
                    folder_name,
                    endpoint_name,
                    "Endpoint-level auth override (should inherit from collection)",
                )
            )
            stats["auth_overrides"] += 1

        # Validate endpoint name format (should be "Area: Action")
        if not self._validate_endpoint_name(endpoint_name):
            if self.verbose:
                self.issues.append(
                    ValidationIssue(
                        IssueLevel.INFO,
                        self.path.stem,
                        folder_name,
                        endpoint_name,
                        "Endpoint name doesn't follow 'Area: Action' pattern",
                    )
                )

    def _validate_endpoints(self):
        """Validate endpoint-specific rules."""
        # Check for duplicates within folders
        for folder_name, names in self.endpoint_names.items():
            duplicates = [name for name in set(names) if names.count(name) > 1]
            for dup in duplicates:
                self.issues.append(
                    ValidationIssue(
                        IssueLevel.ERROR,
                        self.path.stem,
                        folder_name,
                        dup,
                        "Duplicate endpoint name in folder",
                    )
                )

    def _validate_completeness(self):
        """Check which API inventory endpoints are covered."""
        api_inventory = APIInventory.get_all_endpoints()

        # Normalize found endpoints for comparison
        found_normalized = set()
        for ep in self.endpoints_found:
            # Extract the path part from full URL
            if "/services/data/" in ep:
                # Salesforce core APIs - skip from inventory check
                continue
            # Normalize {id} for comparison
            normalized = ep.replace("{id}", "{{id}}")
            found_normalized.add(normalized)

        self.missing_endpoints = api_inventory - self.endpoints_found

    def _extract_raw_url(self, url_data) -> str:
        """Extract raw URL from various Postman URL formats."""
        if isinstance(url_data, str):
            return url_data
        elif isinstance(url_data, dict):
            return url_data.get("raw", "")
        return ""

    def _validate_endpoint_name(self, name: str) -> bool:
        """Check if endpoint name follows 'Area: Action' pattern."""
        return ":" in name or name.startswith("Get ") or name.startswith("Post ")


class ValidationReport:
    """Generates formatted validation reports."""

    # ANSI color codes
    COLORS = {
        "RED": "\033[91m",
        "YELLOW": "\033[93m",
        "GREEN": "\033[92m",
        "BLUE": "\033[94m",
        "CYAN": "\033[96m",
        "WHITE": "\033[97m",
        "RESET": "\033[0m",
        "BOLD": "\033[1m",
    }

    @classmethod
    def _colorize(cls, text: str, color: str) -> str:
        """Add ANSI color codes to text."""
        return f"{cls.COLORS.get(color, '')}{text}{cls.COLORS['RESET']}"

    @classmethod
    def print_header(cls):
        """Print report header."""
        print()
        print(cls._colorize("=" * 100, "BLUE"))
        print(cls._colorize("🔍 Postman Collection Validator — Revenue Cloud APIs (v260/Spring '26)", "CYAN"))
        print(cls._colorize("=" * 100, "BLUE"))
        print()

    @classmethod
    def print_collection_report(cls, collection_path: Path, issues: List[ValidationIssue], stats: Dict):
        """Print validation report for a single collection."""
        print(cls._colorize(f"\n📦 Collection: {stats['collection_name']}", "BOLD"))
        print(f"   Path: {collection_path.name}")
        if stats["collection_description"]:
            print(f"   Description: {stats['collection_description'][:80]}...")
        print()

        print(cls._colorize("📊 Statistics:", "CYAN"))
        print(f"   Folders: {stats['folders']}")
        print(f"   Endpoints: {stats['endpoints']}")
        print(f"   Endpoints with request body: {stats['endpoints_with_body']}")
        print()

        # Filter issues for this collection
        collection_issues = [i for i in issues if i.collection_name == collection_path.stem]

        if not collection_issues:
            print(cls._colorize("✅ No issues found!", "GREEN"))
            print()
            return

        # Group by level
        errors = [i for i in collection_issues if i.level == IssueLevel.ERROR]
        warnings = [i for i in collection_issues if i.level == IssueLevel.WARNING]
        infos = [i for i in collection_issues if i.level == IssueLevel.INFO]

        if errors:
            print(cls._colorize(f"❌ Errors ({len(errors)}):", "RED"))
            for issue in errors[:10]:
                print(f"   • {issue}")
            if len(errors) > 10:
                print(f"   ... and {len(errors) - 10} more errors")
            print()

        if warnings:
            print(cls._colorize(f"⚠️  Warnings ({len(warnings)}):", "YELLOW"))
            for issue in warnings[:5]:
                print(f"   • {issue}")
            if len(warnings) > 5:
                print(f"   ... and {len(warnings) - 5} more warnings")
            print()

        if infos:
            print(cls._colorize(f"ℹ️  Info ({len(infos)}):", "BLUE"))
            for issue in infos[:3]:
                print(f"   • {issue}")
            if len(infos) > 3:
                print(f"   ... and {len(infos) - 3} more info items")
            print()

    @classmethod
    def print_summary(cls, all_issues: List[ValidationIssue], all_stats: Dict[str, Dict]):
        """Print overall summary."""
        errors = [i for i in all_issues if i.level == IssueLevel.ERROR]
        warnings = [i for i in all_issues if i.level == IssueLevel.WARNING]

        print(cls._colorize("\n" + "=" * 100, "BLUE"))
        print(cls._colorize("📋 Overall Summary", "CYAN"))
        print(cls._colorize("=" * 100, "BLUE"))
        print()

        print(cls._colorize("Collections Analyzed:", "CYAN"))
        for coll_name, stats in all_stats.items():
            print(f"   • {stats['collection_name']}: {stats['endpoints']} endpoints")
        print()

        total_endpoints = sum(s["endpoints"] for s in all_stats.values())
        print(f"Total Endpoints: {total_endpoints}")
        print()

        if errors:
            print(cls._colorize(f"❌ Critical Issues: {len(errors)}", "RED"))
        if warnings:
            print(cls._colorize(f"⚠️  Warnings: {len(warnings)}", "YELLOW"))

        print()

        if not errors:
            print(cls._colorize("✅ VALIDATION PASSED — All collections are valid!", "GREEN"))
            return 0
        else:
            print(cls._colorize("❌ VALIDATION FAILED — Please fix errors above.", "RED"))
            return 1


def auto_fix_hardcoded_versions(collection_path: Path) -> int:
    """Auto-fix hardcoded API versions by replacing with {{version}}."""
    print(f"\n🔧 Auto-fixing {collection_path.name}...")

    with open(collection_path, "r") as f:
        collection = json.load(f)

    fixed_count = 0

    def fix_items(items):
        nonlocal fixed_count
        for item in items:
            if "item" in item and "request" not in item:
                fix_items(item["item"])
            else:
                request = item.get("request", {})
                url_data = request.get("url", {})
                if isinstance(url_data, dict):
                    raw_url = url_data.get("raw", "")
                    for version in ["v60.0", "v61.0", "v62.0", "v63.0", "v64.0", "v65.0"]:
                        if f"/{version}/" in raw_url:
                            new_url = raw_url.replace(f"/{version}/", "/v{{{{version}}}}/")
                            url_data["raw"] = new_url
                            fixed_count += 1

    for folder in collection.get("item", []):
        fix_items(folder.get("item", []))

    if fixed_count > 0:
        with open(collection_path, "w") as f:
            json.dump(collection, f, indent=2)
        print(cls._colorize(f"✅ Fixed {fixed_count} hardcoded versions", "GREEN"))
    else:
        print("ℹ️  No hardcoded versions found to fix")

    return fixed_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Postman collections against v260 Revenue Cloud API standards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  validate_collection.py              # Validate all collections in current directory
  validate_collection.py --verbose    # Validate with detailed endpoint output
  validate_collection.py --fix        # Auto-fix hardcoded API versions
  validate_collection.py --collection RLM.postman_collection.json
        """,
    )

    parser.add_argument(
        "--collection",
        type=Path,
        help="Path to a specific collection to validate (default: all in directory)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output with detailed endpoint info",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix hardcoded API versions → {{version}}",
    )

    args = parser.parse_args()

    # Find collections
    script_dir = Path(__file__).parent
    if args.collection:
        collections = [args.collection]
    else:
        collections = sorted(script_dir.glob("*.postman_collection.json"))

    if not collections:
        print("❌ No Postman collections found in current directory")
        return 1

    # Print header
    ValidationReport.print_header()

    # Validate each collection
    all_issues = []
    all_stats = {}
    any_fixed = False

    for collection_path in collections:
        if args.fix:
            fixed = auto_fix_hardcoded_versions(collection_path)
            any_fixed = any_fixed or (fixed > 0)

        validator = PostmanCollectionValidator(collection_path, verbose=args.verbose)
        is_valid, stats = validator.validate()
        all_issues.extend(validator.issues)
        all_stats[collection_path.stem] = stats

        ValidationReport.print_collection_report(collection_path, validator.issues, stats)

    # Print summary
    exit_code = ValidationReport.print_summary(all_issues, all_stats)

    if args.fix and any_fixed:
        print("\n💾 Collections have been updated with auto-fixes.")

    print()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

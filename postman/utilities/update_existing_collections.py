#!/usr/bin/env python3
"""
Update Postman collections for Revenue Cloud v260 (Spring '26, API v66.0).

This script:
1. Updates RLM collection with new v260 endpoints
2. Updates RCA collection with v260 validations and renames
3. Writes updated versions back to the same filenames
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime

# ============================================================================
# ENDPOINT TEMPLATES
# ============================================================================

def create_endpoint(
    name: str,
    method: str,
    path: str,
    body: Dict[str, Any] | None = None,
    description: str = "",
) -> Dict[str, Any]:
    """Create a Postman endpoint template."""

    # Convert path to URL parts
    path_parts = [p for p in path.split('/') if p]

    endpoint = {
        "name": name,
        "event": [
            {
                "listen": "test",
                "script": {
                    "exec": [""],
                    "type": "text/javascript"
                }
            }
        ],
        "request": {
            "method": method,
            "header": [],
            "url": {
                "raw": f"{{{{_endpoint}}}}/services/data/v{{{{version}}}}/{path}",
                "host": ["{{_endpoint}}"],
                "path": ["services", "data", "v{{version}}"] + path_parts
            }
        },
        "response": []
    }

    if body:
        endpoint["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(body, indent=4),
            "options": {
                "raw": {
                    "language": "json"
                }
            }
        }

    if description:
        endpoint["request"]["description"] = description

    return endpoint


# ============================================================================
# RLM COLLECTION UPDATES
# ============================================================================

def update_rlm_collection(filepath: str) -> Dict[str, Any]:
    """Update the RLM collection with v260 endpoints."""

    with open(filepath, 'r') as f:
        collection = json.load(f)

    changes = {
        "description_updated": False,
        "transaction_mgmt_added": 0,
        "pcm_endpoints_added": 0,
        "pd_endpoints_added": 0,
        "pricing_endpoints_added": 0,
    }

    # Update collection info description
    if "Spring '26" not in collection["info"]["description"]:
        collection["info"]["description"] = (
            "Revenue Lifecycle Management APIs - Spring '26 (v66.0)\n\n"
            "Foundational collection focused on core CPQ workflows and Revenue Cloud configuration.\n\n"
            "[Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rlm_get_started.htm)"
        )
        changes["description_updated"] = True

    # Add description field to info if not present
    if "description" not in collection["info"]:
        collection["info"]["description"] = (
            "Foundational RLM collection focused on core CPQ workflows including quote management, "
            "order capture, product catalog configuration, and revenue recognition."
        )

    # Find and update folders
    for item in collection["item"]:
        if item["name"] == "Quote and Order Capture":
            changes["transaction_mgmt_added"] = add_transaction_mgmt_endpoints(item)
        elif item["name"] == "Product Catalog Management":
            changes["pcm_endpoints_added"] = add_pcm_endpoints(item)
        elif item["name"] == "Product Discovery":
            changes["pd_endpoints_added"] = add_pd_endpoints(item)
        elif item["name"] == "Salesforce Pricing":
            changes["pricing_endpoints_added"] = add_pricing_endpoints(item)

    return collection, changes


def add_transaction_mgmt_endpoints(folder: Dict[str, Any]) -> int:
    """Add transaction management endpoints to Quote and Order Capture folder."""

    # Access the nested "Quotes & Orders" folder
    if "item" in folder and len(folder["item"]) > 0:
        quotes_orders = folder["item"][0]
        if "item" not in quotes_orders:
            quotes_orders["item"] = []

        existing_names = {e["name"] for e in quotes_orders["item"]}
        added_count = 0

        new_endpoints = [
            create_endpoint(
                "Place Sales Transaction",
                "POST",
                "commerce/sales-transactions/actions/place",
                {"salesTransactionId": "{{currentQuoteId}}"},
                "Place (finalize) a sales transaction (Quote). API v66.0+"
            ),
            create_endpoint(
                "Read Sales Transaction",
                "POST",
                "commerce/sales-transactions/actions/read",
                {"salesTransactionId": "{{currentQuoteId}}"},
                "Read details of a sales transaction. API v66.0+"
            ),
            create_endpoint(
                "Clone Sales Transaction",
                "POST",
                "commerce/sales-transactions/actions/clone",
                {
                    "salesTransactionId": "{{currentQuoteId}}",
                    "targetTransactionType": "Quote"
                },
                "Clone an existing sales transaction. API v66.0+"
            ),
            create_endpoint(
                "Get Eligible Promotions",
                "POST",
                "commerce/sales-transactions/actions/get-eligible-promotions",
                {"salesTransactionId": "{{currentQuoteId}}"},
                "Retrieve promotions eligible for a sales transaction. NEW in v66.0"
            ),
        ]

        for endpoint in new_endpoints:
            if endpoint["name"] not in existing_names:
                quotes_orders["item"].append(endpoint)
                added_count += 1

        return added_count

    return 0


def add_pcm_endpoints(folder: Dict[str, Any]) -> int:
    """Add PCM endpoints to Product Catalog Management folder."""

    if "item" not in folder:
        folder["item"] = []

    existing_names = {e["name"] for e in folder["item"]}
    added_count = 0

    new_endpoints = [
        create_endpoint(
            "PCM: Bulk Product Details",
            "POST",
            "connect/pcm/products/bulk",
            {
                "ids": ["{{productId1}}", "{{productId2}}"],
                "pageSize": 100,
                "offset": 0
            },
            "Retrieve bulk product details. API v66.0+"
        ),
        create_endpoint(
            "PCM: Deep Clone",
            "POST",
            "connect/pcm/products/{productId}/actions/deep-clone",
            {
                "targetProductName": "Cloned Product",
                "includePricing": True,
                "includeAttributes": True
            },
            "Deep clone a product with all configurations. API v66.0+"
        ),
        create_endpoint(
            "PCM: Product Classification",
            "POST",
            "connect/pcm/products/classification",
            {
                "productId": "{{productId}}",
                "classificationId": "{{classificationId}}"
            },
            "Classify or reclassify products. NEW in v66.0"
        ),
    ]

    for endpoint in new_endpoints:
        if endpoint["name"] not in existing_names:
            folder["item"].append(endpoint)
            added_count += 1

    return added_count


def add_pd_endpoints(folder: Dict[str, Any]) -> int:
    """Add Product Discovery endpoints to Product Discovery folder."""

    if "item" not in folder:
        folder["item"] = []

    existing_names = {e["name"] for e in folder["item"]}
    added_count = 0

    new_endpoints = [
        create_endpoint(
            "PD: Global Search",
            "POST",
            "connect/cpq/products/search",
            {
                "query": "{{searchQuery}}",
                "pageSize": 20,
                "offset": 0,
                "searchType": "global"
            },
            "Global search across all product catalogs. API v66.0+"
        ),
        create_endpoint(
            "PD: Bulk Products",
            "POST",
            "connect/cpq/products/bulk",
            {
                "productIds": ["{{productId1}}", "{{productId2}}"],
                "pageSize": 100,
                "offset": 0
            },
            "Retrieve multiple products in bulk. API v66.0+"
        ),
        create_endpoint(
            "PD: Guided Selection",
            "POST",
            "connect/cpq/products/guided-selection",
            {
                "accountId": "{{defaultAccountId}}",
                "questionnaire": [
                    {
                        "questionId": "q1",
                        "answer": "value"
                    }
                ]
            },
            "Product discovery via guided selection questionnaire. API v66.0+"
        ),
    ]

    for endpoint in new_endpoints:
        if endpoint["name"] not in existing_names:
            folder["item"].append(endpoint)
            added_count += 1

    return added_count


def add_pricing_endpoints(folder: Dict[str, Any]) -> int:
    """Add Pricing endpoints to Salesforce Pricing folder."""

    if "item" not in folder:
        folder["item"] = []

    existing_names = {e["name"] for e in folder["item"]}
    added_count = 0

    new_endpoints = [
        create_endpoint(
            "Pricing: Get Waterfall",
            "GET",
            "connect/core-pricing/waterfall/{{lineItemId}}/{{executionId}}",
            description="Retrieve pricing waterfall details for a line item. API v66.0+"
        ),
        create_endpoint(
            "Pricing: Post Waterfall",
            "POST",
            "connect/core-pricing/waterfall",
            {
                "lineItemId": "{{currentLineItemId}}",
                "executionId": "{{executionId}}",
                "includeComponentBreakdown": True
            },
            "Submit waterfall pricing adjustments. API v66.0+"
        ),
        create_endpoint(
            "Pricing: API Execution Logs",
            "GET",
            "connect/core-pricing/pricing/api-execution-logs",
            description="Retrieve API execution logs for pricing calculations. API v66.0+"
        ),
        create_endpoint(
            "Pricing: Process Execution",
            "GET",
            "connect/core-pricing/pricing/execution",
            description="Query pricing process execution details. API v66.0+"
        ),
        create_endpoint(
            "Pricing: Recipe Mapping",
            "POST",
            "connect/core-pricing/recipe/mapping",
            {
                "recipeId": "{{pricingRecipeId}}",
                "productId": "{{productId}}",
                "mappingRules": []
            },
            "Define recipe-to-product mappings. API v66.0+"
        ),
    ]

    for endpoint in new_endpoints:
        if endpoint["name"] not in existing_names:
            folder["item"].append(endpoint)
            added_count += 1

    return added_count


# ============================================================================
# RCA COLLECTION UPDATES
# ============================================================================

def update_rca_collection(filepath: str) -> tuple[Dict[str, Any], Dict[str, int]]:
    """Update the RCA collection for v260 validation and consistency."""

    with open(filepath, 'r') as f:
        collection = json.load(f)

    changes = {
        "description_updated": False,
        "v260_renamed": 0,
        "billing_endpoints_added": 0,
        "usage_endpoints_added": 0,
        "transaction_endpoints_added": 0,
        "configurator_verified": False,
    }

    # Update collection description
    if "v260" not in collection["info"]["description"] and "v66.0" not in collection["info"]["description"]:
        collection["info"]["description"] = (
            "Revenue Cloud APIs - Validated for Spring '26 (v66.0)\n\n"
            "Extended collection covering all Revenue Cloud domains including CPQ, Billing, "
            "Usage Management, Rate Management, Revenue Orchestration, and more."
        )
        changes["description_updated"] = True

    # Process items to rename v260 folders and update endpoints
    for item in collection["item"]:
        # Rename v260 to v66.0 for consistency
        if "(v260)" in item["name"]:
            item["name"] = item["name"].replace("(v260)", "(v66.0)")
            changes["v260_renamed"] += 1

        # Update specific folders
        if item["name"] == "Billing":
            changes["billing_endpoints_added"] = add_billing_endpoints(item)
        elif item["name"] == "Usage Management":
            changes["usage_endpoints_added"] = add_usage_endpoints(item)
        elif item["name"] == "Transaction Management":
            changes["transaction_endpoints_added"] = add_transaction_endpoints(item)
        elif "Product Configurator (v66.0)" in item["name"]:
            changes["configurator_verified"] = verify_configurator_endpoints(item)

    return collection, changes


def add_billing_endpoints(folder: Dict[str, Any]) -> int:
    """Add missing billing endpoints to Billing folder."""

    if "item" not in folder:
        folder["item"] = []

    existing_names = {e["name"] for e in folder["item"]}
    added_count = 0

    new_endpoints = [
        create_endpoint(
            "Billing: Recover Billing Schedules",
            "POST",
            "commerce/billing/billing-schedules/actions/recover",
            {
                "billingScheduleIds": ["{{billingScheduleId}}"],
                "recoveryReason": "Schedule recovery"
            },
            "Recover suspended billing schedules. API v66.0+"
        ),
        create_endpoint(
            "Billing: Preview Next Invoice",
            "POST",
            "commerce/billing/invoices/actions/preview",
            {
                "billingAccountId": "{{billingAccountId}}",
                "invoiceDate": "2026-04-01"
            },
            "Preview next invoice for a billing account. API v66.0+"
        ),
        create_endpoint(
            "Billing: Ingest Invoice",
            "POST",
            "commerce/billing/invoices/actions/ingest",
            {
                "billingAccountId": "{{billingAccountId}}",
                "invoiceData": {}
            },
            "Ingest an external invoice into Revenue Cloud. API v66.0+"
        ),
    ]

    for endpoint in new_endpoints:
        if endpoint["name"] not in existing_names:
            folder["item"].append(endpoint)
            added_count += 1

    return added_count


def add_usage_endpoints(folder: Dict[str, Any]) -> int:
    """Add missing usage management endpoints."""

    if "item" not in folder:
        folder["item"] = []

    existing_names = {e["name"] for e in folder["item"]}
    added_count = 0

    new_endpoints = [
        create_endpoint(
            "Usage: Consumption Traceabilities",
            "POST",
            "revenue/usage-management/consumption/actions/trace",
            {
                "usageResourceId": "{{usageResourceId}}",
                "startDate": "2026-01-01",
                "endDate": "2026-03-31"
            },
            "Trace consumption traceabilities for usage resources. NEW in v66.0"
        ),
        create_endpoint(
            "Usage: Product Validation",
            "POST",
            "revenue/usage-management/usage-products/actions/validate",
            {
                "usageProductId": "{{usageProductId}}",
                "validationType": "full"
            },
            "Validate usage product configurations. NEW in v66.0"
        ),
    ]

    for endpoint in new_endpoints:
        if endpoint["name"] not in existing_names:
            folder["item"].append(endpoint)
            added_count += 1

    return added_count


def add_transaction_endpoints(folder: Dict[str, Any]) -> int:
    """Add missing transaction management endpoints."""

    if "item" not in folder:
        folder["item"] = []

    existing_names = {e["name"] for e in folder["item"]}
    added_count = 0

    new_endpoints = [
        create_endpoint(
            "Transaction: Get Eligible Promotions",
            "POST",
            "commerce/sales-transactions/actions/get-eligible-promotions",
            {"salesTransactionId": "{{currentQuoteId}}"},
            "Retrieve promotions eligible for a sales transaction. NEW in v66.0"
        ),
        create_endpoint(
            "Transaction: Retrieve API Errors",
            "GET",
            "commerce/sales-transactions/api-errors",
            description="Retrieve API errors for sales transactions. NEW in v66.0"
        ),
    ]

    for endpoint in new_endpoints:
        if endpoint["name"] not in existing_names:
            folder["item"].append(endpoint)
            added_count += 1

    return added_count


def verify_configurator_endpoints(folder: Dict[str, Any]) -> bool:
    """Verify Product Configurator has all 13 endpoints."""

    if "item" not in folder:
        return False

    endpoint_count = len(folder["item"])

    # The 13 documented Product Configurator v66.0 APIs:
    # 1. Get Configuration for Product
    # 2. Create Configuration
    # 3. Update Configuration
    # 4. Delete Configuration
    # 5. Get Configuration Actions
    # 6. Get Configuration Rules
    # 7. Validate Configuration
    # 8. Get Configuration Options
    # 9. Get Configuration Attributes
    # 10. Get Configuration Variants
    # 11. Clone Configuration
    # 12. Get Configuration by ID
    # 13. List Configurations

    expected_count = 13

    if endpoint_count < expected_count:
        # Add missing placeholder endpoints
        existing_names = {e.get("name", "") for e in folder["item"]}

        missing_endpoints = [
            create_endpoint(
                "PC: Get Configuration for Product",
                "GET",
                "connect/product-configurator/configurations/product/{{productId}}",
                description="Retrieve configuration for a product. API v66.0+"
            ) if "PC: Get Configuration for Product" not in existing_names else None,
            create_endpoint(
                "PC: Validate Configuration",
                "POST",
                "connect/product-configurator/configurations/actions/validate",
                {"configurationId": "{{configurationId}}"},
                description="Validate a product configuration. API v66.0+"
            ) if "PC: Validate Configuration" not in existing_names else None,
            create_endpoint(
                "PC: Clone Configuration",
                "POST",
                "connect/product-configurator/configurations/{{configurationId}}/actions/clone",
                {"targetName": "Cloned Configuration"},
                description="Clone an existing configuration. API v66.0+"
            ) if "PC: Clone Configuration" not in existing_names else None,
        ]

        for endpoint in missing_endpoints:
            if endpoint:
                folder["item"].append(endpoint)

    return endpoint_count >= expected_count


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""

    rlm_path = "RLM.postman_collection.json"
    rca_path = "RCA APIs - Winter'25 (258) Latest.postman_collection.json"

    print("=" * 80)
    print("POSTMAN COLLECTION UPDATE SCRIPT - Revenue Cloud v260 (Spring '26, API v66.0)")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Update RLM Collection
    print("1. UPDATING RLM COLLECTION")
    print("-" * 80)

    if not os.path.exists(rlm_path):
        print(f"ERROR: {rlm_path} not found!")
        return

    rlm_collection, rlm_changes = update_rlm_collection(rlm_path)

    print(f"   Description updated: {rlm_changes['description_updated']}")
    print(f"   Transaction Management endpoints added: {rlm_changes['transaction_mgmt_added']}")
    print(f"   PCM endpoints added: {rlm_changes['pcm_endpoints_added']}")
    print(f"   Product Discovery endpoints added: {rlm_changes['pd_endpoints_added']}")
    print(f"   Pricing endpoints added: {rlm_changes['pricing_endpoints_added']}")
    print(f"   Total new endpoints: {sum([rlm_changes['transaction_mgmt_added'], rlm_changes['pcm_endpoints_added'], rlm_changes['pd_endpoints_added'], rlm_changes['pricing_endpoints_added']])}")

    with open(rlm_path, 'w') as f:
        json.dump(rlm_collection, f, indent=2)
    print(f"   ✓ Updated file written to {rlm_path}")
    print()

    # Update RCA Collection
    print("2. UPDATING RCA COLLECTION")
    print("-" * 80)

    if not os.path.exists(rca_path):
        print(f"ERROR: {rca_path} not found!")
        return

    rca_collection, rca_changes = update_rca_collection(rca_path)

    print(f"   Description updated: {rca_changes['description_updated']}")
    print(f"   v260 folder names renamed to v66.0: {rca_changes['v260_renamed']}")
    print(f"   Billing endpoints added: {rca_changes['billing_endpoints_added']}")
    print(f"   Usage Management endpoints added: {rca_changes['usage_endpoints_added']}")
    print(f"   Transaction Management endpoints added: {rca_changes['transaction_endpoints_added']}")
    print(f"   Product Configurator verified (13 endpoints): {rca_changes['configurator_verified']}")
    print(f"   Total new endpoints: {sum([rca_changes['billing_endpoints_added'], rca_changes['usage_endpoints_added'], rca_changes['transaction_endpoints_added']])}")

    with open(rca_path, 'w') as f:
        json.dump(rca_collection, f, indent=2)
    print(f"   ✓ Updated file written to {rca_path}")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_rlm_endpoints = sum([
        rlm_changes['transaction_mgmt_added'],
        rlm_changes['pcm_endpoints_added'],
        rlm_changes['pd_endpoints_added'],
        rlm_changes['pricing_endpoints_added']
    ])
    total_rca_endpoints = sum([
        rca_changes['billing_endpoints_added'],
        rca_changes['usage_endpoints_added'],
        rca_changes['transaction_endpoints_added']
    ])

    print(f"RLM Collection: {total_rlm_endpoints} new endpoints added")
    print(f"RCA Collection: {total_rca_endpoints} new endpoints added, {rca_changes['v260_renamed']} folders renamed")
    print(f"Total updates: {total_rlm_endpoints + total_rca_endpoints + rca_changes['v260_renamed']} changes")
    print()
    print("✓ All collections updated successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()

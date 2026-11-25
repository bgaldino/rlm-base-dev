---
page_id: connect-resources-place-supplemental-transaction
title: Place Supplemental Transaction (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-place-supplemental-transaction.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-business-apis-rest-references
legacy_page_id: connect_resources_place_supplemental_transaction.htm
fetched_at: 2026-11-25
---

# Place Supplemental Transaction (POST)

Create a supplemental order or change orders after they are submitted for processing, such as during the fulfillment process.

Keep these considerations in mind when you use this API.

- The original order must not be assetized.

- If Billing is enabled and configured for the order, verify that the original order hasn’t been billed.

- If Dynamic Revenue Orchestration (DRO) is enabled and configured for the order, ensure the original order hasn’t reached the point of no return milestone. If point of no return milestone hasn’t been reached, the fulfillment plan is frozen.

## Resource

```
/connect/rev/sales-transaction/actions/place-supplemental-transaction
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/rev/sales-transaction/actions/place-supplemental-transaction
```

## Available Version

64.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

This sample creates a supplemental order, which is a clone of the original order. The supplemental order is related to the original order.

```
{
  "relatedSalesTransactionId": "801S70000001VKgIAM"
}
```

This sample overrides a field value of an order line item to supplement the order item with ID value as `802SG000003vZ15YAE`.

```
{
    "relatedSalesTransactionId": "801S70000001VKgIAM",
    "pricingPref": "System",
    "supplementalGraph": {
        "graphId": "1",
        "records": [
            {
                "referenceId": "refOrder",
                "record": {
                    "attributes": {
                        "type": "Order",
                        "method": "PATCH",
                        "id": "801S70000001VKgIAM"
                    },
                    "EffectiveDate": "2025-03-01",
                    "QuoteId": "0Q0xx0000004DQ4CAM"
                }
            },
            {
                "referenceId": "refOrderItem",
                "record": {
                    "attributes": {
                        "type": "OrderItem",
                        "method": "PATCH",
                        "id": "802SG000003vZ15YAE"
                    },
                    "QuoteLineItemId": "0Q0xx0000004E2mYLK"
                }
            }
        ]
    }
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `pricingPref` | String | Pricing preference for this supplemental transaction or order ingestion process. If `pricingPref` value is defined as either `Force` or `System`, the supplemental order can have a different pricing from the original order. | Optional | 64.0 |
| `relatedSales​TransactionId` | String | Related or the original sales transaction upon which a supplemental transaction is created. | Required | 64.0 |
| `supplemental​Graph` | [Object Graph Input](./connect-requests-object-graph-input.md) | The sObject graph that represents a payload with the additional changes to be ingested. The attribute’s HTTP method must be PATCH. The attribute ID must be the ID of the original order or order item that you want to supplement. | Optional | 64.0 |

Valid values are:

- `Force`—Enforces pricing during the creation of sales transactions.

- `Skip`—Skips pricing during the creation of sales transactions.

- `System`—Determines whether a pricing calculation is required.

## Response Body for POST

[Supplemental Transaction](./connect-responses-place-supplemental-transaction-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-place-supplemental-transaction.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

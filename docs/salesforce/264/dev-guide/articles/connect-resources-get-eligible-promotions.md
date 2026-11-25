---
page_id: connect-resources-get-eligible-promotions
title: Get Eligible Promotions (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-eligible-promotions.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-business-apis-rest-references
legacy_page_id: connect_resources_get_eligible_promotions.htm
fetched_at: 2026-11-25
---

# Get Eligible Promotions (POST)

Get eligible promotions for line items within a quote or an order.

This API accepts line item IDs and sales transaction ID as the input and then initializes the context by filtering on the specific line items.

## Resource

```
/revenue/transaction-management/sales-transactions/actions/get-eligible-promotions
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/revenue/transaction-management/sales-transactions/actions/get-eligible-promotions
```

## Available Version

66.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "salesTransactionId": "0Q0xx0000004EOECA2",
  "lineItemIds": [
    "0QLxx0000004E7eGAE",
    "0QLxx0000004GCeGAM",
    "0QLxx0000004E7gGAE"
  ]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `lineItemIds` | String[] | List of line item IDs to evaluate for promotions. The object type is auto-determined from the sales transaction ID. | Required | 66.0 |
| `salesTransactionId` | String | The sales transaction ID, such as an order ID or a quote ID, for the promotion evaluation. | Required | 66.0 |

## Response Body for POST

[Get Eligible Promotions](./connect-responses-get-eligible-promotions-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-eligible-promotions.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

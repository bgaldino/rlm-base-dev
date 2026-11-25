---
page_id: connect-resources-unlock-transaction
title: Unlock Transaction (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-unlock-transaction.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-business-apis-rest-references
legacy_page_id: connect_resources_unlock_transaction.htm
fetched_at: 2026-11-25
---

# Unlock Transaction (POST)

Unlock a quote or order whose calculation is stuck in a non-terminal status so that you can retry the transaction.

Use this API when a [Place Sales Transaction](./connect-resources-place-sales-transaction.md) call is stuck in a non-terminal calculation status. The API sets the calculation status to the appropriate failure status, such as `ConfigurationFailed` or `PriceCalculationFailed` so that you can retry the transaction. To use this API, you need the `userCanAccessRLMPlaceSalesTransaction` or `userCanAccessCoreCPQ` permission.

Keep these considerations in mind when you use this API.

- This release supports only one record ID in the `salesTransactionIds` property.

- If the calculation status is already one of the terminal statuses, such as `CompletedWithPricing`, `CompletedWithoutPricing`, `CompletedWithTax`, `PriceCalculationFailed`, or `ConfigurationFailed`, the API returns an error and doesn’t change the status.

## Resource

```
/revenue/transaction-management/sales-transactions/actions/unlock-transaction
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/revenue/transaction-management/sales-transactions/actions/unlock-transaction
```

## Available Version

68.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

This example shows a sample request to unlock a stuck sales transaction calculation.

```
{
  "salesTransactionIds": ["0Q0xx0000004CIiCAM"]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sales​Transaction​Ids` | String[] | List of record IDs, such as a quote or an order, whose calculation status is unlocked. This release supports only one record ID. | Required | 68.0 |

## Response Body for POST

[Unlock Transaction](./connect-responses-unlock-transaction-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-unlock-transaction.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

---
page_id: connect-resources-clone-sales-transaction
title: Clone Sales Transaction (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-clone-sales-transaction.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-business-apis-rest-references
legacy_page_id: connect_resources_clone_sales_transaction.htm
fetched_at: 2026-11-25
---

# Clone Sales Transaction (POST)

Create a clone of a sales transaction, such as a quote or an order. You can also clone a quote line item or an order item record with its related records and configurations.

This API supports the cloning of records for these objects.

- Quote

- QuoteLineItem

- OrderItem

- QuoteLineGroup

- Order

- OrderItemGroup

You can clone all items in a quote line group or order item group when the record to clone is a quote line group or an order item group record.

## Resource

```
/connect/rev/sales-transaction/actions/clone
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v64.0/connect/rev/sales-transaction/actions/clone
```

## Available Version

64.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

This is a sample request to clone a record within a sales transaction.

```
{
  "recordIds": ["0QLxx0000004CBYGA2"],
  "salesTransactionId": "0Q0xx0000004CE0CAM"
}
```

This is a sample request to clone all line items in a ramped group within a sales transaction.

```
{
  "recordIds": ["0QLxx0000004CBYGA2"],
  "salesTransactionId": "0Q0xx0000004CE0CAM",
  "options": {
    "lineScope": "AllLines"
  }
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `recordIds` | String[] | ID of the record to be cloned. You can specify a single record ID only. | Required | 64.0 |
| `salesTransactionId` | String | ID of the sales transaction related to the record IDs to clone. | Required | 64.0 |
| `options` | [Clone Options Input](./connect-requests-clone-options-input.md) | Specifies options to clone a ramp segment within a sales transaction. You can clone only the last ramp segment. | Optional | 65.0 |

## Response Body for POST

[Clone Sales Transaction](./connect-responses-clone-sales-transaction-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-clone-sales-transaction.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

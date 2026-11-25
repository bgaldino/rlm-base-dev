---
page_id: actions-obj-create-order-from-quote
title: Create Order From Quote Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-create-order-from-quote.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-invocable-actions-parent
legacy_page_id: actions_obj_create_order_from_quote.htm
fetched_at: 2026-11-25
---

# Create Order From Quote Action

Create a draft order from a quote record.

This action is available in API version 60.0 and later.

**Note:**

This API has been deprecated as of API version 65.0. In API version 65.0 and later, use the [Create Orders From Quote Action](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_create_orders_from_quote.htm).

## Special Access Rules

The Create Order From Quote action is available in Enterprise, Unlimited, and Developer Editions of Revenue Management.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/createOrderFromQuote`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `quoteRecordId` | id | Required. ID of the quote record. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `orderId` | string | ID of the created draft order. |
| `orderNumber` | string | Unique order number of the created draft order. |
| `requestId` | string | ID of the request. |

## Example

**POST**

This sample request is for the Create Order From Quote action.

```
{
    "inputs": [
        {
        "quoteRecordId": "0Q0D200000000DhKAI"
        }
    ]
}
```

This sample response is for the Create Order From Quote action.

```
[
  {
    "actionName": "createOrderFromQuote",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "orderNumber": "00000122",
      "orderId": "801oB000000DCrNQAW"
    },
    "sortOrder": -1,
    "version": 1
  }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-create-order-from-quote.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

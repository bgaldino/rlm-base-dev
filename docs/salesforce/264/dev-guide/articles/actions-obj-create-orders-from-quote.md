---
page_id: actions-obj-create-orders-from-quote
title: Create Orders From Quote Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-create-orders-from-quote.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-invocable-actions-parent
legacy_page_id: actions_obj_create_orders_from_quote.htm
fetched_at: 2026-11-25
---

# Create Orders From Quote Action

Create multiple orders from a single quote instead of a single order, ensuring easier order management and fulfillment operations.

- You can create an order by selecting a subset of quote line items.

- You can split a quote into multiple orders based on quote line group.

- You can split a quote into multiple orders based on a quote line item field, such as Product2.

See [Considerations for Creating Multiple Orders from a Quote](https://help.salesforce.com/s/articleView?id=ind.qocal_split_quote_to_orders_important_considerations.htm). This action is available in API version 65.0 and later.

## Special Access Rules

Ensure the **Advanced Order Creation From Quote** toggle from Revenue Settings from Setup is enabled to access this action.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/createOrdersFromQuote`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `orderCreationMethod` | string | If specified, represents the method used to create orders. Valid values are `CreateSingleOrder`—Creates a single order from a quote. This method creates the order header and order line items synchronously; `CreateOrderByGroup`—Create multiple orders based on a quote line group; or `CreateOrderByField`—Create multiple orders based on a specified quote line item field. If you’re creating multiple orders from a quote, the order header records are created synchronously and order line items are created asynchronously. If unspecified, the default value is `CreateSingleOrder`. |
| `orderCreationParameters` | Apex-defined | An Apex `ConnectApi.OrderCreationParametersInputRepresentation` record that contains the additional parameters required by the specified order creation method. |
| `quoteId` | id | Required. The ID of the source quote tied to the orders created. |
| `quoteLineItemIds` | id | List of quote line item IDs to create the orders from. If specified, the orders are created for the list of provided quote line items. If unspecified, orders are created for all quote line items. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `orderIds` | id | List of the created order IDs. |
| `requestId` | string | The request ID used to query the async status. |
| `statusUrl` | string | The status URL that’s used to track the async status. |

## Examples

**Create a Partial Order From a Quote**

This example shows a sample request to create a partial order from a quote.

```
{
  "inputs": [
    {
      "quoteId": "0Q0DU0000005tJc0AI",
      "quoteLineItemIds": [
        "0QLDU000000ay2G4AQ",
        "0QLDU000000ay2n4AA"
      ],
      "orderCreationMethod": "CreateSingleOrder"
    }
  ]
}
```

This example shows a sample successful response.

```
{
    "actionName": "createOrdersFromQuote",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "requestId": null,
      "statusUrl": null,
      "orderIds": [
        "801DU000000EYySYAW"
      ]
    },
    "sortOrder": -1,
    "version": 1
  }
```

**Create Orders From a Quote Based on a Quote Line Group**

This example shows a sample request to create orders from a quote based on a quote line group.

```
{
  "inputs": [
    {
      "quoteId": "0Q0DU0000005tJk0AI",
      "orderCreationMethod": "CreateOrderByGroup"
    }
  ]
}
```

This example shows a sample successful response.

```
{
  "actionName": "createOrdersFromQuote",
  "errors": null,
  "invocationId": null,
  "isSuccess": true,
  "outcome": null,
  "outputValues": {
    "requestId": "16PRM0000004DBq",
    "orderIds": [
      "801S70000001VKgIAM"
    ],
    "success": true,
    "errors": [],
    "statusURL": "/services/data/v68.0/sobjects/AsyncOperationTracker/16PRM0000004DBq"
  },
  "sortOrder": -1,
  "version": 1
}
```

**Create Orders From a Quote Based on a Quote Line Item Field**

This example shows a sample request to create orders from a quote based on a quote line item field

```
{
  "inputs": [
    {
      "quoteId": "0Q0DU0000005tJW0AY",
      "orderCreationMethod": "CreateOrderByField",
      "orderCreationParameters": {
        "splitFieldName": "Product2Id"
      }
    }
  ]
}
```

This example shows a sample successful response.

```
{
  "actionName": "createOrdersFromQuote",
  "errors": null,
  "invocationId": null,
  "isSuccess": true,
  "outcome": null,
  "outputValues": {
    "requestId": "16PRM0000004DBq",
    "orderIds": [
      "801S70000001VKgIAM",
      "801S70000001WKgIBN"
    ],
    "success": true,
    "errors": [],
    "statusURL": "/services/data/v68.0/sobjects/AsyncOperationTracker/16PRM0000004DBq"
  },
  "sortOrder": -1,
  "version": 1
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-create-orders-from-quote.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

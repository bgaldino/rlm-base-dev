---
page_id: actions_obj_create_order_from_quote.htm
title: Create Order From Quote Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_create_order_from_quote.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Create Order From Quote Action

Create an order from a quote record.

This action is available in API version 60.0 and later.

## Special Access Rules

The Create Order From Quote action is available in Enterprise, Unlimited, and Developer
Editions of Revenue Cloud.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/createOrderFromQuote`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization: Bearer
    token`

## Inputs

| Input | Details |
| --- | --- |
| quoteRecordId | Type  datetime  Description  Required.  ID of the quote record. |

## Outputs

| Output | Details |
| --- | --- |
| requestId | Type  string  Description  ID of the request. |

## Example

POST
:   This sample request is for the Create Order From Quote action.

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

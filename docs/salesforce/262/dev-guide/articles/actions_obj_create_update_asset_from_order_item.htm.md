---
page_id: actions_obj_create_update_asset_from_order_item.htm
title: Create or Update Asset From Order Item Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_create_update_asset_from_order_item.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Create or Update Asset From Order Item Action

Create assets from individual order items within an order. Track
assets after the individual line items of an order reach a certain stage in their
lifecycle, such as submitted, fulfilled, or provisioned. If the order item is part of a
renewal, an amendment, or a cancellation, existing assets are changed.

This action is available in API version 60.0 and later.

## Special Access Rules

You need the Assetize Order permission set to
use this invocable action.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/createOrUpdateAssetFromOrderItem`

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
| orderId | Type  string  Description  Required.  ID of the order. |

## Outputs

| Output | Details |
| --- | --- |
| requestId | Type  string  Description  ID of the request to create an asset. |

## Example

POST
:   This sample request is for the Create or Update Asset From Order Item
    action.

    ```
    {
        "inputs": [
            {
                "orderItemIds": ["802SG000002HixxYAC"]
            }
        ]
    }
    ```

    This sample response is for the Create or Update Asset From Order Item
    action.

    ```
    {
      "actionName": "createOrUpdateAssetFromOrderItem",
      "errors": null,
      "isSuccess": true,
      "outputValues": {
        "requestId": "b2a2b4b9-845b-4078-980a-759308389604"
      },
      "version": 1
    }
    ```

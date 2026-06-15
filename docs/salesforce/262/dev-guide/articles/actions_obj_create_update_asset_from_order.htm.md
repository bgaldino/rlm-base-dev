---
page_id: actions_obj_create_update_asset_from_order.htm
title: Create or Update Asset From Order Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_create_update_asset_from_order.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Create or Update Asset From Order Action

Create an asset for each order item in the specified order. New
assets are created for a new order. Modify existing assets for change order requests,
such as a renewal or a cancellation.

When the custom product name for an order line item has a value, the asset name is set
to custom product name.

This action is available in API version 60.0 and
later.

## Special Access Rules

You need the Assetize Order permission set to use
this invocable action.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/createOrUpdateAssetFromOrder`

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
:   This sample request is for the Create or Update Asset From Order action.

    ```
    {
      "inputs": [
        {
          "orderId": "801DE000000oJfAYAU"
        }
      ]
    }
    ```

    This sample response is for the Create or Update Asset From Order action.

    ```
    [
        {
            "actionName": "createOrUpdateAssetFromOrder",
            "errors": null,
            "isSuccess": true,
            "outputValues": {
                "requestId": "3b89392d-6987-40d9-9190-d18fdb5cb849"
            }
        }
    ]
    ```

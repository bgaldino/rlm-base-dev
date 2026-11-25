---
page_id: actions-obj-create-update-asset-from-order
title: Create or Update Asset From Order Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-create-update-asset-from-order.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-invocable-actions-parent
legacy_page_id: actions_obj_create_update_asset_from_order.htm
fetched_at: 2026-11-25
---

# Create or Update Asset From Order Action

Create an asset for each order item in the specified order. New assets are created for a new order. Modify existing assets for change order requests, such as a renewal or a cancellation.

When the custom product name for an order line item has a value, the asset name is set to custom product name.

This action is available in API version 60.0 and later.

## Special Access Rules

You need the Assetize Order permission set to use this invocable action.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/createOrUpdateAssetFromOrder`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `orderId` | string | Required. ID of the order. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `requestId` | string | ID of the request to create an asset. |

## Example

**POST**

This sample request is for the Create or Update Asset From Order action.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-create-update-asset-from-order.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

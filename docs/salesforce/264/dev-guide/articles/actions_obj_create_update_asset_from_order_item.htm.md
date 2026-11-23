---
page_id: actions_obj_create_update_asset_from_order_item.htm
title: Create or Update Asset From Order Item Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_create_update_asset_from_order_item.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Create or Update Asset From Order Item Action

Create assets from individual order items within an order. Track assets after the individual line items of an order reach a certain stage in their lifecycle, such as submitted, fulfilled, or provisioned. If the order item is part of a renewal, an amendment, or a cancellation, existing assets are changed.

This action is available in API version 60.0 and later.

## Special Access Rules

You need the Assetize Order permission set to use this invocable action.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/createOrUpdateAssetFromOrderItem`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer token`

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| orderId | string | Required. ID of the order. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| requestId | string | ID of the request to create an asset. |

## Example

**POST**

This sample request is for the Create or Update Asset From Order Item action.

```
{
    "inputs": [
        {
            "orderItemIds": ["802SG000002HixxYAC"]
        }
    ]
}
```

This sample response is for the Create or Update Asset From Order Item action.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_create_update_asset_from_order_item.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

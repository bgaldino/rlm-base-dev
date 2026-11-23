---
page_id: actions_obj_initiate_rollback_last_action.htm
title: Initiate Rollback on Last Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_initiate_rollback_last_action.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Initiate Rollback on Last Action

Initiate the reversal of the last action on an asset to rectify any transactional errors or to meet changing business requirements.

Use this action to revert the last amendment or renewal on a particular asset, restoring the asset to its previous state. This action creates a quote or an order based on the specified output type. Use the created reversal quote to verify the reversal and convert the quote into an order.

Keep these considerations in mind when you use this action.

- You can roll back only future dated transactions.
- Rollback action isn't supported for legacy assets.
- The rollback operation is supported for amendment and renewal only.

This action is available in API version 65.0 and later.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/initiateRollBackLastAction`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer token`

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| assetIds | string | Required. List of asset IDs to include in the last action rollback. |
| outputType | string | Required. The type of record to create for reversal. Valid values are `Quote`—Creates a reversal quote or `Order`—Creates a reversal order. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| recordId | id | The ID of the created quote or order. |

## Example

**POST**

This example shows a sample request that initiates the rollback action on an asset and converts it into a quote.

```
{
  "inputs": [
    {
      "assetIds": [
        "02iDU0000006UisYAE"
      ],
      "outputType": "Quote"
    }
  ]
}
```

This example shows a sample successful response.

```
{
  "actionName": "initiateRollBackLastAction",
  "errors": null,
  "isSuccess": true,
  "outputValues": {
    "recordId": "0Q0xx0000004NsSCAU"
  },
  "version": 1
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_initiate_rollback_last_action.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

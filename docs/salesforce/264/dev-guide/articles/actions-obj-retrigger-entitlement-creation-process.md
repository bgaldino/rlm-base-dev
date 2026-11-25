---
page_id: actions-obj-retrigger-entitlement-creation-process
title: Retrigger Entitlement Creation Process Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-retrigger-entitlement-creation-process.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-invocable-actions-parent
legacy_page_id: actions_obj_retrigger_entitlement_creation_process.htm
fetched_at: 2026-11-25
---

# Retrigger Entitlement Creation Process Action

Retrigger entitlement creation process for failed or unprocessed assets.

Trigger the entitlement creation process again in these scenarios.

- Process failed assets in the asset to entitlement journey.

- Assetize or create wallets for assets without corresponding records in Usage Management.

This action is available in API version 65.0 and later.

## Special Access Rules

The Retrigger Entitlement Creation Process action is available in Enterprise, Developer, and Unlimited Editions where Usage Management is enabled. To use this action, you need the Usage Management Run Time User permission.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/retriggerEntlCreaProc`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `assetId` | string | Required. ID of the asset for which you want to trigger the asset to entitlement process again. |

## Outputs

None.

## Example

**POST**

Here’s a sample request for the Retrigger Entitlement Creation Process action.

```
{
  "inputs": [
    {
      "assetId": "02iSB000000JzZFYA0"
    }
  ]
}
```

Here’s a sample response for the Retrigger Entitlement Creation Process action.

```
[
  {
    "actionName": "retriggerEntlCreaProc",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": null,
    "sortOrder": -1,
    "version": 1
  }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-retrigger-entitlement-creation-process.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

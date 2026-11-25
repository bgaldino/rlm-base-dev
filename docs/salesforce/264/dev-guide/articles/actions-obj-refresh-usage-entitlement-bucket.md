---
page_id: actions-obj-refresh-usage-entitlement-bucket
title: Refresh Usage Entitlement Bucket Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-refresh-usage-entitlement-bucket.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-invocable-actions-parent
legacy_page_id: actions_obj_refresh_usage_entitlement_bucket.htm
fetched_at: 2026-11-25
---

# Refresh Usage Entitlement Bucket Action

Refresh entitlements by evaluating the usage entitlement bucket records and creating a new usage entitlement entry.

This action is available in API version 63.0 and later.

## Special Access Rules

The Refresh Usage Entitlement Bucket action is available in Enterprise, Developer, and Unlimited Editions where Usage Management is enabled. To use this action, you need the Usage Management Run Time User permission.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/refreshUsageEntitlementBucket`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `transactionUsageEntitlementId` | string | Required. ID of the transaction usage entitlement record that’s associated with the usage entitlement buckets that you need to refresh. |

## Outputs

None.

## Example

**POST**

This example shows a sample request for the Refresh Usage Entitlement Bucket action.

```
{
  "inputs": [
    {
      "transactionUsageEntitlementId": "3ttDU00000000iZYAQ"
    }
  ]
}
```

This example shows a sample response for the Refresh Usage Entitlement Bucket action.

```
{
  "actionName": "refreshUsageEntitlementBucket",
  "errors": null,
  "isSuccess": true
}
```

**See Also**

- [*Salesforce Help*: Permission Set Licenses, Personas, and User Permissions for Usage Management](https://help.salesforce.com/s/articleView?id=ind.um_usage_management_psls_and_personas.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-refresh-usage-entitlement-bucket.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

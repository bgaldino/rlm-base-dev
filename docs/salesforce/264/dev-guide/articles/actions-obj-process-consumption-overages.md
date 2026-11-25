---
page_id: actions-obj-process-consumption-overages
title: Process Consumption Overages Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-process-consumption-overages.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-invocable-actions-parent
legacy_page_id: actions_obj_process_consumption_overages.htm
fetched_at: 2026-11-25
---

# Process Consumption Overages Action

Process consumption overages for the usage summary records with `SummaryComplete` status. This action uses the entitlement service to process the overages.

This action is available in API version 63.0 and later.

## Special Access Rules

The Process Consumption Overages action is available in Enterprise, Developer, and Unlimited Editions where Usage Management is enabled. To use this action, you need the Usage Management Run Time User permission.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/processConsumptionOverages`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `usageRatableSummaryId` | string | Required. ID of the usage ratable summary record that contains the consumption details, and is used to calculate consumption overages and create usage entitlement entry records. |

## Outputs

None.

## Example

**POST**

This example shows a sample request for the Process Consumption Overages action.

```
{
  "inputs": [
    {
      "usageRatableSummaryId": "3ttDU00000000iZYAQ"
    }
  ]
}
```

This example shows a sample response for the Process Consumption Overages action.

```
{
  "actionName": "processConsumptionOverages",
  "errors": null,
  "isSuccess": true
}
```

**See Also**

- [*Salesforce Help*: Permission Set Licenses, Personas, and User Permissions for Usage Management](https://help.salesforce.com/s/articleView?id=ind.um_usage_management_psls_and_personas.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-process-consumption-overages.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

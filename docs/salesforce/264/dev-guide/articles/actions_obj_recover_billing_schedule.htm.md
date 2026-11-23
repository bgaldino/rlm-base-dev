---
page_id: actions_obj_recover_billing_schedule.htm
title: Recover Billing Schedules Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_recover_billing_schedule.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Recover Billing Schedules Action

Recover one or more billing schedules in the `Error` or `Processing` status.

This action uses the ID of the billing schedule record in the `Error` or `Processing` status to retrieve the latest generated invoice. This action also retrieves any other billing schedules in the `Error` or `Processing` status associated with that invoice.

This action is available in API version 62.0 and later.

## Special Access Rules

The Recover Billing Schedules action is available in Enterprise, Unlimited, and Developer Editions where Billing is enabled. To use this action, you need the Manage Errors Using Invoice Error Recovery API permission set.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/recoverBillingSchedules`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer token`

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| billingScheduleId | string | Required. ID of the billing schedule record in the `Error` or `Processing` status. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| successBillingScheduleIds | string | Comma-separated list of IDs associated with the parent billing schedule record in the `Error` or `Processing` status. |

## Example

**POST**

This example shows a sample request for the Recover Billing Schedules action.

```
{
  "inputs": [
    {
      "billingScheduleId": "801xx000003JztvAAC"
    }
  ]
}
```

This example shows a sample response for the Recover Billing Schedules action.

```
{
  "actionName": "recoverBillingSchedules",
  "errors": null,
  "isSuccess": true,
  "outputValues": {
    "successBillingScheduleIds": ["4sFDU00000000652AA", 16Pxx0000004NhAEAU]
  },
  "sortOrder": -1,
  "version": 1
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_recover_billing_schedule.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

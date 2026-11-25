---
page_id: actions-obj-blng-send-dunning-email
title: Send Dunning Email Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-blng-send-dunning-email.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_blng_send_dunning_email.htm
fetched_at: 2026-11-25
---

# Send Dunning Email Action

Run an orchestration that sends dunning process emails for collection plans to recover overdue revenue and notify customers about amounts still due.

Specify the collection plan for the dunning emails. Optionally, specify the email template by name or by ID. The action triggers an orchestration that sends dunning process emails for a collection plan based on your configured timeline.

This action is available in API version 67.0 and later.

## Special Access Rules

The Send Dunning Email action is available in Enterprise, Unlimited, and Developer Editions of Revenue Cloud.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/blngSendDunningEmail`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `collection​PlanId` | string | Required. ID of the collection plan record for dunning emails. |
| `emailTemplate​NameOrId` | string | Email template name or ID to use for the reminder email. If not specified, the default email template is used. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `isDunning​EmailSent` | boolean | Indicates whether the dunning email related to the collection plan was sent (`true`) or not (`false`). |
| `additional​Information` | string | Additional information to be passed on with the response. |

## Example

**POST**

This sample request is for the Send Dunning Email action.

```
{
  "inputs": [
    {
      "collectionPlanId": "0PLxxxxxxxxxxxxxxx",
      "emailTemplateNameOrId": "Dunning_Reminder_Template"
    }
  ]
}
```

This sample response is for the Send Dunning Email action.

```
[
  {
    "actionName": "blngSendDunningEmail",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "isDunningEmailSent": true,
      "additionalInformation": null
    },
    "sortOrder": -1,
    "version": 1
  }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-blng-send-dunning-email.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

---
page_id: actions-obj-blng-svc-inv-extend-due-date
title: Extend Invoice Due Date Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-blng-svc-inv-extend-due-date.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_blng_svc_inv_extend_due_date.htm
fetched_at: 2026-11-25
---

# Extend Invoice Due Date Action

Update the due date on an invoice to accommodate payment extensions or resolve billing disputes.

Specify the invoice ID and the revised due date to adjust the payment timeline. Use this action to extend or change the due date on an invoice.

This action is available in API version 66.0 and later.

## Special Access Rules

The Extend Invoice Due Date Action is available in Enterprise, Developer, and Unlimited Editions where Dispute Management is enabled in Billing.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/blngSvcExtendInvoiceDueDate`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `invoiceId` | string | ID of the invoice whose due date must be revised. |
| `revisedDue​DateTime` | date | Date and time that’s to be updated as the new due date on the invoice. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `additional​Information` | string | Any additional information to be included in the response. |
| `isSuccess` | boolean | Indicates whether the due date is updated on the invoice record (`true`) or not (`false`). |

## Example

**POST**

This sample request is for the Extend Invoice Due Date action.

```
{
  "inputs": [
    {
      "invoiceID": "801xx000003GYexAAG",
      "revisedDueDate": "2025-03-31"
    }
  ]
}
```

This sample response is for the Extend Invoice Due Date action.

```
[
  {
    "actionName": "blngSvcExtendInvoiceDueDate",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "isSuccess": true,
      "additionalInformation": "{\"status\":\"Due date updated successfully\"}"
    },
    "sortOrder": -1,
    "version": 1
  }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-blng-svc-inv-extend-due-date.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

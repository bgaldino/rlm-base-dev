---
page_id: actions-obj-run-unapply-credit
title: Unapply Credit Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-run-unapply-credit.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_run_unapply_credit.htm
fetched_at: 2026-11-25
---

# Unapply Credit Action

Unapply a credit memo or credit memo line from an invoice or invoice line, respectively.

This action unapplies the credit from an invoice or invoice line. This process involves crediting the applied amount of the credit memo invoice application or credit memo line invoice line record to the related credit memo or credit memo line and invoice or invoice line.

This action is available in API version 62.0 and later.

## Special Access Rules

The Apply Credit action is available in Enterprise, Developer, and Unlimited Editions where Billing is enabled. To use this action, you need the Credit Memo Operations User permission set.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/unapplyCredit`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `effectiveDate` | string | Date when the credit is unapplied from an invoice or invoice line. |
| `description` | string | Additional details about the credit memo invoice application or credit memo line invoice line record of type `Applied` that’s processed. |
| `recordId` | string | Required. ID of the credit memo invoice application or credit memo line invoice line record of type `Applied` that’s processed to unapply the credit. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `recordId` | string | ID of the credit memo invoice application or credit memo line invoice line record of type `Unapplied` that the action created. |

## Example

**POST**

This example shows a sample request for the Unapply Credit action.

```
{
  "inputs": [
    {
      "recordId": "4sFDU000000005g2AA",
      "description": "Unapplied credit memo from an invoice",
      "effectiveDate": "2024-08-27"
    }
  ]
}
```

This example shows a sample response for the Unapply Credit action.

```
  {
    "actionName": "unapplyCredit",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outputValues": {
      "recordId": "4sFDU00000000602AA"
    },
    "sortOrder": -1,
    "version": 1
  }
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-run-unapply-credit.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

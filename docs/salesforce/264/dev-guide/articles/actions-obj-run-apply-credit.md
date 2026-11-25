---
page_id: actions-obj-run-apply-credit
title: Apply Credit Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-run-apply-credit.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_run_apply_credit.htm
fetched_at: 2026-11-25
---

# Apply Credit Action

Apply a credit memo or credit memo line to an invoice or invoice line, respectively.

This action credits the amount of the credit memo or credit memo line to the corresponding invoice or invoice line, reducing both their balances.

This action is available in API version 62.0 and later.

## Special Access Rules

The Apply Credit action is available in Enterprise, Developer, and Unlimited Editions where Billing is enabled. To use this action, you need the Credit Memo Operations User permission set.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/applyCredit`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `appliedCreditAmount` | double | Required. Credit amount applied to an invoice or invoice line. |
| `creditSourceRecordId` | string | Required. ID of the credit memo or credit memo line that’s applied to an invoice or invoice line. |
| `creditTargetRecordId` | string | Required. ID of the invoice or invoice line record that the credit is applied to. |
| `description` | string | Additional details about the credit memo or credit memo line to be applied to an invoice or invoice line. |
| `effectiveDate` | string | Date to use for applying the credit memo to an invoice or invoice line. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `recordId` | string | ID of the credit memo invoice application or credit memo line invoice line record of type `Applied` that the action created. |

## Example

**POST**

This example shows a sample request for the Apply Credit action.

```
{
  "inputs": [
    {
      "appliedCreditAmount": 20,
      "creditTargetRecordId": "3ttDU00000000iZYAQ",
      "creditSourceRecordId": "50gDU000000007NYAQ",
      "description": "Applied credit memo to an invoice",
      "effectiveDate": "2024-08-27"
    }
  ]
}
```

This example shows a sample response for the Apply Credit action.

```
{
  "actionName": "applyCredit",
  "errors": null,
  "invocationId": null,
  "isSuccess": true,
  "outputValues": {
    "recordId": "4sFDU00000000652AA"
  },
  "sortOrder": -1,
  "version": 1
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-run-apply-credit.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

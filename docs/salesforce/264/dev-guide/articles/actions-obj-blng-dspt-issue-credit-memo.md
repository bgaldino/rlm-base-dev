---
page_id: actions-obj-blng-dspt-issue-credit-memo
title: Issue Credit Memo Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-blng-dspt-issue-credit-memo.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_blng_dspt_issue_credit_memo.htm
fetched_at: 2026-11-25
---

# Issue Credit Memo Action

Issue credit memos for disputed invoices to resolve billing disputes.

Specify the credit request list to automate the creation of credit memos during the dispute resolution process. The credit request list includes the invoice ID, the total credit amount, an optional description, and a detailed list of specific invoice lines with their corresponding credit amounts.

This action is available in API version 66.0 and later.

## Special Access Rules

The Issue Credit Memo Action is available in Enterprise, Developer, and Unlimited Editions where Dispute Management is enabled in Billing.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/blngDsptIssueCreditMemo`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `creditRequest​List` | Apex-defined | List of Apex-defined creditRequestInputRepresentations objects that contains the invoice ID, credit amount, description, and a list of creditLineRequestInputRepresentations objects. The creditLineRequestInputRepresentations objects include the invoice line ID, credit line amount, and a description. See [CreditLineRequestInputRepresentations](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm) Apex class. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `creditResponse` | Apex-defined | An Apex-defined creditResponseOutputRepresentations object that contains the status and any additional information. |

## Example

**POST**

This sample request is for the Issue Credit Memo action.

```
{
  "inputs": [
    {
      "creditRequestList": [
        {
          "invoiceId": "801xx000003GYexAAG",
          "creditAmount": 100,
          "description": "Credit for disputed charges",
          "creditLineRequestInputRepresentations": [
            {
              "invoiceLineId": "801xx000003GYeyAAG",
              "creditLineAmount": 50,
              "description": "Line-level credit"
            }
          ]
        }
      ]
    }
  ]
}
```

This sample response is for the Issue Credit Memo action.

```
[
  {
    "actionName": "blngDsptIssueCreditMemo",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "creditResponse": {
        "success": true,
        "message": "Credit memo issued successfully"
      }
    },
    "sortOrder": -1,
    "version": 1
  }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-blng-dspt-issue-credit-memo.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

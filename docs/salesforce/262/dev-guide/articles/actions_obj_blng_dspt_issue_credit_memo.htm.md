---
page_id: actions_obj_blng_dspt_issue_credit_memo.htm
title: Issue Credit Memo Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_blng_dspt_issue_credit_memo.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Issue Credit Memo Action

Issue credit memos for disputed invoices to resolve billing
disputes.

Specify the credit request list to automate the creation of credit memos during the
dispute resolution process. The credit request list includes the invoice ID, the
total credit amount, an optional description, and a detailed list of specific
invoice lines with their corresponding credit amounts.

This action is available in API version 66.0 and later.

## Special Access Rules

The Issue Credit Memo Action is available in Enterprise, Developer, and Unlimited
Editions where Dispute Management is enabled in Billing.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/blngDsptIssueCreditMemo`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization:
    Bearertoken`

## Inputs

| Input | Details |
| --- | --- |
| creditRequest​List | Type  Apex-defined  Description  List of Apex-defined creditRequestInputRepresentations objects that contains the invoice ID, credit amount, description, and a list of creditLineRequestInputRepresentations objects. The creditLineRequestInputRepresentations objects include the invoice line ID, credit line amount, and a description. See [CreditLineRequestInputRepresentations](./apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm.md "HTML (New Window)") Apex class. |

## Outputs

| Output | Details |
| --- | --- |
| creditResponse | Type  Apex-defined  Description  An Apex-defined creditResponseOutputRepresentations object that contains the status and any additional information.  See [CreditResponseOutputRepresentations](./apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm.md "HTML (New Window)") Apex class. |

## Example

POST
:   This sample request is for the Issue Credit Memo action.

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
:   This sample response is for the Issue Credit Memo action.

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

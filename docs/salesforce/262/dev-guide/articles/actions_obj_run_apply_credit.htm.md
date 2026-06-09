---
page_id: actions_obj_run_apply_credit.htm
title: Apply Credit Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_run_apply_credit.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Apply Credit Action

Apply a credit memo or credit memo line to an invoice or invoice
line, respectively.

This action credits the amount of the credit memo or credit memo line to the
corresponding invoice or invoice line, reducing both their balances.

This action is available in API version 62.0 and later.

## Special Access Rules

The Apply Credit action is available in Enterprise, Developer, and Unlimited Editions
where Billing is enabled. To use this action, you need the Credit Memo Operations
User permission set.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/applyCredit`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization: Bearer
    token`

## Inputs

| Input | Details |
| --- | --- |
| appliedCreditAmount | Type  double  Description  Required.  Credit amount applied to an invoice or invoice line. |
| creditSourceRecordId | Type  string  Description  Required.  ID of the credit memo or credit memo line that’s applied to an invoice or invoice line. |
| creditTargetRecordId | Type  string  Description  Required.  ID of the invoice or invoice line record that the credit is applied to. |
| description | Type  string  Description  Additional details about the credit memo or credit memo line to be applied to an invoice or invoice line. |
| effectiveDate | Type  string  Description  Date to use for applying the credit memo to an invoice or invoice line. |

## Outputs

| Output | Details |
| --- | --- |
| recordId | Type  string  Description  ID of the credit memo invoice application or credit memo line invoice line record of type `Applied` that the action created. |

## Example

POST
:   This example shows a sample request for the Apply Credit action.

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

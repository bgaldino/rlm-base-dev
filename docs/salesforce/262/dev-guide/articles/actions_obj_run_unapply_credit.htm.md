---
page_id: actions_obj_run_unapply_credit.htm
title: Unapply Credit Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_run_unapply_credit.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Unapply Credit Action

Unapply a credit memo or credit memo line from an invoice or invoice
line, respectively.

This action unapplies the credit from an invoice or invoice line. This process
involves crediting the applied amount of the credit memo invoice application or
credit memo line invoice line record to the related credit memo or credit memo line
and invoice or invoice line.

This action is available in API version 62.0 and
later.

## Special Access Rules

The Apply Credit action is available in Enterprise, Developer, and Unlimited Editions where
Billing is enabled. To use this action, you need the Credit Memo Operations User
permission set.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/unapplyCredit`

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
| effectiveDate | Type  string  Description  Date when the credit is unapplied from an invoice or invoice line. |
| description | Type  string  Description  Additional details about the credit memo invoice application or credit memo line invoice line record of type `Applied` that’s processed. |
| recordId | Type  string  Description  Required.   ID of the credit memo invoice application or credit memo line invoice line record of type `Applied` that’s processed to unapply the credit. |

## Outputs

| Output | Details |
| --- | --- |
| recordId | Type  string  Description  ID of the credit memo invoice application or credit memo line invoice line record of type `Unapplied` that the action created. |

## Example

POST
:   This example shows a sample request for the Unapply Credit action.

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

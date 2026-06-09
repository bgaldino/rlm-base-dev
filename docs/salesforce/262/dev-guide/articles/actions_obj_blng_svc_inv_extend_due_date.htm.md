---
page_id: actions_obj_blng_svc_inv_extend_due_date.htm
title: Extend Invoice Due Date Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_blng_svc_inv_extend_due_date.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Extend Invoice Due Date Action

Update the due date on an invoice to accommodate payment extensions
or resolve billing disputes.

Specify the invoice ID and the revised due date to adjust the payment timeline. Use
this action to extend or change the due date on an invoice.

This action is available in API version 66.0 and later.

## Special Access Rules

The Extend Invoice Due Date Action is available in Enterprise, Developer, and
Unlimited Editions where Dispute Management is enabled in Billing.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/blngSvcExtendInvoiceDueDate`

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
| invoiceId | Type  string  Description  ID of the invoice whose due date must be revised. |
| revisedDue​DateTime | Type  date  Description  Date and time that’s to be updated as the new due date on the invoice. |

## Outputs

| Output | Details |
| --- | --- |
| additional​Information | Type  string  Description  Any additional information to be included in the response. |
| isSuccess | Type  boolean  Description  Indicates whether the due date is updated on the invoice record (`true`) or not (`false`). |

## Example

POST
:   This sample request is for the Extend Invoice Due Date action.

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
:   This sample response is for the Extend Invoice Due Date action.

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

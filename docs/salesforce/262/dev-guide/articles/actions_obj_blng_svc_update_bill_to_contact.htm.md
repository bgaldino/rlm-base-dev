---
page_id: actions_obj_blng_svc_update_bill_to_contact.htm
title: Update Bill To Contact Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_blng_svc_update_bill_to_contact.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Update Bill To Contact Action

Update the Bill to Contact detail on an invoice to ensure accurate
billing communication and routing.

Specify the invoice ID and the new Bill to Contact detail. Optionally, indicate
whether the new contact must be set as the default for future invoices. Use this
action to change the contact to be billed on an invoice, for example, when handling
a billing dispute.

This action is available in API version 66.0 and later.

## Special Access Rules

The Update Bill To Contact Action is available in Enterprise, Developer, and
Unlimited Editions where Dispute Management is enabled in Billing.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/blngSvcUpdateBillToContact`

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
| invoiceId | Type  string  Description  ID of the invoice whose Bill to Contact detail must be updated. |
| newBill​ToContactId | Type  string  Description  ID of the Bill to Contact record to be updated on the invoice. |
| setAs​Default | Type  boolean  Description  Indicates whether the new Bill to Contact detail must be set as default for future invoices (`true`) or not (`false`). The default value is `false`. |

## Outputs

| Output | Details |
| --- | --- |
| additional​Information | Type  string  Description  Any additional information to be included in the response. |
| isSuccess | Type  boolean  Description  Indicates whether the Bill to Contact detail is updated on the invoice record (`true`) or not (`false`). |

## Example

POST
:   This sample request is for the Update Bill To Contact action.

    ```
    {
      "inputs": [
        {
          "invoiceID": "3ttxx0000000001AAA",
          "newBillToContactid": "003xx000004XYZPAA4",
          "setAsDefault": true
        }
      ]
    }
    ```
:   This sample response is for the Update Bill To Contact action.

    ```
    [
      {
        "actionName": "blngSvcUpdateBillToContact",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "isSuccess": true,
          "additionalInformation": "{\"status\":\"Success\",\"notes\":\"Default billing contact updated.\"}"
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```

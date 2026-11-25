---
page_id: actions-obj-blng-svc-update-bill-to-contact
title: Update Bill To Contact Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-blng-svc-update-bill-to-contact.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_blng_svc_update_bill_to_contact.htm
fetched_at: 2026-11-25
---

# Update Bill To Contact Action

Update the Bill to Contact detail on an invoice to ensure accurate billing communication and routing.

Specify the invoice ID and the new Bill to Contact detail. Optionally, indicate whether the new contact must be set as the default for future invoices. Use this action to change the contact to be billed on an invoice, for example, when handling a billing dispute.

This action is available in API version 66.0 and later.

## Special Access Rules

The Update Bill To Contact Action is available in Enterprise, Developer, and Unlimited Editions where Dispute Management is enabled in Billing.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/blngSvcUpdateBillToContact`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `invoiceId` | string | ID of the invoice whose Bill to Contact detail must be updated. |
| `newBill​ToContactId` | string | ID of the Bill to Contact record to be updated on the invoice. |
| `setAs​Default` | boolean | Indicates whether the new Bill to Contact detail must be set as default for future invoices (`true`) or not (`false`). The default value is `false`. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `additional​Information` | string | Any additional information to be included in the response. |
| `isSuccess` | boolean | Indicates whether the Bill to Contact detail is updated on the invoice record (`true`) or not (`false`). |

## Example

**POST**

This sample request is for the Update Bill To Contact action.

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

This sample response is for the Update Bill To Contact action.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-blng-svc-update-bill-to-contact.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

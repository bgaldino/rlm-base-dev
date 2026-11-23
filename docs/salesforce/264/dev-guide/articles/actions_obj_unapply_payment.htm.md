---
page_id: actions_obj_unapply_payment.htm
title: Unapply Payment Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_unapply_payment.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Unapply Payment Action

Unapplies a payment that's already been applied to an invoice or invoice line by crediting the amount back to the payment and the invoice or invoice line.

If the **Apply Payments to Invoices** setting is enabled, payments can be applied to invoices, which creates the PaymentLineInvoice records of type `Applied`. If the **Apply Payments to Invoices feature** setting is disabled, payments can be applied to invoice lines, which creates the PaymentLineInvoiceLine records of type `Applied`.

When payments are unapplied, the PaymentLineInvoice or PaymentLineInvoiceLine records of type `Applied` has the associated PaymentLineInvoice or PaymentLineInvoiceLine records of type `Unapplied`.

This action is available in API version 64.0 and later.

## Special Access Rules

This action is available in Enterprise, Unlimited, and Developer Editions where Billing is enabled. To use this action, you need the Payment Ops permission set.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/unapplyPayment`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer token`

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| description | string | Additional details about the payment line invoice or payment line invoice line that's processed to unapply the payment. |
| effectiveDateTime | datetime | Date and time to use for unapplying the payment from an invoice or invoice line. |
| recordId | id | Required ID of the payment line invoice or payment line invoice line record of type `Applied` that’s processed to unapply the payment. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| recordId | id | ID of the payment line invoice or payment line invoice line record of type `Unapplied` that the action created. |
| unappliedDateTime | datetime | Date and time when the payment was unapplied. |

## Example

**POST**

This sample request is for the Unapply Payment action.

```
{
  "inputs": [
    {
      "description": "Unapply payment",
      "effectiveDateTime": "2024-08-11T07:53:15.000Z",
      "recordId": "1PLR000000000dDOAQ"
    }
  ]
}
```

This sample response is for the Unapply Payment action.

```
{
  "actionName": "unapplyPayment",
  "errors": null,
  "isSuccess": true,
  "outputValues": {
    "recordId": "1PLR000000000dDOAQ",
    "unappliedDateTime": "2024-08-11T08:09:01.000Z"
  },
  "sortOrder": -1,
  "version": 1
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_unapply_payment.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

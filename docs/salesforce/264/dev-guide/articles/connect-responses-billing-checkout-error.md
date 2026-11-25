---
page_id: connect-responses-billing-checkout-error
title: Billing Checkout Error
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-checkout-error.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: connect-responses-billing-checkout-output
legacy_page_id: connect_responses_billing_checkout_error.htm
fetched_at: 2026-11-25
---

# Billing Checkout Error

Output representation of an error that occurred during a checkout transaction.

## JSON Example

```
{
  "errorCode": "PaymentAmountMustMatchInvoiceTotal",
  "message": "The payment amount must match the invoice total for a full payment."
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​Code` | String | Error code for the checkout failure. | Small, 68.0 | 68.0 |
| `message` | String | Message that states the reason for the error, if any. | Small, 68.0 | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-checkout-error.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

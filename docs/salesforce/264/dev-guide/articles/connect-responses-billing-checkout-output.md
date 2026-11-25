---
page_id: connect-responses-billing-checkout-output
title: Billing Checkout
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-checkout-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_billing_checkout_output.htm
fetched_at: 2026-11-25
---

# Billing Checkout

Output representation of the billing checkout transaction result.

## JSON Example

```
{
  "checkoutStatus": "InProgressPayment",
  "paymentId": "0azXXXXXXXXXXXXXXX",
  "paymentMethodId": "0dpXXXXXXXXXXXXXXX",
  "asyncOperationTrackerId": "9btXXXXXXXXXXXXXXX",
  "statusURL": "/services/data/v64.0/sobjects/RevenueAsyncOperation/9btXXXXXXXXXXXXXXX",
  "invoicePreview": null,
  "errorsList": []
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `async​Operation​Tracker​Id` | String | ID of the AsyncOperationTracker record that tracks the async message queue processing of this checkout. | Small, 68.0 | 68.0 |
| `checkout​Status` | String | End-to-end status of the checkout process. | Small, 68.0 | 68.0 |
| `errors​List` | [Billing Checkout Error](./connect-responses-billing-checkout-error.md)[] | Details of the errors generated during the checkout transaction. | Big, 68.0 | 68.0 |
| `invoice​Preview` | [Invoice Preview Result](./connect-responses-invoice-preview-output.md) | Invoice Preview API response for the checkout cart. Populated only when `previewInvoice` is `true`. | Big, 68.0 | 68.0 |
| `payment​Id` | String | ID of the successful payment record. | Big, 68.0 | 68.0 |
| `payment​Method​Id` | String | ID of the newly saved payment method, if a new payment method was saved. | Big, 68.0 | 68.0 |
| `status​URL` | String | URL to poll for the status of the async checkout processing (the RevenueAsyncOperation record). | Small, 68.0 | 68.0 |

- 

**[Billing Checkout Error](./connect-responses-billing-checkout-error.md)**

Output representation of an error that occurred during a checkout transaction.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-billing-checkout-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

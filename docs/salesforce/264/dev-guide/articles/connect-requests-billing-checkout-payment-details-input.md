---
page_id: connect-requests-billing-checkout-payment-details-input
title: Billing Checkout Payment Details Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-billing-checkout-payment-details-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: connect-requests-billing-checkout-input
legacy_page_id: connect_requests_billing_checkout_payment_details_input.htm
fetched_at: 2026-11-25
---

# Billing Checkout Payment Details Input

Input representation of payment details used during checkout, referencing a saved payment method.

## JSON Example

```
{
  "idempotencyKey": "a1B2c3D4-e5F6-7890-gH1i-2j3K4l5M6n7O",
  "paymentGatewayId": "0cGxx0000004C99",
  "savedPaymentMethodId": "0cAxx0000004C98"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `idempotency​Key` | String | Unique key used to retry the checkout payment safely without creating a duplicate charge. | Optional | 68.0 |
| `payment​Gateway​Id` | String | Unique ID of the preconfigured payment gateway. | Optional | 68.0 |
| `saved​Payment​Method​Details` | [Saved Payment Method Details Input](./connect-requests-billing-checkout-saved-payment-method-details-input.md) | Details required to create a saved payment method during checkout. | Optional | 68.0 |
| `saved​Payment​Method​Id` | String | Unique ID of the saved payment method to use during checkout. | Optional | 68.0 |

- 

**[Saved Payment Method Details Input](./connect-requests-billing-checkout-saved-payment-method-details-input.md)**

Input representation of the details required to create a saved payment method during checkout.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-billing-checkout-payment-details-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

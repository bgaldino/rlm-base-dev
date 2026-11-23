---
page_id: connect_resources_payment_line_apply.htm
title: Payment Line Apply (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_payment_line_apply.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-11-23
---

# Payment Line Apply (POST)

Allocate the balance of a payment to reduce the balance of an invoice. The response includes an ID of the payment line invoice or payment line invoice line that represents the payment balance allocated against the invoice.

Use the Commerce Payments APIs to send your payment and refund details to external payment gateways for processing against a customer's bank. See [Commerce Payments resources](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/connect_resources_payments.htm "HTML (New Window)") to check the APIs for payment gateways, payment captures, and payment authorizations.

## Resource

```
/commerce/billing/payments/paymentId/actions/apply
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/billing/payments/1PLR000000000dDOAQ/actions/apply
```

## Available Version

64.0

## HTTP Methods

POST

## Path Parameter for POST

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `paymentId` | String | ID of the payment record. | Required | 64.0 |

## Request Body for POST

**JSON Example**

```
{
  "appliedToId": "3ttR000000001IkIAI",
  "amount": 10,
  "effectiveDate": "2020-08-11T07:53:15.000Z",
  "comments": "Apply payment",
  "associatedAccountId": "001R00000060AyuIAE"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `amount` | Double | Amount that's applied. The amount must be less than the invoice line and payment balance. | Required | 64.0 |
| `applied​ToId` | String | ID of the invoice line that this payment is applied to. Specify the IDs for these records. | Required | 64.0 |
| `associated​AccountId` | String | ID of the associated account. | Optional | 64.0 |
| `comments` | String | Comments that you can add to the payment line application. | Optional | 64.0 |
| `effective​Date` | String | Date from which the payment line application takes effect. | Optional | 64.0 |

Supported values:

- Invoice
- Invoice Line

## Response Body for POST

[Payment Line Apply](./connect_responses_payment_line_apply_output.htm.md "Output representation of the details of the applied payment line. The details include the ID of the payment record and date when the payment line was applied.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_payment_line_apply.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

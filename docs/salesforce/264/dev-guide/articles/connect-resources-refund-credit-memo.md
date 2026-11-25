---
page_id: connect-resources-refund-credit-memo
title: Refund Credit Memo (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-refund-credit-memo.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_refund_credit_memo.htm
fetched_at: 2026-11-25
---

# Refund Credit Memo (POST)

Initiate a refund against a credit memo.

Initiates a refund for a credit memo. Locks the credit memo, calls the Commerce Refund API, and applies the refund inline (sync) or defers the apply until the payment gateway event is received (async).

## Resource

```
/revenue/billing/refunds/unreferenced-refunds/actions/process
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/revenue/billing/refunds/unreferenced-refunds/actions/process
```

## Available Version

68.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "appliedToId": "0PMxx0000000001AAA",
  "refundAmount": 100,
  "currencyIsoCode": "USD",
  "refundReason": "Customer requested refund",
  "paymentMethodId": "08pxx0000000001AAA",
  "refundNotes": "Refund processed per case 00298475."
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `applied​To​Id` | String | ID of the credit memo that the refund is applied to. | Required | 68.0 |
| `currency​Iso​Code` | String | ISO currency code. Required when multi-currency is enabled. Must match the credit memo’s currency. | Required if multi-currency is enabled | 68.0 |
| `payment​Method​Id` | String | ID of the payment method to issue the refund. Must reference a valid, active payment method. | Required | 68.0 |
| `refund​Amount` | Double | Amount to be refunded. Must be greater than 0 and not exceed the remaining balance on the credit memo. | Required | 68.0 |
| `refund​Notes` | String | Optional notes that are stored in the comments of the refund entity. | Optional | 68.0 |
| `refund​Reason` | String | Reason for the refund. | Required | 68.0 |

## Response Body for POST

[Refund Credit Memo](./connect-responses-refund-credit-memo-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-refund-credit-memo.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

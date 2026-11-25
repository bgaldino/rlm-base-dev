---
page_id: connect-requests-refund-credit-memo-input
title: Refund Credit Memo Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-refund-credit-memo-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_refund_credit_memo_input.htm
fetched_at: 2026-11-25
---

# Refund Credit Memo Input

Input representation of the details required to initiate a refund against a credit memo.

## JSON Example

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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `applied​To​Id` | String | ID of the credit memo that the refund is applied to. | Required | 68.0 |
| `currency​Iso​Code` | String | ISO currency code. Required when multi-currency is enabled. Must match the credit memo’s currency. | Required if multi-currency is enabled | 68.0 |
| `payment​Method​Id` | String | ID of the payment method to issue the refund. Must reference a valid, active payment method. | Required | 68.0 |
| `refund​Amount` | Double | Amount to be refunded. Must be greater than 0 and not exceed the remaining balance on the credit memo. | Required | 68.0 |
| `refund​Notes` | String | Optional notes that are stored in the comments of the refund entity. | Optional | 68.0 |
| `refund​Reason` | String | Reason for the refund. | Required | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-refund-credit-memo-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

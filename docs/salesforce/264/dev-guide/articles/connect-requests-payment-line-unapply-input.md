---
page_id: connect-requests-payment-line-unapply-input
title: Payment Line Unapply Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-payment-line-unapply-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_payment_line_unapply_input.htm
fetched_at: 2026-11-25
---

# Payment Line Unapply Input

Input representation of the payment line details. This representation covers fields that you can specify to revert a payment line application to their preapplication state.

## JSON Example

```
{
  "effectiveDate": "2025-05-22T11:30:25.000Z",
  "comments": "Unapply payment"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `comments` | String | Comments that you can add when you revert a payment line application. | Optional | 64.0 |
| `effective​Date` | String | Date from when the reversal of the payment line application is in effect. | Optional | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-payment-line-unapply-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

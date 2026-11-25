---
page_id: connect-requests-credit-memo-apply-input
title: Credit Memo Apply Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-credit-memo-apply-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_credit_memo_apply_input.htm
fetched_at: 2026-11-25
---

# Credit Memo Apply Input

Input representation of the request to apply a credit memo to an invoice.

## JSON Example

```
{
  "applications": [
    {
      "appliedToId": "3ttxx000000003FAAQ",
      "amount": 10,
      "description": "Apply to invoice for refund",
      "effectiveDate": "2024-07-01"
    },
    {
      "appliedToId": "3ttxx0000000001AAA",
      "amount": 100
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `applications` | [Credit Memo Apply Application Input](./connect-requests-credit-memo-apply-application-input.md)[] | List of one or more applications to apply the credit memo for. Each application represents an invoice that’s credited by using the balance of the specified credit memo. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-credit-memo-apply-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

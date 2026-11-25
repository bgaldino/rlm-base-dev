---
page_id: connect-responses-refund-credit-memo-output
title: Refund Credit Memo
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-refund-credit-memo-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_refund_credit_memo_output.htm
fetched_at: 2026-11-25
---

# Refund Credit Memo

Output representation for the process refund against a credit memo API.

## JSON Example

```
{
  "applications": [
    {
      "applicationId": "0CMxx0000000001AAA",
      "appliedToId": "0PMxx0000000001AAA"
    }
  ],
  "errors": [],
  "refundId": "0Rfxx0000000001AAA",
  "success": true
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `applications` | [Refund Application](./connect-responses-refund-application-output.md)[] | Application records created by the refund. One `CreditMemoRefund` record for a top-level credit memo, or one `CreditMemoLineRefund` record per applied line for a line-level credit memo. | Big, 68.0 | 68.0 |
| `errors` | [Refund Error](./connect-responses-refund-error-output.md)[] | Details of the errors if the API request was unsuccessful. | Big, 68.0 | 68.0 |
| `refund​Id` | String | ID of the created record. | Big, 68.0 | 68.0 |
| `success` | Boolean | Indicates whether the refund was successfully initiated (`true`) or not (`false`). | Big, 68.0 | 68.0 |

- 

**[Refund Application](./connect-responses-refund-application-output.md)**

Output representation of a single refund application record created by the refund against a credit memo API.

- 

**[Refund Error](./connect-responses-refund-error-output.md)**

Output representation of an error that occurred during a refund against a credit memo.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-refund-credit-memo-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

---
page_id: connect_responses_refund_credit_memo_output.htm
title: Refund Credit Memo
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_refund_credit_memo_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
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
| `applications` | [Refund Application](./connect_responses_refund_application_output.htm.md "Output representation of a single refund application record created by the refund against a credit memo API.")[] | Application records created by the refund. One `CreditMemoRefund` record for a top-level credit memo, or one `CreditMemoLineRefund` record per applied line for a line-level credit memo. | Big, 68.0 | 68.0 |
| `errors` | [Refund Error](./connect_responses_refund_error_output.htm.md "Output representation of an error that occurred during a refund against a credit memo.")[] | Details of the errors if the API request was unsuccessful. | Big, 68.0 | 68.0 |
| `refund​Id` | String | ID of the created record. | Big, 68.0 | 68.0 |
| `success` | Boolean | Indicates whether the refund was successfully initiated (`true`) or not (`false`). | Big, 68.0 | 68.0 |

- **[Refund Application](./connect_responses_refund_application_output.htm.md)**  
  Output representation of a single refund application record created by the refund against a credit memo API.
- **[Refund Error](./connect_responses_refund_error_output.htm.md)**  
  Output representation of an error that occurred during a refund against a credit memo.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_refund_credit_memo_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

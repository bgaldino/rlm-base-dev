---
page_id: connect_responses_void_posted_credit_memo_output.htm
title: Void Posted Credit Memo
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_void_posted_credit_memo_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Void Posted Credit Memo

Output representation of the request to void a posted credit memo.

## JSON Example

This example shows a sample success response.

```
{
  "errors": null,
  "statusURL": "/services/data/v68.0/sobjects/AsyncOperationTracker/16Pxx0000004LdkEAE",
  "debitMemoId": "4Dmxx00000000XtAAK",
  "success": true
}
```

This example shows a sample error response.

```
{
  "errors": [
    {
      "errorCode": "INVALID_STATUS",
      "message": "CreditMemo 50gxx00000000XtAAI is not in the Posted status."
    }
  ],
  "debitMemoId": "",
  "success": false
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `debitMemoId` | String | ID of the created debit memo. | Big, 66.0 | 66.0 |
| `errors` | [Error Response](./connect_responses_error_response.htm.md "Output representation of the error details encountered during the API request.")[] | List of errors specific to this API request that were encountered during voiding the credit memo. | Big, 66.0 | 66.0 |
| `isSuccess` | Boolean | Indicates whether the API request was successful (`true`) or not (`false`). | Big, 66.0 | 66.0 |
| `statusURL` | String | Status URL for tracking this operation. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_void_posted_credit_memo_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

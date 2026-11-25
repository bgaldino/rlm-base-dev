---
page_id: connect-responses-clone-sales-transaction-error-response
title: Clone Sales Transaction Error Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-clone-sales-transaction-error-response.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_clone_sales_transaction_error_response.htm
fetched_at: 2026-11-25
---

# Clone Sales Transaction Error Response

Output representation of the errors that occur during the clone sales transaction operation.

## JSON Example

```
{
  "errors": [
    {
      "errorCode": "INVALID_API_INPUT",
      "message": "Specify only one record",
      "referenceId": "0QLxx0000004CBYGA2"
    }
  ]
}
```

## Properties

| Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errorCode` | String | Code associated with the error. | 64.0 |
| `message` | String | Message associated with the error. | 64.0 |
| `referenceId` | String | Reference ID associated with the error. | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-clone-sales-transaction-error-response.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

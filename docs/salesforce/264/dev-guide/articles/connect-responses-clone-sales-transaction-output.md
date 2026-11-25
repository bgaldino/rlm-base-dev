---
page_id: connect-responses-clone-sales-transaction-output
title: Clone Sales Transaction
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-clone-sales-transaction-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_clone_sales_transaction_output.htm
fetched_at: 2026-11-25
---

# Clone Sales Transaction

Output representation for the result of cloning records within a sales transaction.

## JSON Example

This example shows a sample of a successful response.

```
{
    "requestId": "9356bcbf04f06e22360a09807c13e1d4e395",
    "salesTransactionId": "0Q0SG000000ACxf0AG",
    "errors": [],
    "success": true
}
```

This example shows a sample error response.

```
{
    "requestId": "9356bcbf04f06e22360a09807c13e1d4e395",
    "salesTransactionId": "0Q0SG000000ACxf0AG",
    "errors": [
        {
            "errorCode": "INVALID_API_INPUT",
            "message": "Specify only one record",
            "referenceId": "0QLxx0000004CBYGA2"
        }
    ],
    "success": false
}
```

## Properties

| Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `requestId` | String | Request ID of the process that can be used to query the async status. | 64.0 |
| `salesTransactionId` | String | ID of the quote line item, order item, quote line group, or order item group record. | 64.0 |
| `success` | Boolean | Indicates whether the synchronous part of the processing is successful (`true`) or not (`false`). | 64.0 |
| `errors` | [Clone Sales Transaction Error Response](./connect-responses-clone-sales-transaction-error-response.md)[] | List of errors encountered during synchronous processing. | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-clone-sales-transaction-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

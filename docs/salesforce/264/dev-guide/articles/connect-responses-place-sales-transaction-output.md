---
page_id: connect-responses-place-sales-transaction-output
title: Sales Transaction
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-place-sales-transaction-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_place_sales_transaction_output.htm
fetched_at: 2026-11-25
---

# Sales Transaction

Output representation of the request to create a sales transaction.

## JSON Example

```
{
  "contextDetails": {
    "contextId": "e055bb18-d4e8-41c3-881e-0132b9561708",
    "isBuiltInTransaction": true
  },
  "errorResponse": {
    "errorCode": "INVALID_API_INPUT",
    "message": "Include record type and method in the request and try again.",
    "referenceId": "refQuoteItem2"
  },
  "isSuccess": true,
  "salesTransactionId": "0Q0xx0000004CNYCA2",
  "statusUrl": null,
  "trackerId": null
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDetails` | [Sales Transaction Context](./connect-responses-sales-transaction-context-output.md) | Details of the context that’s created for the sales transaction. | Small, 63.0 | 63.0 |
| `errorResponse` | [Sales Transaction Error Response](./connect-responses-place-sales-transaction-error-response.md)[] | Details of the error if the operation fails. | Small, 63.0 | 63.0 |
| `isSuccess` | Boolean | Indicates if the operation is successful (`true`) or not (`false`). | Small, 63.0 | 63.0 |
| `salesTransactionId` | String | ID of the sales transaction, such as a quote or an order. | Small, 63.0 | 63.0 |
| `statusUrl` | String | URL to check the status of the operation. | Small, 63.0 | 63.0 |
| `trackerId` | String | Unique identifier assigned to a specific operation or request that’s used for tracking and referencing the operation. | Small, 63.0 | 63.0 |

The **Calculation Status** field for a quote or an order shows an intermediate status as `Saving` during the creation of a sales transaction. If the pricing calculation fails, then the **Calculation Status** field shows the `Pricing Calculation Failed` status. See [Quote standard object](https://developer.salesforce.com/docs/atlas.en-us.254.0.object_reference.meta/object_reference/sforce_api_objects_quote.htm) for a list of applicable calculation status values.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-place-sales-transaction-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

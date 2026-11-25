---
page_id: connect-responses-sales-transaction-context-output
title: Sales Transaction Context
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-sales-transaction-context-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_sales_transaction_context_output.htm
fetched_at: 2026-11-25
---

# Sales Transaction Context

Output representation of the context details that are associated with a sales transaction.

## JSON Example

```
{
  "contextDetails": {
    "contextId": "e055bb18-d4e8-41c3-881e-0132b9561708",
    "isBuiltInTransaction": true
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | ID of the context that’s created for a session of the sales transaction. | Small, 63.0 | 63.0 |
| `isBuiltIn​Transaction` | Boolean | Indicates whether a new context ID is created for the sales transaction ( `true` ) or not ( `false` ). If the `contextId` property isn’t specified, the Place Sales Transaction API generates it. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-sales-transaction-context-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

---
page_id: connect-requests-unlock-transaction-input
title: Unlock Transaction Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-unlock-transaction-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_unlock_transaction_input.htm
fetched_at: 2026-11-25
---

# Unlock Transaction Input

Input representation of the details of the request to unlock a sales transaction.

## JSON Example

This example shows a sample request to unlock a stuck sales transaction calculation.

```
{
  "salesTransactionIds": ["0Q0xx0000004CIiCAM"]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sales​Transaction​Ids` | String[] | List of record IDs, such as a quote or an order, whose calculation status is unlocked. This release supports only one record ID. | Required | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-unlock-transaction-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

---
page_id: connect_requests_unlock_transaction_input.htm
title: Unlock Transaction Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_unlock_transaction_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-11-23
---

# Unlock Transaction Input

Input representation of the details of the request to unlock a sales
transaction.

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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_unlock_transaction_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

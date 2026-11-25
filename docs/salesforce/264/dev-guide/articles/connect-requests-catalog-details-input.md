---
page_id: connect-requests-catalog-details-input
title: Catalog Details Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-catalog-details-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-api-requests
legacy_page_id: connect_requests_catalog_details_input.htm
fetched_at: 2026-11-25
---

# Catalog Details Input

Input representation of the request to get the catalog details.

## JSON Example

```
{
  "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
  "userContext": {
     "accountId": "001xx0000000001AAA",
     "contactId": "003xx00000000D7AAI"
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique identifier value that’s attached to the requests and messages, and accepts references to a particular transaction or event chain. | Optional | 60.0 |
| `user​Context` | [User Context Input](./connect-requests-user-context-input.md) | User context details. For example, account ID or contact ID. | Optional | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-catalog-details-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

---
page_id: connect-responses-status
title: Status
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-status.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_status.htm
fetched_at: 2026-11-25
---

# Status

Output representation of the status of the request.

## JSON Example

```
"status": {
    "code": "200",
    "errors": [],
    "message": "Successfully fetched the catalog records."
  }
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Code of the error message. | Small, 60.0 | 60.0 |
| `errors` | [Error](./connect-responses-epc-error-output.md)[] | Details of the error. | Small, 60.0 | 60.0 |
| `message` | String | Error message. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-status.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

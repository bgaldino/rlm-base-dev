---
page_id: connect-responses-p-c-m-error-output
title: Product Catalog Management Error
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-p-c-m-error-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_p_c_m_error_output.htm
fetched_at: 2026-11-25
---

# Product Catalog Management Error

Output representation that contains error details, including error codes and messages.

## JSON Example

```
{
  "errorCode": "INSUFFICIENT_ACCESS",
  "message": "Insufficient access rights on cross-reference ID"
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Error code that identifies the type of error. | Small, 66.0 | 66.0 |
| `message` | String | Message that explains the reason for the error. | Small, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-p-c-m-error-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

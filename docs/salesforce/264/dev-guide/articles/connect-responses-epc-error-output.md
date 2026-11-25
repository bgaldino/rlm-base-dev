---
page_id: connect-responses-epc-error-output
title: Error Output
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-epc-error-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_epc_error_output.htm
fetched_at: 2026-11-25
---

# Error Output

Output representation of the error details.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​Code` | String | Code of the error message. | Small, 60.0 | 60.0 |
| `message​Detail` | String | Details of the error message. | Small, 60.0 | 60.0 |
| `message​Title` | String | Title of the error message. | Small, 60.0 | 60.0 |
| `node​ProductId` | String | ID of the product node. | Small, 61.0 | 61.0 |
| `record​Id` | String | ID of the record. | Small, 60.0 | 60.0 |
| `record​Name` | String | Name of the record. | Small, 60.0 | 60.0 |
| `related​ObjectNodes` | [Invalid Related Object Node](./connect-responses-invalid-related-object-node-output.md)[] | List of related object nodes with errors. | Small, 62.0 | 62.0 |
| `source` | String | Name of the API that’s the source of the error. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-epc-error-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

---
page_id: connect-responses-index-error-output
title: Index Error
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-index-error-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_index_error_output.htm
fetched_at: 2026-11-25
---

# Index Error

Output representation of the error details related to an index.

## JSON Example

```
  "indexErrorDetails": {
    "errorFileId": "069xx0000004C92AAE",
    "indexCreatedDate": "2024-10-03T05:24:18.000Z",
    "indexErrorsCount": 1,
    "indexLastUpdatedDate": "2024-10-03T05:27:00.000Z",
    "itemLevelErrorsCount": 1
  }
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​FileId` | String | ID of the exported error file that contains the index errors. | Small, 63.0 | 63.0 |
| `indexCreated​Date` | String | Date on which the index was created. | Small, 63.0 | 63.0 |
| `index​ErrorsCount` | Integer | Number of index-level errors. | Small, 63.0 | 63.0 |
| `indexLast​UpdatedDate` | String | Date on which the index was last updated. | Small, 63.0 | 63.0 |
| `itemLevel​ErrorsCount` | Integer | Number of item-level errors. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-index-error-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

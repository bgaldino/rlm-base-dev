---
page_id: connect_responses_snapshot_index_error_output.htm
title: Snapshot Index Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_snapshot_index_error_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-11-23
---

# Snapshot Index Error

Output representation of the error details related to a snapshot index.

## JSON Example

```
{
  "errors": [],
  "indexErrorDetails": {
    "errorFileId": "069xx0000004C92AAE",
    "indexCreatedDate": "2024-10-03T05:24:18.000Z",
    "indexErrorsCount": 1,
    "indexLastUpdatedDate": "2024-10-03T05:27:00.000Z",
    "itemLevelErrorsCount": 1
  },
  "statusCode": "200"
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Output](./connect_responses_epc_error_output.htm.md "Output representation of the error details.")[] | List of errors encountered during the processing of the API request. | Small, 63.0 | 63.0 |
| `indexError​Details` | [Index Error](./connect_responses_index_error_output.htm.md "Output representation of the error details related to an index.")[] | Count and details of errors that occurred during indexing. | Small, 63.0 | 63.0 |
| `status​Code` | String | Code that indicates the status of the API request. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_snapshot_index_error_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

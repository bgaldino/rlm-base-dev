---
page_id: connect_resources_get_index_errors.htm
title: Snapshot Index Error (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_index_errors.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-11-23
---

# Snapshot Index Error (GET)

Get the count and details of the errors that occurred during the indexing process.

**Resource**

```
/connect/pcm/index/error
```

**Resource Example**

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/error
```

**Available Version:** 63.0

**HTTP Methods:** GET

**Request Parameters for GET**

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `indexId` | String | ID of the index. | Required | 63.0 |
| `snapshot​IndexId` | String | ID of the snapshot index. | Required | 63.0 |

**Response Body for GET:** [Snapshot Index Error](./connect_responses_snapshot_index_error_output.htm.md "Output representation of the error details related to a snapshot index.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_index_errors.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

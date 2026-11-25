---
page_id: connect-resources-get-index-errors
title: Snapshot Index Error (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-index-errors.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-resources
legacy_page_id: connect_resources_get_index_errors.htm
fetched_at: 2026-11-25
---

# Snapshot Index Error (GET)

Get the count and details of the errors that occurred during the indexing process.

**Resource**

```
/connect/pcm/index/error
```

**Resource Example**

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/pcm/index/error
```

**Available Version:** 63.0

**HTTP Methods:** GET

**Request Parameters for GET**

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `indexId` | String | ID of the index. | Required | 63.0 |
| `snapshot​IndexId` | String | ID of the snapshot index. | Required | 63.0 |

**Response Body for GET:** [Snapshot Index Error](./connect-responses-snapshot-index-error-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-index-errors.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

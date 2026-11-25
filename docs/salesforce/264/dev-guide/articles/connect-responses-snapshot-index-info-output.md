---
page_id: connect-responses-snapshot-index-info-output
title: Snapshot Index Info
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-snapshot-index-info-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_snapshot_index_info_output.htm
fetched_at: 2026-11-25
---

# Snapshot Index Info

Output representation of the details of a snapshot index.

## JSON Example

```
 "indexInfos": [
            {
              "buildType": "FULL",
              "id": "0axxx00000000T3AAI",
              "isIncrementable": true,
              "usageType": "LIVE"
            }
          ]
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `buildType` | String | Build type of the index. Valid values are `FULL`—Specifies a full index build or `INCREMENTAL`—Specifies an incremental index build. Available in API version 63.0 and later. | Small, 63.0 | 63.0 |
| `id` | String | ID of the index information record. | Small, 63.0 | 63.0 |
| `isIncrementable` | Boolean | Indicates whether a partial build is enabled (`true`) or disabled (`false`). | Small, 63.0 | 63.0 |
| `usageType` | String | Usage type of the index. Valid values are `LIVE`—Index usage type is live or `OUT_OF_USE`—Index usage type is out of use. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-snapshot-index-info-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

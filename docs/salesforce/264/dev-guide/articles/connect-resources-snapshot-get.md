---
page_id: connect-resources-snapshot-get
title: Snapshot Collection (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-snapshot-get.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-resources
legacy_page_id: connect_resources_snapshot_get.htm
fetched_at: 2026-11-25
---

# Snapshot Collection (GET)

Retrieve the created snapshots and snapshot indexes.

**Resource**

```
/connect/pcm/index/snapshots
```

**Resource Example**

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/pcm/index/snapshots
```

**Available Version:** 62.0

**HTTP Methods:** GET

**Query Parameter for GET**

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `numberOf​IndexLogs` | Integer | Number of index logs to include in the response. Specify a number from 0 through 100. The default value is 25. | Optional | 63.0 |

**Response Body for GET:** [Snapshot Collection](./connect-responses-snapshot-collection-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-snapshot-get.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

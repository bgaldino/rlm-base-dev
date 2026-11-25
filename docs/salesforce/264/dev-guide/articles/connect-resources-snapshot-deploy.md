---
page_id: connect-resources-snapshot-deploy
title: Snapshot Deployment (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-snapshot-deploy.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-resources
legacy_page_id: connect_resources_snapshot_deploy.htm
fetched_at: 2026-11-25
---

# Snapshot Deployment (POST)

Create indexes for a snapshot. Indexes improve search results and make it easier to find products at run time through search terms.

**Resource**

```
/connect/pcm/index/deploy
```

**Resource Example**

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/pcm/index/deploy
```

**Available Version:** 62.0

**HTTP Methods:** POST

**Request Body for POST**

**JSON Example**

This example shows a sample request to build a new snapshot with immediate activation.

```
{
  "snapshot": {
    "activationType": "IMMEDIATE"
  },
  "buildType": "FULL"
}
```

This example shows a sample request to rebuild a snapshot in the `active` status.

```
{
  "snapshot": {
    "activationType": "IMMEDIATE",
    "id": "1Avxx0000005DFe1AM"
  },
  "buildType": "FULL"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `buildType` | String | Build type of the snapshot index. Valid value is `FULL`—Specifies a full index build or `INCREMENTAL`—Specifies an incremental index build. Available from API version 63.0 and later. | Required | 62.0 |
| `snapshot` | [Run-time Catalog Snapshot Input](./connect-requests-runtime-catalog-snapshot-input.md)[] | Snapshot to deploy. | Required | 62.0 |

**Response Body for POST:** [Snapshot Deployment](./connect-responses-snapshot-deployment-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-snapshot-deploy.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

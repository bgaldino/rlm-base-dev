---
page_id: connect-requests-snapshot-deployment-input
title: Snapshot Deployment Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-snapshot-deployment-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-requests
legacy_page_id: connect_requests_snapshot_deployment_input.htm
fetched_at: 2026-11-25
---

# Snapshot Deployment Input

Input representation of the request to deploy a run-time catalog snapshot.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-snapshot-deployment-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

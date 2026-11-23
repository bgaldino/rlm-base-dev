---
page_id: connect_requests_runtime_catalog_snapshot_input.htm
title: Run-time Catalog Snapshot Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_runtime_catalog_snapshot_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-11-23
---

# Run-time Catalog Snapshot Input

Input representation of the details of a run-time catalog snapshot for deployment.

**JSON Example**

```
  "snapshot": {
    "activationType": "IMMEDIATE",
    "activationDate": "2024-05-06T05:12:59.000Z",
    "id": "1Avxx0000005DFe1AM"
  }
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `activationDate` | String | Activation date of the snapshot. | Optional | 62.0 |
| `activationType` | String | Activation type of the snapshot. Valid value is `IMMEDIATE`—Snapshot is activated immediately after a successful build. | Required | 62.0 |
| `id` | String | ID of the snapshot. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_runtime_catalog_snapshot_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

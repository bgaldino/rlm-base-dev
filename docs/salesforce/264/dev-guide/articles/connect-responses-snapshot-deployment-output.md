---
page_id: connect-responses-snapshot-deployment-output
title: Snapshot Deployment
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-snapshot-deployment-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_snapshot_deployment_output.htm
fetched_at: 2026-11-25
---

# Snapshot Deployment

Output representation of the snapshot deployment.

## JSON Example

This example shows a sample response to the request to build a new snapshot with immediate activation.

```
{
  "errors": [],
  "snapshot": {
    "activationStatus": "NONE",
    "activationType": "IMMEDIATE",
    "id": "1Avxx0000004CFU",
    "snapshotIndexes": [
      {
        "createdDate": "2024-07-24T21:10:48.000Z",
        "id": "1D6xx0000004CFU",
        "indexBuildType": "FULL",
        "indexType": "PRODUCT",
        "lastBuildStatus": "IN_PROGRESS"
      }
    ]
  },
  "statusCode": "200"
}
```

This example shows a sample response of the request to rebuild a snapshot in the `active` status.

```
{
  "errors": [],
  "snapshot": {
    "activationStatus": "NONE",
    "activationType": "IMMEDIATE",
    "id": "1Avxx0000004CH6",
    "snapshotIndexes": [
      {
        "createdDate": "2024-07-24T21:13:05.000Z",
        "id": "1D6xx0000004CH6",
        "indexBuildType": "FULL",
        "indexType": "PRODUCT",
        "lastBuildStatus": "IN_PROGRESS"
      }
    ]
  },
  "statusCode": "200"
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Output](./connect-responses-epc-error-output.md)[] | List of errors, if any. | Small, 62.0 | 62.0 |
| `snapshot` | [Snapshot](./connect-responses-snapshot-output.md)[] | Run-time catalog snapshot associated with the created index. | Small, 62.0 | 62.0 |
| `statusCode` | String | Code indicating the status of the request. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-snapshot-deployment-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

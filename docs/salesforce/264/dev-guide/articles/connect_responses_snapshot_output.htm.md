---
page_id: connect_responses_snapshot_output.htm
title: Snapshot
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_snapshot_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-11-23
---

# Snapshot

Output representation of the list of active snapshots.

## JSON Example

```
  "snapshots": [
    {
      "activationDate": "2024-11-06T06:58:02.000Z",
      "activationStatus": "ACTIVE",
      "activationType": "IMMEDIATE",
      "id": "1Avxx0000004C92CAE",
      "snapshotIndexes": [
        {
          "createdDate": "2024-11-06T06:56:49.000Z",
          "id": "1D6xx0000004C92CAE",
          "indexBuildType": "FULL",
          "indexInfos": [
            {
              "buildType": "FULL",
              "id": "0axxx00000000T3AAI",
              "isIncrementable": true,
              "usageType": "LIVE"
            }
          ],
          "indexLogs": [
            {
              "catalogSnapshotTime": "2024-11-06T16:14:30.000Z",
              "completionTime": "2024-11-06T16:16:02.000Z",
              "createdById": "005xx000001X7x7AAC",
              "indexBuildStatus": "COMPLETED",
              "indexBuildType": "FULL",
              "indexId": "0axxx00000000T3AAI",
              "numberOfChanges": 7
            },
            {
              "catalogSnapshotTime": "2024-11-06T15:03:32.000Z",
              "completionTime": "2024-11-06T15:05:02.000Z",
              "createdById": "005xx000001X7x7AAC",
              "indexBuildStatus": "COMPLETED_WITH_ERRORS",
              "indexBuildType": "INCREMENTAL",
              "indexId": "0axxx00000000RRAAY",
              "message": "Warning: Product errors found.",
              "numberOfChanges": 3
            },
            {
              "catalogSnapshotTime": "2024-11-06T12:35:34.000Z",
              "completionTime": "2024-11-06T12:35:34.000Z",
              "createdById": "005xx000001X7x7AAC",
              "indexBuildStatus": "COMPLETED",
              "indexBuildType": "INCREMENTAL",
              "indexId": "0axxx00000000RRAAY",
              "message": "There are no changes for the partial update.",
              "numberOfChanges": 0
            },
            {
              "catalogSnapshotTime": "2024-11-06T12:07:32.000Z",
              "completionTime": "2024-11-06T12:09:02.000Z",
              "createdById": "005xx000001X7x7AAC",
              "indexBuildStatus": "COMPLETED_WITH_ERRORS",
              "indexBuildType": "FULL",
              "message": "Warning: Product errors found.",
              "numberOfChanges": 1
            }
          ],
          "indexType": "PRODUCT",
          "lastBuildStatus": "IN_PROGRESS",
          "venueId": "1D6xx0000004C92CAE"
        }
      ]
    }
  ]
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `activation​Date` | String | Activation date of the snapshot. | Small, 62.0 | 62.0 |
| `activation​Status` | String | Activation status of the snapshot. Valid values are `NONE`, `ACTIVE`—Snapshot is in active status, or `EXPIRED`—Snapshot is in expired status. | Small, 62.0 | 62.0 |
| `activation​Type` | String | Activation type of the snapshot. Valid values are `IMMEDIATE`—Snapshot is activated immediately after a successful build. | Small, 62.0 | 62.0 |
| `id` | String | ID of the snapshot. | Small, 61.0 | 61.0 |
| `snapshot​Indexes` | [Snapshot Index](./connect_responses_snapshot_index_output.htm.md "Output representation of the snapshot index of a run-time catalog.")[] | List of indexes created in the snapshot. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_snapshot_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.

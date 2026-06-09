---
page_id: connect_responses_snapshot_index_output.htm
title: Snapshot Index
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_snapshot_index_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Snapshot Index

Output representation of the snapshot index of a run-time catalog.

JSON example
:   ```
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
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `completed​Date` | String | Completed date of the snapshot index. | Small, 62.0 | 62.0 |
| `created​Date` | String | Created date of the snapshot index. | Small, 62.0 | 62.0 |
| `id` | String | ID of the snapshot index. | Small, 62.0 | 62.0 |
| `indexBuild​Type` | String | Build type of the snapshot index. Valid value is:  - `FULL`—Specifies a full index   build. - `INCREMENTAL`—Specifies an   incremental index build. Available in API version 63.0 and later. | Small, 62.0 | 62.0 |
| `indexInfos` | [Index Info](./connect_responses_snapshot_index_info_output.htm.md "Output representation of the details of a snapshot index.") | Index information records associated with the snapshot index. | Small, 63.0 | 63.0 |
| `indexLogs` | [Index Logs](./connect_responses_snapshot_index_log_output.htm.md "Output representation of a snapshot index log.")[] | Index logs associated with the snapshot index. | Small, 63.0 | 63.0 |
| `indexType` | String | Index type of the snapshot index. Valid value is:  - `PRODUCT`—Snapshot index is of   product type. | Small, 62.0 | 62.0 |
| `lastBuild​Status` | String | Last build status of the snapshot index. Valid values are:  - `IN_PROGRESS`—Snapshot index build   is in progress. - `FAILED`—Snapshot index build   failed. - `COMPLETED`—Snapshot index build   completed successfully. | Small, 62.0 | 62.0 |
| `numberOf​Records` | Integer | Number of indexed records. | Small, 62.0 | 62.0 |
| `venueId` | String | Venue ID of the snapshot index. | Small, 63.0 | 63.0 |

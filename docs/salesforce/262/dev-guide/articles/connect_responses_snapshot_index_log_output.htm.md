---
page_id: connect_responses_snapshot_index_log_output.htm
title: Snapshot Index Log
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_snapshot_index_log_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Snapshot Index Log

Output representation of a snapshot index log.

JSON example
:   ```
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
              ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `catalog​SnapshotTime` | String | Catalog snapshot time of the index. | Small, 63.0 | 63.0 |
| `completion​Time` | String | Completion time of the index. | Small, 63.0 | 63.0 |
| `createdBy​Id` | String | ID of the user that initiated the index build. | Small, 63.0 | 63.0 |
| `indexBuild​Status` | String | Status of the index build. | Small, 63.0 | 63.0 |
| `indexBuild​Type` | String | Type of the index build. Valid values are:   - `FULL`—Specifies a full index   build. - `INCREMENTAL`—Specifies an   incremental index build. Available in API version 63.0 and later. | Small, 63.0 | 63.0 |
| `index​Id` | String | ID of the index. | Small, 63.0 | 63.0 |
| `message` | String | Message for the index status. | Small, 63.0 | 63.0 |
| `numberOf​Changes` | Integer | Number of new or changed products included in the index. | Small, 63.0 | 63.0 |

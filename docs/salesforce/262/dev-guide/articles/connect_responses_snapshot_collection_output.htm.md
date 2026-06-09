---
page_id: connect_responses_snapshot_collection_output.htm
title: Snapshot Collection
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_snapshot_collection_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Snapshot Collection

Output representation of the retrieved snapshot collection.

JSON example
:   ```
    {
      "errors": [],
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
      ],
      "statusCode": "200"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Output](./connect_responses_epc_error_output.htm.md "Output representation of the error details.")[] | List of errors, if any. | Small, 62.0 | 62.0 |
| `snapshots` | [Snapshot](./connect_responses_snapshot_output.htm.md "Output representation of the list of active snapshots.")[] | List of active snapshots. | Small, 62.0 | 62.0 |
| `statusCode` | String | Code indicating the status of the request. | Small, 62.0 | 62.0 |

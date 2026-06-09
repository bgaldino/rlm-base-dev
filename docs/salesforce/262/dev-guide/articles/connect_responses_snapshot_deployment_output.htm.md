---
page_id: connect_responses_snapshot_deployment_output.htm
title: Snapshot Deployment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_snapshot_deployment_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Snapshot Deployment

Output representation of the snapshot deployment.

JSON example
:   This example shows a sample response to the request to build a new snapshot with
    immediate activation.
:   ```
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
:   This example shows a sample response of the request to rebuild a snapshot in the
    `active` status.
:   ```
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

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Output](./connect_responses_epc_error_output.htm.md "Output representation of the error details.")[] | List of errors, if any. | Small, 62.0 | 62.0 |
| `snapshot` | [Snapshot](./connect_responses_snapshot_output.htm.md "Output representation of the list of active snapshots.")[] | Run-time catalog snapshot associated with the created index. | Small, 62.0 | 62.0 |
| `statusCode` | String | Code indicating the status of the request. | Small, 62.0 | 62.0 |
